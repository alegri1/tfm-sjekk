"""Prosjektets TFM-master (§3, K7).

SIMBA krever at prosjektet utarbeider en prosjektspesifikk TFM-master med
tverrfaglig systemliste, komponentliste, komponentforekomster og
komponenttyper. K7 sjekker modellen mot denne — begge veier.

STATUS: stubbet. Full innlesing er uke 5 (§9).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class TfmMaster(BaseModel):
    """Systemer og komponenttyper prosjektet har definert."""

    kilde: str
    systemer: set[str] = set()
    komponenttyper: set[str] = set()

    def kjenner_system(self, systemforekomst: str) -> bool:
        return systemforekomst in self.systemer

    def kjenner_type(self, komponenttype: str) -> bool:
        return komponenttype in self.komponenttyper


def les_master(sti: Path) -> TfmMaster:
    """Leser TFM-master fra XLSX eller CSV.

    TODO uke 5: arkfaner varierer mellom prosjekter, så arknavn og kolonner
    må inn i `tfm-sjekk.toml` på samme måte som pset-navnene. Skaff to-tre
    ekte mastere før formatet låses — ikke gjett.
    """
    raise NotImplementedError(
        "Innlesing av TFM-master er ikke implementert ennå (planlagt uke 5). "
        f"Kunne ikke lese {sti}."
    )
