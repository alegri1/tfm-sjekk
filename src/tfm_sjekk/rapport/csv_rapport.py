"""CSV-rapport — for videre analyse (§5)."""

from __future__ import annotations

import csv
from pathlib import Path

from tfm_sjekk.modell import Funn

KOLONNER = ["kontroll", "alvorlighet", "melding", "global_id", "ifc_klasse", "kildefil", "verdi"]


def skriv_csv(funn: list[Funn], sti: Path) -> Path:
    """Semikolon som skilletegn — norsk Excel forventer det."""
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("w", encoding="utf-8-sig", newline="") as f:
        skriver = csv.DictWriter(f, fieldnames=KOLONNER, delimiter=";")
        skriver.writeheader()
        for f_ in funn:
            rad = f_.model_dump(include=set(KOLONNER))
            rad["alvorlighet"] = f_.alvorlighet.value
            skriver.writerow(rad)
    return sti
