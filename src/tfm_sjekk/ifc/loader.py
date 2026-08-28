"""Leser én IFC-fil og trekker ut TFM-verdiene fra egenskapssettene."""

from __future__ import annotations

import os
from codecs import BOM_UTF8
from collections import defaultdict
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.feil import FilFeil
from tfm_sjekk.modell import IfcObjekt, Kilde, Krets, Verdikilde
from tfm_sjekk.parser import ligner_komponenttype, ligner_tfm_id, mmi_niva

# ISO 10303-21 krever begge. Starten sier at dette er en SPF-fil i det hele
# tatt; slutten sier at skrivingen kom i mål.
START = b"ISO-10303-21;"
SLUTT = b"END-ISO-10303-21;"

# Nok til å fange begge markørene med god margin, uten å lese en fil på 200 MB
# for å svare på et spørsmål som gjelder de ytterste bytene.
KIKKHULL = 64


def _kikk(sti: Path) -> tuple[bytes, bytes]:
    """Første og siste bytene i fila."""
    with sti.open("rb") as f:
        forste = f.read(KIKKHULL)
        f.seek(0, os.SEEK_END)
        storrelse = f.tell()
        f.seek(max(0, storrelse - KIKKHULL))
        return forste, f.read(KIKKHULL)


def _apne(sti: Path):
    """Åpner fila, eller sier hvorfor den ikke lot seg åpne.

    Rekkefølgen er meningen. «Er dette IFC i det hele tatt» må spørres før «er
    den hel»: en tekstfil som ikke er IFC mangler også avslutningen, og å melde
    den som avkuttet ville sendt brukeren til å eksportere på nytt framfor til å
    se på hvilken fil de plukket.
    """
    try:
        forste, siste = _kikk(sti)
    except OSError as feil:
        raise FilFeil(sti, f"kunne ikke åpnes: {feil.strerror or feil}.") from feil

    if not forste:
        raise FilFeil(
            sti,
            "er tom (0 byte). En fil på null byte er som regel en skriving som "
            "aldri kom i gang — finn eksporten igjen.",
        )

    # startswith, ikke «in». Et zip-arkiv som inneholder en IFC bærer teksten
    # «ISO-10303-21;» inne i seg, og en substrengsjekk meldte derfor en
    # .ifcZIP som avkuttet — altså «eksporter på nytt» framfor «se på hvilken
    # fil du plukket». BOM og innledende blanke tegn tas av først; noen
    # eksportører legger på en BOM, og da STÅR headeren der — den har bare tre
    # byte foran seg. Fila er ikke gyldig for det: ifcopenshell avviser en BOM,
    # og sier det selv. Poenget med å ta den av er å ikke gi feil svar på feil
    # spørsmål — «begynner ikke med ISO-10303-21;» ville vært usant her.
    hode = forste.removeprefix(BOM_UTF8).lstrip()
    if not hode.startswith(START):
        hint = (
            " Fila ser ut som et zip-arkiv — er dette en .ifcZIP som har fått endelsen .ifc?"
            if forste.startswith(b"PK")
            else ""
        )
        raise FilFeil(
            sti,
            f"lot seg ikke lese som IFC: fila begynner ikke med «ISO-10303-21;».{hint}",
        )

    if SLUTT not in siste:
        raise FilFeil(
            sti,
            "ser avkuttet ut: avslutningen «END-ISO-10303-21;» mangler. Eksporten "
            "ble sannsynligvis avbrutt — eksporter på nytt.",
        )

    try:
        return ifcopenshell.open(str(sti))
    except Exception as feil:
        raise FilFeil(sti, f"lot seg ikke lese som IFC: {feil}") from feil


def les_modell(sti: Path | str, config: Konfigurasjon | None = None) -> list[IfcObjekt]:
    """Åpner IFC 2x3 eller IFC4 og returnerer picklebare `IfcObjekt`.

    Ingen ifcopenshell-entiteter forlater denne funksjonen.
    """
    sti = Path(sti)
    config = config or Konfigurasjon()
    fil = _apne(sti)

    naboer = _koblingsgraf(fil)
    kretser = _kretser(fil, config)
    # Én gang per fil, ikke per objekt: enheten er en egenskap ved fila, og
    # Snowdon har 2439 objekter som alle ville fått det samme svaret.
    faktor = meterfaktor(fil)

    objekter: list[IfcObjekt] = []
    for produkt in fil.by_type("IfcProduct"):
        if produkt.is_a("IfcSpatialStructureElement"):
            continue
        if produkt.is_a("IfcPort"):
            # Porter er kanter, ikke objekter: de bærer ingen TFM-merking og
            # skal ikke telle som kontrollerte objekter. Koblingen de
            # uttrykker er allerede lest inn i `naboer`.
            continue
        egenskaper = _psets(produkt)
        forekomst, forekomst_kilde = _finn(
            egenskaper, config.pset.forekomst, config.pset.egenskapsnavn_forekomst, ligner_tfm_id
        )
        type_verdi, type_kilde = _finn(
            egenskaper, config.pset.type, config.pset.egenskapsnavn_type, ligner_komponenttype
        )
        mmi_verdi, mmi_kilde = _finn(
            egenskaper,
            config.pset.mmi,
            config.pset.egenskapsnavn_mmi,
            lambda v: mmi_niva(v) is not None,
        )
        kilder = {
            navn: kilde
            for navn, kilde in (
                ("forekomst", forekomst_kilde),
                ("type", type_kilde),
                ("mmi", mmi_kilde),
            )
            if kilde is not None
        }
        objekter.append(
            IfcObjekt(
                global_id=produkt.GlobalId,
                ifc_klasse=produkt.is_a(),
                ifc_supertyper=_supertyper(produkt),
                navn=getattr(produkt, "Name", None),
                kildefil=sti.name,
                tfm_forekomst=forekomst,
                tfm_type=type_verdi,
                mmi=mmi_verdi,
                kilder=kilder,
                posisjon=_posisjon(produkt, faktor),
                tilkoblet=sorted(naboer.get(produkt.GlobalId, set())),
                kretser=kretser.get(produkt.GlobalId, []),
            )
        )
    return objekter


# Meter per SI-lengdeenhet med prefiks. Norske modeller er ofte i millimeter,
# og der sto kameraet 8 millimeter fra objektet — praktisk talt inni det.
SI_PREFIKS: dict[str | None, float] = {
    None: 1.0,
    "KILO": 1000.0,
    "DECI": 0.1,
    "CENTI": 0.01,
    "MILLI": 0.001,
}


def meterfaktor(fil: Any) -> float:
    """Meter per lengdeenhet i fila.

    En modell kan være i millimeter, fot eller meter, og koordinatene står i
    modellens egen enhet — ifcopenshell regner ikke om noe. BCF krever meter,
    og uten denne faktoren havnet kameraet 969 kilometer fra objektet i en
    amerikansk eksport.

    Slås opp én gang per fil. Enheten er en egenskap ved fila, og Snowdon har
    2439 objekter som alle ville fått det samme svaret.

    Klarer vi ikke å tolke enheten, gis 1.0. Et kamera på feil sted er en
    dårligere rapport, ikke en mislykket kjøring — samme avveining som
    `_posisjon` gjør når plasseringen ikke lar seg lese.
    """
    try:
        tildeling = fil.by_type("IfcUnitAssignment")
        if not tildeling:
            # IFC krever enheter på IfcProject, så en fil uten er ufullstendig.
            # Meter er den eneste antakelsen som ikke gjør noe verre: faktor 1.0
            # er nøyaktig oppførselen fra før.
            return 1.0
        for enhet in tildeling[0].Units:
            if getattr(enhet, "UnitType", None) != "LENGTHUNIT":
                continue
            if enhet.is_a("IfcSIUnit"):
                return SI_PREFIKS.get(enhet.Prefix, 1.0)
            if enhet.is_a("IfcConversionBasedUnit"):
                faktor = enhet.ConversionFactor
                return float(faktor.ValueComponent.wrappedValue)
    except Exception:
        return 1.0
    return 1.0


def _posisjon(produkt: Any, faktor: float = 1.0) -> tuple[float, float, float] | None:
    """Objektets origo, i METER.

    Går ut fra plasseringskjeden, ikke fra geometrien: en modell kan ha
    titusenvis av objekter, og å tessellere hvert av dem for å finne et punkt
    ville kostet mange sekunder for noe kameraet bare trenger omtrentlig.

    Punktet ender i BCF-viewpointet. Uten det har viewer-en ingen synsvinkel å
    gjenopprette, og svarer «this issue has no viewpoint to zoom to».

    `faktor` er meter per lengdeenhet i fila — se `meterfaktor`. Omregningen
    skjer her og ikke i rapportmodulen: enheter er en IFC-sak, og `tfm_sjekk.ifc`
    er eneste modul som skal kjenne dem. Da betyr feltet meter for alle som
    leser det, og det neste formatet som trenger posisjonen arver garantien
    uten å gjøre noe.
    """
    plassering = getattr(produkt, "ObjectPlacement", None)
    if plassering is None:
        return None
    try:
        import ifcopenshell.util.placement

        matrise = ifcopenshell.util.placement.get_local_placement(plassering)
        return (
            float(matrise[0][3]) * faktor,
            float(matrise[1][3]) * faktor,
            float(matrise[2][3]) * faktor,
        )
    except Exception:
        # Plasseringen kan være sirkulær eller bruke noe vi ikke forstår.
        # Et manglende kamera er en dårligere rapport, ikke en mislykket
        # kjøring — kontrollene bryr seg ikke om posisjon.
        return None


def _by_type(fil: Any, klasse: str) -> list[Any]:
    """`by_type` som tåler at klassen ikke finnes i skjemaet.

    `IfcDistributionCircuit` finnes bare i IFC4, `IfcElectricalCircuit` bare i
    2x3, og ifcopenshell kaster RuntimeError på den som mangler.
    """
    try:
        return fil.by_type(klasse)
    except RuntimeError:
        return []


def _koblingsgraf(fil: Any) -> dict[str, set[str]]:
    """Element → elementene det er koblet til, gjennom portene (K8b/K8c).

    IFC uttrykker dette i to ledd: en port hører til et element, og to porter
    er koblet til hverandre. Leddene leses fra relasjonene direkte i stedet
    for fra inverse attributter — `IfcRelNests` (IFC4) og
    `IfcRelConnectsPortToElement` (2x3) finnes i begge skjemaer, mens hvilken
    av dem en eksportør faktisk bruker varierer.
    """
    eier: dict[int, str] = {}
    for rel in _by_type(fil, "IfcRelNests"):
        vert = rel.RelatingObject
        if vert is None or not hasattr(vert, "GlobalId"):
            continue
        for nestet in rel.RelatedObjects or []:
            if nestet.is_a("IfcPort"):
                eier[nestet.id()] = vert.GlobalId
    for rel in _by_type(fil, "IfcRelConnectsPortToElement"):
        if rel.RelatingPort is not None and rel.RelatedElement is not None:
            eier[rel.RelatingPort.id()] = rel.RelatedElement.GlobalId

    naboer: dict[str, set[str]] = defaultdict(set)
    for rel in _by_type(fil, "IfcRelConnectsPorts"):
        fra = eier.get(rel.RelatingPort.id()) if rel.RelatingPort is not None else None
        til = eier.get(rel.RelatedPort.id()) if rel.RelatedPort is not None else None
        if fra is None or til is None or fra == til:
            continue
        naboer[fra].add(til)
        naboer[til].add(fra)
    return naboer


def _kretser(fil: Any, config: Konfigurasjon) -> dict[str, list[Krets]]:
    """Element → kursgruppene det er tilordnet.

    `is_a(klasse)` matcher arvekjeden, så en eksportør som bruker en subklasse
    av `IfcDistributionCircuit` fanges også.
    """
    ut: dict[str, list[Krets]] = defaultdict(list)
    for rel in _by_type(fil, "IfcRelAssignsToGroup"):
        gruppe = rel.RelatingGroup
        if gruppe is None:
            continue
        if not any(gruppe.is_a(klasse) for klasse in config.elektro.krets_klasser):
            continue
        krets = Krets(global_id=gruppe.GlobalId, navn=getattr(gruppe, "Name", None))
        for objekt in rel.RelatedObjects or []:
            if hasattr(objekt, "GlobalId"):
                ut[objekt.GlobalId].append(krets)
    return ut


@lru_cache(maxsize=512)
def _supertyper_for_klasse(klasse: str, skjema: str) -> tuple[str, ...]:
    """Arvekjeden over `klasse`, uten klassen selv.

    Cachet per (klasse, skjema): en modell har titusenvis av objekter, men
    sjelden mer enn hundre distinkte klasser.
    """
    deklarasjon = ifcopenshell.ifcopenshell_wrapper.schema_by_name(skjema).declaration_by_name(
        klasse
    )
    kjede: list[str] = []
    gjeldende = deklarasjon.as_entity()
    if gjeldende is None:
        return ()
    gjeldende = gjeldende.supertype()
    while gjeldende is not None:
        kjede.append(gjeldende.name())
        gjeldende = gjeldende.supertype()
    return tuple(kjede)


def _supertyper(produkt: Any) -> list[str]:
    try:
        return list(_supertyper_for_klasse(produkt.is_a(), produkt.wrapped_data.file.schema))
    except Exception:
        # Ukjent eller utvidet skjema — kontrollene faller tilbake til
        # eksakt klassematch. Ikke verdt å stoppe hele kjøringen for.
        return []


def _typeobjekt(produkt: Any) -> Any | None:
    """Typeobjektet forekomsten hører til, om det finnes.

    Koblingen heter ikke det samme i de to skjemaene. IFC4 har den omvendte
    attributten `IsTypedBy`; 2x3 har ingen, og der ligger relasjonen inne i
    `IsDefinedBy` sammen med egenskapsrelasjonene. Begge må følges — en modell
    fra Revit kan være hvilken som helst av dem.
    """
    for navn in ("IsTypedBy", "IsDefinedBy"):
        for rel in getattr(produkt, navn, None) or []:
            if rel.is_a("IfcRelDefinesByType"):
                return rel.RelatingType
    return None


def _sett_fra(definisjoner: Any) -> dict[str, dict[str, str]]:
    """Navn/verdi ut av en samling `IfcPropertySet`."""
    ut: dict[str, dict[str, str]] = {}
    for definisjon in definisjoner or []:
        if not definisjon.is_a("IfcPropertySet"):
            continue
        verdier: dict[str, str] = {}
        for prop in definisjon.HasProperties or []:
            if not prop.is_a("IfcPropertySingleValue"):
                continue
            if prop.NominalValue is None:
                continue
            verdier[prop.Name] = str(prop.NominalValue.wrappedValue)
        if verdier:
            ut.setdefault(definisjon.Name, {}).update(verdier)
    return ut


def _psets(produkt: Any) -> dict[str, dict[str, str]]:
    """Egenskapssett på forekomsten OG på typen den hører til, som ren dict.

    IfcOpenShell har `ifcopenshell.util.element.get_psets`, men den er tregere
    og drar inn mer enn vi trenger; her henter vi bare navn/verdi.

    Typens sett legges inn først og forekomstens over. Da overstyrer
    forekomsten av seg selv, som er hva et typeobjekt er i IFC: et utgangspunkt
    en forekomst kan fravike. Den som har skrevet en verdi på selve objektet,
    har gjort det for å si noe om nettopp det objektet.

    Sammenslåingen går felt for felt, ikke sett for sett. Har typen
    `TFM11_Type.TFMType` og forekomsten `TFM11_Type.MMI`, leses begge.

    Uten typeleddet så verktøyet ingenting av en modell merket som
    typeparameter i Revit, og K1 meldte at hvert eneste objekt manglet TFM.
    Rapporten så da ut som en modell uten merking, ikke som et verktøy som
    ikke leste etter.
    """
    ut: dict[str, dict[str, str]] = {}

    type_objekt = _typeobjekt(produkt)
    if type_objekt is not None:
        ut = _sett_fra(getattr(type_objekt, "HasPropertySets", None))

    for rel in getattr(produkt, "IsDefinedBy", None) or []:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        for navn, verdier in _sett_fra([rel.RelatingPropertyDefinition]).items():
            ut.setdefault(navn, {}).update(verdier)
    return ut


def _finn(
    egenskaper: dict[str, dict[str, str]],
    pset_navn: list[str],
    egenskapsnavn: list[str],
    gjenkjenner: Callable[[str], bool],
) -> tuple[str | None, Verdikilde | None]:
    """Finner én verdi, og sier hvor sikkert den ble funnet.

    Tre strategier, i synkende styrke på beviset:

    1. Konfigurert egenskapssett og konfigurert feltnavn. Sikkert.
    2. Et konfigurert feltnavn i et hvilket som helst egenskapssett. Norske
       modeller legger ofte riktig verdi et sted ingen forutså, og et gjenkjent
       feltnavn er bevis nok.
    3. Konfigurert egenskapssett, ukjent feltnavn. En gjetning — og den godtas
       bare hvis verdien er gjenkjennelig som det feltet skal inneholde.

    Steg 3 leser alle feltene, ikke bare det første. Ellers ville utfallet
    avgjøres av rekkefølgen egenskapene tilfeldigvis har i IFC-fila.
    """
    # Alle settene som har et gjenkjent feltnavn, samlet én gang. Sortert på
    # settnavn, så rekkefølgen i IFC-fila ikke avgjør noe: to eksporter av
    # samme modell kan sortere ulikt, og da ville samme modell gitt ulik TFM
    # fra én kjøring til den neste. Samme resonnement som steg 3 gjør for
    # felter innen ett sett, anvendt på tvers av sett.
    kandidater = [
        (pset, navn, verdi)
        for pset in sorted(egenskaper)
        for navn in egenskapsnavn
        if (verdi := (egenskaper[pset].get(navn) or "").strip())
    ]

    def med_uenige(pset: str, navn: str, verdi: str, kilde: Kilde) -> Verdikilde:
        """Kilden, med de kandidatene som IKKE er enige.

        Bare ulike bæres. Samme verdi i to sett er normalt etter en runde
        gjennom Revit — kartleggingsfila skriver den ene, importen legger igjen
        den andre — og en melding om det ville stått på hvert eneste objekt.
        """
        return Verdikilde(
            kilde=kilde,
            pset=pset,
            felt=navn,
            uenige=tuple(dict.fromkeys((p, v) for p, _, v in kandidater if v != verdi)),
        )

    # Steg 1: konfigurert sett og konfigurert felt. Rekkefølgen her er
    # BRUKERENS egen liste i tfm-sjekk.toml, ikke filas, så den skal avgjøre.
    for pset in pset_navn:
        for kandidat_pset, navn, verdi in kandidater:
            if kandidat_pset == pset:
                return verdi, med_uenige(pset, navn, verdi, Kilde.KONFIGURERT)

    # Steg 2: et gjenkjent feltnavn i et hvilket som helst sett.
    if kandidater:
        pset, navn, verdi = kandidater[0]
        return verdi, med_uenige(pset, navn, verdi, Kilde.GJENKJENT_FELT)

    for pset in pset_navn:
        if pset not in egenskaper:
            continue
        forkastet: tuple[str, str] | None = None
        for navn, raa in egenskaper[pset].items():
            verdi = (raa or "").strip()
            if not verdi:
                continue
            if gjenkjenner(verdi):
                return verdi, Verdikilde(kilde=Kilde.GJETTET, pset=pset, felt=navn)
            if forkastet is None:
                forkastet = (navn, verdi)
        if forkastet is not None:
            return None, Verdikilde(
                kilde=Kilde.FORKASTET,
                pset=pset,
                felt=forkastet[0],
                forkastet_verdi=forkastet[1],
            )

    return None, None
