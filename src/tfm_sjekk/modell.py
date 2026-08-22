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


class Kilde(StrEnum):
    """Hvordan verktøyet kom fram til en verdi.

    Rekkefølgen er styrken på beviset: et konfigurert felt er sikkert, et
    gjenkjent feltnavn andre steder er godt nok, en gjetning er en gjetning.
    """

    KONFIGURERT = "konfigurert"
    GJENKJENT_FELT = "gjenkjent felt"
    GJETTET = "gjettet"
    FORKASTET = "forkastet"


class Verdikilde(BaseModel):
    """Hvor en verdi ble lest fra, og med hvilken sikkerhet.

    Følger objektet gjennom prosessgrensa som ren data — se modulens
    docstring. Kontrollene leser den som strenger og trenger ikke vite hva et
    egenskapssett er.
    """

    model_config = {"frozen": True}

    kilde: Kilde
    pset: str
    felt: str
    forkastet_verdi: str | None = Field(
        default=None, description="Verdien som ble forkastet, til bruk i meldingen"
    )

    @property
    def sikker(self) -> bool:
        return self.kilde is Kilde.KONFIGURERT

    def forklaring(self) -> str | None:
        """Én setning om opphavet, til bruk i et funn. None når verdien er sikker."""
        if self.kilde is Kilde.KONFIGURERT:
            return None
        if self.kilde is Kilde.FORKASTET:
            return (
                f"Egenskapssettet «{self.pset}» har feltet «{self.felt}» med verdien "
                f"«{self.forkastet_verdi}», som ikke er gjenkjennelig som det feltet "
                f"skal inneholde."
            )
        if self.kilde is Kilde.GJENKJENT_FELT:
            return f"Verdien ble lest fra egenskapssettet «{self.pset}», feltet «{self.felt}»."
        return (
            f"Verdien ble gjettet fra egenskapssettet «{self.pset}», feltet «{self.felt}», "
            f"som ikke er et konfigurert feltnavn."
        )


class TfmId(BaseModel):
    """En parset TFM-ID.

    Eksempel fra spesifikasjonen (tilluftsvifte):

        ++115080=3600.001.04-JVZ001%JVZ.001.008

    Delene tilsvarer prefiksene ``++`` plassering, ``=`` systemforekomst,
    ``-`` komponentforekomst og ``%`` komponenttype.
    """

    model_config = {"frozen": True}

    raa: str = Field(description="Original streng, uendret")

    plassering: str | None = Field(
        default=None,
        description=(
            "Byggnummer, normalt 6 siffer. None når grammatikken har gjort delen "
            "valgfri og modellen ikke har fått byggnummer ennå."
        ),
    )
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

        Mangler plasseringen, bygges nøkkelen av delene som finnes. En ID med
        plassering og en uten havner da i hvert sitt nøkkelrom og kolliderer
        ikke. Alternativet — å normalisere plasseringen bort for alle — ville
        meldt to bygg med samme system og komponent som duplikat, og et falskt
        funn i en unikhetskontroll er dyrere enn et uteblitt: det lærer brukeren
        å overse kontrollen, og da er også de ekte funnene tapt.
        """
        start = f"++{self.plassering}" if self.plassering is not None else ""
        return f"{start}={self.systemforekomst}-{self.komponentforekomst}"

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

    kilder: dict[str, Verdikilde] = Field(
        default_factory=dict,
        description=(
            "Hvor hver verdi kom fra, nøklet på «forekomst», «type» og «mmi». "
            "Et funn som hviler på noe annet enn den konfigurerte veien sier det."
        ),
    )
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
    tfm: str | None = Field(
        default=None,
        description=(
            "Objektets egen TFM-forekomstverdi, uansett hva funnet handler om. "
            "Dette er nøkkelen noe utenfor verktøyet kan koble funnet til objektet "
            "med. Tom når funnet ikke gjelder et objekt, eller objektet mangler TFM."
        ),
    )
    verdi: str | None = Field(
        default=None,
        description=(
            "Verdien funnet handler om. For de fleste kontroller er det TFM-verdien, "
            "men ikke alltid: K9 melder om MMI og legger MMI-verdien her. Bruk `tfm` "
            "når du trenger objektets identitet."
        ),
    )
    posisjon: tuple[float, float, float] | None = Field(
        default=None, description="Objektets plassering, til kameraet i BCF-viewpointet"
    )
    kilde: Verdikilde | None = Field(
        default=None, description="Hvor verdien funnet hviler på ble lest fra"
    )

    @classmethod
    def for_objekt(
        cls,
        kontroll: str,
        alvorlighet: Alvorlighet,
        melding: str,
        objekt: IfcObjekt,
        verdi: str | None = None,
        felt: str = "forekomst",
    ) -> Funn:
        """`felt` sier hvilken av objektets verdier funnet hviler på, slik at
        meldingen kan si fra hvis nettopp den ble lest et uventet sted."""
        kilde = objekt.kilder.get(felt)
        opphav = kilde.forklaring() if kilde else None
        return cls(
            kontroll=kontroll,
            alvorlighet=alvorlighet,
            melding=f"{melding} {opphav}" if opphav else melding,
            kilde=kilde,
            global_id=objekt.global_id,
            ifc_klasse=objekt.ifc_klasse,
            kildefil=objekt.kildefil,
            # Ingen parameter for `tfm`, med vilje. `verdi` kan overstyres av
            # kontrollen som melder, og det var nettopp den overstyrbarheten som
            # gjorde den ubrukelig som nøkkel. Et felt som skal kunne stoles på,
            # må ikke kunne settes av den som melder funnet.
            tfm=objekt.tfm_forekomst,
            verdi=verdi if verdi is not None else objekt.tfm_forekomst,
            posisjon=objekt.posisjon,
        )

    def sorteringsnokkel(self) -> tuple[str, str, str]:
        """Deterministisk rekkefølge — golden files (§7) krever det."""
        return (self.kontroll, self.kildefil or "", self.global_id or "")
