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
    egenskapsnavn_type: list[str] = ["TFM", "TFMType", "Type"]
    egenskapsnavn_mmi: list[str] = ["MMI", "Prosesstatus"]


class KontrollOppsett(BaseModel):
    aktiv: bool = True
    alvorlighet: Alvorlighet | None = Field(
        default=None, description="Overstyrer kontrollens standardgrad"
    )


class Konfigurasjon(BaseModel):
    grammatikk: Grammatikk = Grammatikk()
    pset: PsetOppsett = PsetOppsett()

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

    def oppsett_for(self, kontroll_id: str) -> KontrollOppsett:
        return self.kontroller.get(kontroll_id, KontrollOppsett())

    @classmethod
    def les(cls, sti: Path | None) -> Konfigurasjon:
        """Leser TOML. Uten fil brukes standardverdiene over."""
        if sti is None:
            return cls()
        with sti.open("rb") as f:
            data = tomllib.load(f)
        return cls.model_validate(data)
