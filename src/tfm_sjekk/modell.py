"""Datamodeller for tfm-sjekk.

Alt i denne modulen må være picklebart. Federering (§3) leser hver IFC-fil i
en egen prosess, og resultatene krysser en prosessgrense — ifcopenshell-
entiteter kan ikke pickles. Derfor: ingen import av ifcopenshell her, og
ingen andre steder enn i `tfm_sjekk.ifc`.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class Alvorlighet(StrEnum):
    """Alvorlighetsgrad på et funn. Konfigurerbart per kontroll (§4)."""

    FEIL = "feil"
    ADVARSEL = "advarsel"
    INFO = "info"


class TfmId(BaseModel):
    """En parset TFM-ID.

    Eksempel fra spesifikasjonen (tilluftsvifte):

        ++115080=3600.001.04-JVZ001%JVZ.001.008

    Delene tilsvarer prefiksene ``++`` plassering, ``=`` systemforekomst,
    ``-`` komponentforekomst og ``%`` komponenttype.
    """

    model_config = {"frozen": True}

    raa: str = Field(description="Original streng, uendret")

    plassering: str = Field(description="Byggnummer, normalt 6 siffer")
    systemkode: str = Field(description="NS 3451 tabell 8, normalt 4 siffer")
    system_lopenummer: str
    undernummer: str = Field(
        description="Fagavhengig: tur/retur for VVS, kurs-/sløyfenummer for elektro"
    )
    komponentkode: str = Field(description="NS 3457-8, 3 bokstaver")
    komponent_lopenummer: str

    typekode: str | None = None
    type_lopenummer: str | None = None
    type_undernummer: str | None = None

    @property
    def systemforekomst(self) -> str:
        """``3600.001.04`` — identifiserer ett system i ett bygg."""
        return f"{self.systemkode}.{self.system_lopenummer}.{self.undernummer}"

    @property
    def komponentforekomst(self) -> str:
        """``JVZ001`` — skal være unik i modellen (K6)."""
        return f"{self.komponentkode}{self.komponent_lopenummer}"

    @property
    def global_forekomst(self) -> str:
        """Komponentforekomst kvalifisert med plassering og system.

        K6 sjekker unikhet på denne, ikke på `komponentforekomst` alene —
        samme løpenummer kan gjenbrukes i et annet bygg.
        """
        return f"++{self.plassering}={self.systemforekomst}-{self.komponentforekomst}"

    @property
    def komponenttype(self) -> str | None:
        if self.typekode is None:
            return None
        return f"{self.typekode}.{self.type_lopenummer}.{self.type_undernummer}"

    @property
    def system(self) -> str:
        """``3600.001`` — systemet uten kurs-/undernummer.

        Det er dette som skal være likt for alt som henger på samme fordeling
        (K8b), mens undernummeret er nettopp det som skal variere.
        """
        return f"{self.systemkode}.{self.system_lopenummer}"

    @property
    def kurs(self) -> str:
        """Undernummeret lest som kurs-/sløyfenummer. Bare meningsfullt for
        elektro — se `er_elektro` og §4."""
        return self.undernummer

    @property
    def er_elektro(self) -> bool:
        """Systemer i NS 3451 kapittel 4 (elkraft) og 5 (tele/automatisering).

        Styrer K8. Se §4.
        """
        return self.systemkode[:1] in ("4", "5")


class Krets(BaseModel):
    """En kurs slik den er gruppert i IFC.

    `IfcDistributionCircuit` (IFC4) eller `IfcElectricalCircuit` (2x3), begge
    knyttet til objektene sine med `IfcRelAssignsToGroup`. Revit eksporterer
    dette når kursene faktisk er modellert; mange modeller har det ikke, og
    K8c sier da fra om at den ikke kan konkludere framfor å gjette.
    """

    model_config = {"frozen": True}

    global_id: str
    navn: str | None = None

    def __str__(self) -> str:
        return self.navn or self.global_id


class IfcObjekt(BaseModel):
    """Ett IFC-objekt redusert til det kontrollene trenger.

    Bevisst flat og picklebar — se modulens docstring.
    """

    global_id: str
    ifc_klasse: str
    ifc_supertyper: list[str] = Field(
        default_factory=list,
        description=(
            "Hele arvekjeden, f.eks. IfcAirTerminal → IfcFlowTerminal → … → IfcRoot. "
            "Gjør at konfigurerte klasser kan angis på et generelt nivå uten at "
            "kontrollene trenger tilgang til IFC-skjemaet."
        ),
    )
    navn: str | None = None
    kildefil: str = Field(description="Filnavn, for sporing ved federering")

    tfm_forekomst: str | None = Field(
        default=None, description="Rå verdi fra pset for forekomst, f.eks. TFM11_Forekomst"
    )
    tfm_type: str | None = Field(default=None, description="Rå verdi fra pset for type")
    mmi: str | None = Field(default=None, description="Prosesstatus/MMI, for K9")

    posisjon: tuple[float, float, float] | None = Field(
        default=None,
        description=(
            "Objektets plassering i modellens koordinater. Brukes til å sikte "
            "kameraet i BCF-viewpointet; uten den har viewer-en ingen "
            "synsvinkel å gjenopprette."
        ),
    )
    tilkoblet: list[str] = Field(
        default_factory=list,
        description=(
            "GlobalId-ene til elementene dette er koblet til gjennom porter. "
            "Portene selv er ikke objekter her — de er kanten mellom to "
            "objekter, og forsvinner i uttrekket (K8b/K8c)."
        ),
    )
    kretser: list[Krets] = Field(
        default_factory=list,
        description="Kursgruppene objektet er tilordnet med IfcRelAssignsToGroup",
    )

    def er_av_type(self, klasse: str) -> bool:
        """Som ifcopenshell sin `is_a(klasse)`, men uten ifcopenshell."""
        return klasse == self.ifc_klasse or klasse in self.ifc_supertyper

    def __str__(self) -> str:
        navn = f" «{self.navn}»" if self.navn else ""
        return f"{self.ifc_klasse}{navn} [{self.global_id}]"


class Funn(BaseModel):
    """Ett kontrollfunn. Rapportformatene (BCF/HTML/CSV) rendrer denne."""

    kontroll: str = Field(description="Kontroll-ID, f.eks. «K2»")
    alvorlighet: Alvorlighet
    melding: str = Field(description="Forklarende tekst på norsk (§4)")

    global_id: str | None = None
    ifc_klasse: str | None = None
    kildefil: str | None = None
    verdi: str | None = Field(default=None, description="Den aktuelle TFM-verdien, om relevant")
    posisjon: tuple[float, float, float] | None = Field(
        default=None, description="Objektets plassering, til kameraet i BCF-viewpointet"
    )

    @classmethod
    def for_objekt(
        cls,
        kontroll: str,
        alvorlighet: Alvorlighet,
        melding: str,
        objekt: IfcObjekt,
        verdi: str | None = None,
    ) -> Funn:
        return cls(
            kontroll=kontroll,
            alvorlighet=alvorlighet,
            melding=melding,
            global_id=objekt.global_id,
            ifc_klasse=objekt.ifc_klasse,
            kildefil=objekt.kildefil,
            verdi=verdi if verdi is not None else objekt.tfm_forekomst,
            posisjon=objekt.posisjon,
        )

    def sorteringsnokkel(self) -> tuple[str, str, str]:
        """Deterministisk rekkefølge — golden files (§7) krever det."""
        return (self.kontroll, self.kildefil or "", self.global_id or "")
