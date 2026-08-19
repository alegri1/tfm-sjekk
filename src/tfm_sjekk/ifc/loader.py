"""Leser én IFC-fil og trekker ut TFM-verdiene fra egenskapssettene."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from functools import lru_cache
from pathlib import Path
from typing import Any

import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.modell import IfcObjekt, Kilde, Krets, Verdikilde
from tfm_sjekk.parser import ligner_komponenttype, ligner_tfm_id, mmi_niva


def les_modell(sti: Path | str, config: Konfigurasjon | None = None) -> list[IfcObjekt]:
    """Åpner IFC 2x3 eller IFC4 og returnerer picklebare `IfcObjekt`.

    Ingen ifcopenshell-entiteter forlater denne funksjonen.
    """
    sti = Path(sti)
    config = config or Konfigurasjon()
    fil = ifcopenshell.open(str(sti))

    naboer = _koblingsgraf(fil)
    kretser = _kretser(fil, config)

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
                posisjon=_posisjon(produkt),
                tilkoblet=sorted(naboer.get(produkt.GlobalId, set())),
                kretser=kretser.get(produkt.GlobalId, []),
            )
        )
    return objekter


def _posisjon(produkt: Any) -> tuple[float, float, float] | None:
    """Objektets origo i modellens koordinater.

    Går ut fra plasseringskjeden, ikke fra geometrien: en modell kan ha
    titusenvis av objekter, og å tessellere hvert av dem for å finne et punkt
    ville kostet mange sekunder for noe kameraet bare trenger omtrentlig.

    Punktet ender i BCF-viewpointet. Uten det har viewer-en ingen synsvinkel å
    gjenopprette, og svarer «this issue has no viewpoint to zoom to».
    """
    plassering = getattr(produkt, "ObjectPlacement", None)
    if plassering is None:
        return None
    try:
        import ifcopenshell.util.placement

        matrise = ifcopenshell.util.placement.get_local_placement(plassering)
        return (float(matrise[0][3]), float(matrise[1][3]), float(matrise[2][3]))
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


def _psets(produkt: Any) -> dict[str, dict[str, str]]:
    """Egenskapssett på forekomsten, som ren dict.

    IfcOpenShell har `ifcopenshell.util.element.get_psets`, men den er tregere
    og drar inn mer enn vi trenger; her henter vi bare navn/verdi.

    MANGEL: typeegenskaper leses ikke. Ligger TFM-verdien på typeobjektet —
    en Revit-familietype med TFM som typeparameter — ser verktøyet ingenting,
    og K1 melder at hvert eneste objekt mangler TFM.

    Koblingen ligger i `IsTypedBy` i IFC4 og som en `IfcRelDefinesByType` i
    `IsDefinedBy` i 2x3; ingen av delene fanges her. Prøvd i begge skjemaer,
    se `test_ifc.py::test_typeegenskaper_leses_ikke`.

    Om det er verdt å lukke avhenger av om norske eksporter faktisk merker på
    typen. Det er et spørsmål til en RIE, ikke en antakelse å kode på.
    """
    ut: dict[str, dict[str, str]] = {}
    for rel in getattr(produkt, "IsDefinedBy", None) or []:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        definisjon = rel.RelatingPropertyDefinition
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
            ut[definisjon.Name] = verdier
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
    for pset in pset_navn:
        if pset not in egenskaper:
            continue
        for navn in egenskapsnavn:
            verdi = (egenskaper[pset].get(navn) or "").strip()
            if verdi:
                return verdi, Verdikilde(kilde=Kilde.KONFIGURERT, pset=pset, felt=navn)

    for pset, verdier in egenskaper.items():
        for navn in egenskapsnavn:
            verdi = (verdier.get(navn) or "").strip()
            if verdi:
                return verdi, Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset=pset, felt=navn)

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
