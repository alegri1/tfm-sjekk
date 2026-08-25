"""Konfigurasjon fra ``tfm-sjekk.toml``.

§14 sier: «Gjør alt konfigurerbart, ikke hardkodet. Lever regelsettet som
data.» TFM-tolkningene varierer mellom prosjekter og driftsorganisasjoner,
så grammatikk, pset-navn, IFC-klasser og alvorlighetsgrader hører hjemme her
— ikke som konstanter i kontrollene.
"""

from __future__ import annotations

import difflib
import tomllib
from fnmatch import fnmatch
from pathlib import Path
from typing import get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from tfm_sjekk.modell import Alvorlighet

OPPSETTNAVN = "tfm-sjekk.toml"


def finn_oppsett(modeller: list[Path], arbeidskatalog: Path | None = None) -> Path | None:
    """Leter etter tfm-sjekk.toml: hos modellen først, så i arbeidskatalogen.

    Rekkefølgen følger av hvor brukeren er. Ved dra-og-slipp er arbeidskatalogen
    programmets egen mappe, som ikke har med prosjektet å gjøre — det er samme
    innsikt som ligger bak at rapporten legges hos modellen og ikke hos exe-en.

    Bare to steder, begge til å peke på i en setning. Et søk oppover i
    mappetreet kunne plukket opp en fil langt unna, og da er «hvilken fil ble
    lest» ikke lenger noe man kan svare på uten å kjøre.
    """
    steder = []
    if modeller:
        steder.append(Path(modeller[0]).resolve().parent)
    steder.append(Path(arbeidskatalog) if arbeidskatalog else Path.cwd())

    for mappe in steder:
        kandidat = mappe / OPPSETTNAVN
        if kandidat.is_file():
            return kandidat
    return None


class Grammatikk(BaseModel):
    """Sifferantall i TFM-ID-en. Se §1 for standardoppsettet."""

    model_config = ConfigDict(extra="forbid")

    plassering_siffer: int = 6
    systemkode_siffer: int = 4
    system_lopenummer_siffer: int = 3
    undernummer_siffer_min: int = 2
    undernummer_siffer_maks: int = 3
    komponentkode_bokstaver: int = 3
    komponent_lopenummer_siffer: int = 3
    type_lopenummer_siffer: int = 3
    type_undernummer_siffer: int = 3

    krev_plassering: bool = Field(
        default=True,
        description=(
            "Om ++-delen må være til stede. En tidlig modell har ikke alltid fått "
            "byggnummer, mens systemet og komponenten er merket og skal kunne "
            "kontrolleres. Standarden krever den, slik at et eksisterende oppsett "
            "ikke endrer oppførsel."
        ),
    )

    krev_komponenttype: bool = Field(
        default=False,
        description="Om %-delen må være til stede. Mange prosjekter utelater den.",
    )


class PsetOppsett(BaseModel):
    """Hvor TFM-verdiene ligger. Navnene under er de vanlige i norske
    Revit-maler, men de varierer — derfor konfigurerbart (§3)."""

    model_config = ConfigDict(extra="forbid")

    forekomst: list[str] = ["TFM11_Forekomst"]
    type: list[str] = ["TFM11_Type"]
    mmi: list[str] = ["MMI", "Prosesstatus"]

    egenskapsnavn_forekomst: list[str] = ["TFM", "TFMForekomst", "Forekomst"]
    # To navn er fjernet herfra, begge fordi et treff på dem ikke er bevis for
    # at verdien er en komponenttype: «Type» finnes i
    # Pset_ManufacturerTypeInformation i praktisk talt enhver modell, og «TFM»
    # er forekomstens eget kandidatnavn — et treff der gir hele TFM-ID-en.
    egenskapsnavn_type: list[str] = ["TFMType", "TFM11_Type"]
    egenskapsnavn_mmi: list[str] = ["MMI", "Prosesstatus"]


class MmiOppsett(BaseModel):
    """Prosesstatus/MMI (K9).

    Skalaen varierer mellom prosjekter og byggherrer, så den er data (§14).
    Standardverdiene er den vanlige norske MMI-skalaen; bruker prosjektet en
    annen, settes den her. Tom liste slår av verdisjekken helt.
    """

    model_config = ConfigDict(extra="forbid")

    gyldige_verdier: list[str] = ["100", "200", "300", "350", "400", "500"]

    krev_pa_alle: bool = Field(
        default=False,
        description=(
            "Om MMI kreves på alle objekter i omfanget. Uten dette sier K9 bare "
            "fra om manglende MMI i modeller som ellers bruker MMI — en modell "
            "der ingen har satt det er antatt å ikke bruke MMI i det hele tatt."
        ),
    )


class ElektroOppsett(BaseModel):
    """Hva som er en fordeling og hva som er en kurs (K8b/K8c).

    Klassenavnene er ikke de samme i IFC 2x3 og IFC4 — 2x3 har
    `IfcElectricDistributionPoint`, IFC4 har `IfcElectricDistributionBoard` —
    så begge står i lista. Navn som ikke finnes i skjemaet til fila som leses
    hoppes over.
    """

    model_config = ConfigDict(extra="forbid")

    fordeling_klasser: list[str] = [
        "IfcElectricDistributionBoard",  # IFC4
        "IfcElectricDistributionPoint",  # IFC 2x3
        "IfcDistributionBoard",  # IFC4.3
    ]
    krets_klasser: list[str] = [
        "IfcDistributionCircuit",  # IFC4
        "IfcElectricalCircuit",  # IFC 2x3
    ]

    # Klassene som BÆRER kurser framfor å ligge på en. K8a krever kursnummer av
    # elektroobjekter, og et kabelrør har ikke noe kursnummer å ha — det fører
    # dem. Samme argument som allerede gjelder fordelinger: tavla er roten
    # kursene går ut fra.
    #
    # De fire siste finnes bare i IFC4. Det er ufarlig å liste dem: treff går
    # mot objektets egen arvekjede, så et navn som ikke finnes i skjemaet
    # matcher aldri noe.
    #
    # Segment og Fitting er brede og dekker også VVS-rør. Det gjør ingenting —
    # K8a gjelder bare NS 3451 kapittel 4 og 5, så en ventilasjonskanal er
    # allerede utenfor.
    foring_klasser: list[str] = [
        "IfcFlowSegment",
        "IfcFlowFitting",
        "IfcCableCarrierSegment",  # IFC4
        "IfcCableCarrierFitting",  # IFC4
        "IfcCableSegment",  # IFC4
        "IfcCableFitting",  # IFC4
    ]

    # Systemkoder som ER føringsvei, uansett hvilken IFC-klasse objektet fikk.
    #
    # Klassen sier hva eksporten fikk til; systemkoden sier hva prosjektet har
    # bestemt at objektet er. En ekte Revit-eksport ga seksten koblingsbokser
    # som IfcBuildingElementProxy — TFM-en sa føringsvei, klassen sa ingenting.
    #
    # TOM MED VILJE. Hvilken kode som betyr føringsvei står i NS 3451, som er en
    # betalt standard, og innholdet skal ikke ligge i verktøyet (§8). Mekanismen
    # hører hjemme her; koden hører hjemme hos prosjektet. Se tfm-sjekk.toml for
    # et utfylt eksempel.
    foring_systemkoder: list[str] = []


class MasterOppsett(BaseModel):
    """Hvor systemene og komponenttypene står i prosjektets TFM-master (K7).

    Formatet er ikke standardisert — hvert prosjekt lager sin egen mal — så
    kolonnenavnene må være data (§14). Listene er kandidater: første kolonne
    som matcher vinner.

    Merk at det er *kolonnenavnene* som styrer, ikke arknavnene. Alle ark i
    en XLSX leses, og de som ikke har noen gjenkjennelig kolonne hoppes over.
    Det tåler «Ark1» og «Systemliste rev. C» like godt, og et prosjekt som
    legger systemer og komponenttyper side om side i samme ark fungerer også.
    """

    model_config = ConfigDict(extra="forbid")

    kolonne_system: list[str] = ["systemforekomst", "system", "systemid", "tfm-system"]
    kolonne_komponenttype: list[str] = ["komponenttype", "type", "typeid", "tfm-type"]
    kolonne_komponentforekomst: list[str] = ["komponentforekomst", "forekomst", "komponent"]

    maks_overskriftsrader: int = Field(
        default=10,
        description=(
            "Hvor mange rader det letes etter overskriftsraden i. Ekte mastere "
            "har ofte logo, prosjektnavn og revisjonstabell over selve tabellen."
        ),
    )


class FagmodellOppsett(BaseModel):
    """Omfanget for fagmodellene som treffer ett filnavnmønster.

    Finnes fordi en federering blander filer med ulikt ansvar. Arkitekten
    tegner armaturer og servanter for å vise rommet, og de skal ikke merkes av
    RIE — en ekte kjøring mot Snowdon Towers ga 675 K1-funn på dem, mot 177
    ekte funn i elektromodellen.

    Tom liste betyr at fila ikke kontrolleres for TFM. Det er den eneste måten
    å unnta på; en egen «aktiv»-nøkkel ved siden av lista ville før eller siden
    kommet i konflikt med den.
    """

    model_config = ConfigDict(extra="forbid")

    ifc_klasser: list[str] = Field(
        default=[],
        description=(
            "Klassene som kontrolleres i fagmodeller som treffer mønsteret. "
            "Tom liste: fila kontrolleres ikke for TFM."
        ),
    )


class KontrollOppsett(BaseModel):
    model_config = ConfigDict(extra="forbid")
    aktiv: bool = True
    alvorlighet: Alvorlighet | None = Field(
        default=None, description="Overstyrer kontrollens standardgrad"
    )


class OppsettFeil(Exception):
    """Konfigurasjonen ble ikke forstått, og kjøringen skal stoppe.

    Samme linje som en sti i oppsettet som peker feil: en nøkkel verktøyet
    forkaster i stillhet gir en rapport laget med andre regler enn den som
    skrev fila ba om — og den ser like ren ut. Det har skjedd: «ifc_klasser»
    skrevet etter «[pset]» leses av TOML som «pset.ifc_klasser».
    """


def _er_kart(annotasjon: object) -> bool:
    """Sant for `dict[str, EnEllerAnnenModell]`."""
    return get_origin(annotasjon) is dict


def _modellen_bak(annotasjon: object) -> type[BaseModel] | None:
    """Pydantic-modellen et felt beskriver, enten direkte eller som verdi i et kart.

    `kontroller` og `fagmodell` er begge `dict[str, Modell]`. Uten dette
    stoppet oppslaget på dem, og nøklene under fikk aldri et forslag.
    """
    if isinstance(annotasjon, type) and issubclass(annotasjon, BaseModel):
        return annotasjon
    if _er_kart(annotasjon):
        argumenter = get_args(annotasjon)
        verdi = argumenter[1] if len(argumenter) > 1 else None
        if isinstance(verdi, type) and issubclass(verdi, BaseModel):
            return verdi
    return None


def _gyldige_nokler(sti: tuple) -> list[str]:
    """Feltnavnene som hører hjemme der den ukjente nøkkelen sto.

    Hentes fra modellen, ikke skrevet av. En håndskrevet liste driver fra
    modellen første gang noen legger til en nøkkel.
    """
    modell: type[BaseModel] = Konfigurasjon
    ledd = list(sti[:-1])
    while ledd:
        felt = modell.model_fields.get(str(ledd.pop(0)))
        if felt is None:
            return []
        neste = _modellen_bak(felt.annotation)
        if neste is None:
            return []
        modell = neste
        # En seksjon som «[kontroller.K4]» eller «[fagmodell."*Arch*"]» har et
        # ledd til som er en nøkkel brukeren fant på, ikke et feltnavn. Det
        # hoppes over — uten dette ga hele denne grenen ingen forslag, og en
        # skrivefeil under [kontroller.K4] sto uten «Mente du?».
        if _er_kart(felt.annotation) and ledd:
            ledd.pop(0)
    return list(modell.model_fields)


def _stedet(loc: tuple) -> str:
    """Hvor nøkkelen faktisk sto, i samme form som kartet bruker."""
    return "toppnivå" if len(loc) == 1 else f"[{'.'.join(str(x) for x in loc[:-1])}]"


def _som_sted(steder: list[str]) -> str:
    """«på toppnivå», «i [grammatikk]», «i [mmi] eller [elektro]».

    Preposisjonen følger stedet: man er PÅ toppnivå og I en seksjon.
    """
    deler = [("på " if s == "toppnivå" else "i ") + s for s in steder]
    if len(deler) == 1:
        return deler[0]
    return " eller ".join([", ".join(deler[:-1]), deler[-1]])


def _hvor_horer_nokkelen_hjemme(nokkel: str) -> list[str]:
    """Stedene et feltnavn er gyldig, som «toppnivå» eller «[grammatikk]».

    Bygges av modellenes egne `model_fields`. En håndskrevet tabell ville drevet
    fra modellen første gang noen la til et felt — samme grunn til at
    `_gyldige_nokler` leser modellen framfor en liste.

    Gir alle stedene, ikke det første. Finnes samme navn to steder, er det å
    peke på ett av dem i en vilkårlig rekkefølge en gjetning forkledd som et
    svar.
    """
    steder = []
    if nokkel in Konfigurasjon.model_fields:
        steder.append("toppnivå")
    for seksjon, felt in Konfigurasjon.model_fields.items():
        annotasjon = felt.annotation
        if (
            isinstance(annotasjon, type)
            and issubclass(annotasjon, BaseModel)
            and nokkel in annotasjon.model_fields
        ):
            steder.append(f"[{seksjon}]")
    return steder


def _ukjente_nokler(sti: Path, feil: ValidationError) -> str:
    """Pydantics feil oversatt til noe en BIM-koordinator kan handle på.

    «Extra inputs are not permitted» med en feltsti sier hverken hva som er galt
    eller hva det skulle stått, og det er engelsk i et verktøy der alt annet er
    norsk.
    """
    linjer = [f"Feil i {sti}:"]
    for e in feil.errors():
        if e["type"] != "extra_forbidden":
            linjer.append(f"  {'.'.join(str(x) for x in e['loc'])}: {e['msg']}")
            continue
        nokkel = str(e["loc"][-1])
        if len(e["loc"]) == 1 and isinstance(e.get("input"), dict):
            linjer.append(f"  Ukjent seksjon [{nokkel}].")
        elif len(e["loc"]) == 1:
            linjer.append(f"  Ukjent nøkkel «{nokkel}» på toppnivå.")
        else:
            seksjon = ".".join(str(x) for x in e["loc"][:-1])
            linjer.append(f"  Ukjent nøkkel «{nokkel}» i [{seksjon}].")
        # 0.85, ikke difflibs standard 0.6. Målt på ekte skrivefeil:
        # «foring_systemkode» → «foring_systemkoder» gir 0.97 og «systemtabel»
        # → «systemtabell» gir 0.96, mens «krev_plasering» — som hører hjemme i
        # [grammatikk] — traff «krets_klasser» med 0.67. Et forslag som peker
        # galt sender brukeren av gårde i feil retning, og er verre enn ingen.
        # Å peke hjem går foran å foreslå noe som ligner. Et identisk navn et
        # annet sted er et svar; et lignende navn i samme seksjon er en
        # gjetning, og en gjetning som ser ut som en opplysning sender brukeren
        # til feil sted.
        hjemme = [s for s in _hvor_horer_nokkelen_hjemme(nokkel) if s != _stedet(e["loc"])]
        if hjemme:
            linjer.append(f"  Den hører hjemme {_som_sted(hjemme)}.")
            continue
        nære = difflib.get_close_matches(nokkel, _gyldige_nokler(e["loc"]), n=1, cutoff=0.85)
        if nære:
            linjer.append(f"  Mente du «{nære[0]}»?")
    return "\n".join(linjer)


class Konfigurasjon(BaseModel):
    model_config = ConfigDict(extra="forbid")
    grammatikk: Grammatikk = Grammatikk()
    pset: PsetOppsett = PsetOppsett()
    master: MasterOppsett = MasterOppsett()
    elektro: ElektroOppsett = ElektroOppsett()
    mmi: MmiOppsett = MmiOppsett()

    ifc_klasser: list[str] = Field(
        default=[
            "IfcDistributionElement",
            "IfcFlowTerminal",
            "IfcFlowController",
            "IfcFlowMovingDevice",
            "IfcEnergyConversionDevice",
            "IfcDistributionFlowElement",
        ],
        description="Hvilke klasser K1 krever TFM på. Utvid per fag.",
    )

    kontroller: dict[str, KontrollOppsett] = {}

    fagmodell: dict[str, FagmodellOppsett] = Field(
        default={},
        description=(
            "Omfang per fagmodell, nøklet på filnavnmønster, f.eks. "
            '[fagmodell."*Architectural*"]. Tom klasseliste unntar fila.'
        ),
    )

    modeller: list[str] = Field(
        default=[],
        description=(
            "IFC-filene en kjøring leser når ingen er oppgitt på kommandolinjen. "
            "Filnavn eller mønster, f.eks. «eksport/*.ifc». Løses mot denne fila."
        ),
    )
    ut: Path | None = Field(
        default=None, description="Hvor rapportene legges når --ut ikke er oppgitt"
    )

    tfm_master: Path | None = Field(default=None, description="TFM-master, XLSX eller CSV (K7)")
    systemtabell: Path | None = Field(
        default=None, description="Din egen CSV med NS 3451 tabell 8 (K3, K4)"
    )
    komponenttabell: Path | None = Field(
        default=None, description="Din egen CSV med NS 3457-8 (K5)"
    )

    kilde: Path | None = Field(
        default=None,
        exclude=True,
        description=(
            "Konfigurasjonsfila dette ble lest fra. Relative stier over løses mot "
            "mappa den ligger i — objektet som bærer stiene må bære opphavet sitt, "
            "ellers kan de ikke tolkes."
        ),
    )

    def oppsett_for(self, kontroll_id: str) -> KontrollOppsett:
        return self.kontroller.get(kontroll_id, KontrollOppsett())

    def sti(self, felt: str) -> Path | None:
        """En sti fra konfigurasjonen, løst mot fila den står i.

        Relativt til konfigurasjonsfila, ikke til arbeidskatalogen: oppsettet
        hører til prosjektet, sammen med tabellene det peker på. Tolket mot
        arbeidskatalogen ville samme fil gitt ulikt resultat avhengig av hvor
        terminalen tilfeldigvis sto, og den kunne ikke sendes til en kollega.
        """
        verdi: Path | None = getattr(self, felt)
        if verdi is None or verdi.is_absolute() or self.kilde is None:
            return verdi
        return (self.kilde.parent / verdi).resolve()

    def _fagmodelltreff(self, kildefil: str) -> FagmodellOppsett | None:
        """Seksjonen som gjelder for en fagmodell, eller None.

        Treffer flere mønstre, vinner det lengste — «*Sample Architectural*» er
        mer spesifikt enn «*». Å ta det første i en vilkårlig rekkefølge ville
        vært en gjetning forkledd som et svar; det er samme grunn til at
        `_hvor_horer_nokkelen_hjemme` nekter å peke på ett av flere steder.

        To like lange som begge treffer er en feil i oppsettet, ikke noe å
        velge mellom.
        """
        treff = [(m, o) for m, o in self.fagmodell.items() if fnmatch(kildefil, m)]
        if not treff:
            return None

        lengst = max(len(m) for m, _ in treff)
        beste = [m for m, _ in treff if len(m) == lengst]
        if len(beste) > 1:
            raise OppsettFeil(
                "Flere like spesifikke mønstre i [fagmodell] treffer «{}»: {}. "
                "Verktøyet kan ikke velge mellom dem — gjør ett av dem mer "
                "spesifikt, eller fjern det ene.".format(kildefil, ", ".join(sorted(beste)))
            )
        return dict(treff)[beste[0]]

    def omfang_for(self, kildefil: str) -> list[str]:
        """IFC-klassene som kontrolleres i denne fagmodellen.

        Uten treff gjelder `ifc_klasser` på toppnivå, som før. Det er dette som
        gjør at et oppsett uten [fagmodell] oppfører seg bit for bit som i dag.
        """
        oppsett = self._fagmodelltreff(kildefil)
        return self.ifc_klasser if oppsett is None else oppsett.ifc_klasser

    def er_unntatt(self, kildefil: str) -> bool:
        """Sant når fila er unntatt med vilje: et mønster med tom klasseliste.

        Skiller seg fra «omfanget ble tomt» ved at noen har skrevet det. D1 kan
        ikke se forskjellen på tallene — begge gir null i omfanget — og det er
        nettopp derfor kontrollen må spørre oppsettet.
        """
        oppsett = self._fagmodelltreff(kildefil)
        return oppsett is not None and not oppsett.ifc_klasser

    def stier(self, felt: str) -> list[tuple[str, Path, list[Path]]]:
        """Per oppføring i et listefelt: teksten, stien den ble løst til, og treffene.

        Tre ledd og ikke bare filene, fordi en oppføring uten treff skal kunne
        meldes med begge halvdeler. «eksport/*.ifc finnes ikke» er ubrukelig når
        «eksport» er relativ til en fil brukeren ikke tenkte på.

        Mønstre utvides, og treffene sorteres. Filsystemets egen rekkefølge er
        ikke lik mellom maskiner, og rapporttittelen og BCF-fila bygges av
        rekkefølgen — usortert ville fila ikke vært byte-identisk for samme
        funn, og avviket ville bare vist seg hos noen andre.
        """
        rot = self.kilde.parent if self.kilde is not None else Path.cwd()
        ut: list[tuple[str, Path, list[Path]]] = []
        for rå in getattr(self, felt):
            løst = Path(rå) if Path(rå).is_absolute() else (rot / rå)
            if any(tegn in rå for tegn in "*?["):
                treff = sorted(p for p in løst.parent.glob(løst.name) if p.is_file())
            else:
                treff = [løst.resolve()] if løst.is_file() else []
            ut.append((rå, løst, treff))
        return ut

    @classmethod
    def les(cls, sti: Path | None) -> Konfigurasjon:
        """Leser TOML. Uten fil brukes standardverdiene over.

        En nøkkel verktøyet ikke kjenner stopper kjøringen framfor å bli
        forkastet. Se `OppsettFeil` for hvorfor.
        """
        if sti is None:
            return cls()

        # utf-8-sig, ikke utf-8: Notisblokk og PowerShells «Set-Content -Encoding
        # utf8» skriver BOM, og tomllib leser den som et tegn på linje 1. Uten
        # dette svarte verktøyet med en Python-tilbakesporing og exit 1 på en fil
        # som så helt riktig ut i editoren — og oppsettet er nettopp fila
        # brukeren redigerer selv.
        try:
            data = tomllib.loads(sti.read_text(encoding="utf-8-sig"))
        except tomllib.TOMLDecodeError as feil:
            raise OppsettFeil(f"Feil i {sti.name}:\n  Ugyldig TOML: {feil}") from feil

        try:
            oppsett = cls.model_validate(data)
        except ValidationError as feil:
            raise OppsettFeil(_ukjente_nokler(sti, feil)) from feil
        oppsett.kilde = sti.resolve()
        return oppsett
