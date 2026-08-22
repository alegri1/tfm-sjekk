"""Konfigurasjon fra ``tfm-sjekk.toml``.

§14 sier: «Gjør alt konfigurerbart, ikke hardkodet. Lever regelsettet som
data.» TFM-tolkningene varierer mellom prosjekter og driftsorganisasjoner,
så grammatikk, pset-navn, IFC-klasser og alvorlighetsgrader hører hjemme her
— ikke som konstanter i kontrollene.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

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


class KontrollOppsett(BaseModel):
    aktiv: bool = True
    alvorlighet: Alvorlighet | None = Field(
        default=None, description="Overstyrer kontrollens standardgrad"
    )


class Konfigurasjon(BaseModel):
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

    @classmethod
    def les(cls, sti: Path | None) -> Konfigurasjon:
        """Leser TOML. Uten fil brukes standardverdiene over."""
        if sti is None:
            return cls()
        with sti.open("rb") as f:
            data = tomllib.load(f)
        oppsett = cls.model_validate(data)
        oppsett.kilde = sti.resolve()
        return oppsett
