"""Datamodellen for et konfigurasjonsforslag."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from tfm_sjekk.modell import Kilde


class Verditype(StrEnum):
    """Hvilken av de tre verdiene et forslag gjelder.

    Samme navn som nøklene i `IfcObjekt.kilder`, slik at aggregeringen kan gå
    rett fra kilde til forslag uten en oversettelsestabell i mellom.
    """

    FOREKOMST = "forekomst"
    TYPE = "type"
    MMI = "mmi"

    @property
    def pset_attributt(self) -> str:
        """Feltet i `PsetOppsett` som holder egenskapssettene for denne verdien."""
        return self.value

    @property
    def felt_attributt(self) -> str:
        """Feltet i `PsetOppsett` som holder feltnavnene for denne verdien."""
        return f"egenskapsnavn_{self.value}"

    @property
    def omtale(self) -> str:
        """Hva verdien heter i tekst til bruker."""
        return {"forekomst": "TFM-forekomst", "type": "TFM-type", "mmi": "MMI/prosesstatus"}[
            self.value
        ]


class Foreslatt(BaseModel):
    """Én foreslått verdi, med belegget den hviler på.

    Antallet er ikke pynt. Forskjellen mellom et egenskapssett brukt på 840
    objekter og ett brukt på 2 er hele forskjellen mellom en prosjektkonvensjon
    og en tilfeldighet, og bare den som ser tallet kan avgjøre hvilken det er.
    """

    model_config = {"frozen": True}

    verdi: str
    antall: int = Field(description="Objekter verdien ble observert på")
    kilde: Kilde | None = Field(
        default=None,
        description=(
            "Hvordan verdien ble funnet. None for et klasseforslag: beviset der "
            "er at objektene er merket, ikke hvordan et felt ble gjenkjent."
        ),
    )


class ForeslattGrammatikk(BaseModel):
    """En grammatikkinnstilling verktøyet mener bør slås av.

    Begge tallene følger med, og det er ikke pynt: ett tall alene kan ikke skille
    en fase fra en feil. «43 verdier løses» ser likt ut enten de to øvrige parser
    fint eller det er 40 av dem. 43 mot 2 er en modell uten byggnummer ennå;
    3 mot 40 er tre objekter merket feil.
    """

    model_config = {"frozen": True}

    innstilling: str = Field(description="Feltnavnet i `Grammatikk`, f.eks. krev_plassering")
    verdi: bool = Field(default=False, description="Verdien som foreslås")
    loser: int = Field(description="Verdier som parser når innstillingen slås av")
    parser_alt: int = Field(description="Verdier som allerede parser uten den")


class Oppsettforslag(BaseModel):
    """Alt verktøyet har grunnlag for å foreslå, som ren data.

    Skiller bevisst mellom «ingenting å foreslå» og «ingenting å bygge på».
    De to har motsatt betydning og ser like ut: en modell uten et eneste merket
    objekt gir samme tomme forslag som en modell der alt lå akkurat der det
    skulle. Det er samme lærdom `dekning` allerede bærer — to tall, ikke ett.
    """

    psett: dict[Verditype, list[Foreslatt]] = Field(
        default_factory=dict,
        description="Egenskapssett som bør legges til, per verditype",
    )
    feltnavn: dict[Verditype, list[Foreslatt]] = Field(
        default_factory=dict,
        description="Feltnavn som bør legges til, per verditype",
    )
    klasser: list[Foreslatt] = Field(
        default_factory=list,
        description="IFC-klasser utenfor omfanget som har TFM-merkede objekter",
    )
    grammatikk: list[ForeslattGrammatikk] = Field(
        default_factory=list,
        description="Grammatikkinnstillinger som får alle verdiene til å parse",
    )

    lest: int = Field(default=0, description="Objekter lest i alt")
    med_tfm: int = Field(default=0, description="Objekter med en TFM-forekomstverdi")
    kildefiler: list[str] = Field(default_factory=list)

    def har_noe(self) -> bool:
        """Om forslaget inneholder noe å ta stilling til."""
        return (
            bool(self.klasser)
            or bool(self.grammatikk)
            or any(self.psett.values())
            or any(self.feltnavn.values())
        )

    def fant_grunnlag(self) -> bool:
        """Om modellene i det hele tatt hadde TFM-verdier å utlede noe av.

        Et tomt forslag betyr én av to helt ulike ting, og uten dette skillet
        er tomheten et svar brukeren ikke kan bruke til noe.
        """
        return self.med_tfm > 0
