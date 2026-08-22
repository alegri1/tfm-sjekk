"""CSV-rapport — for videre analyse (§5).

Semikolonseparert UTF-8 med BOM, og ingenting mer. Fila er ment for
programmer: `csv`-modulen, pandas og `Import-Csv` leser den rett fram.

Her sto det en stund en `sep=;`-linje for å få Excel på web til å dele i
kolonner. Den virket — men den satte samtidig Excel på en parse-vei som
ignorerer BOM-en, så «følger» ble til «fÃ¸lger». Innenfor én CSV kan Excel
gi riktige tegn eller riktige kolonner, ikke begge. Derfor er Excel-jobben
flyttet til `xlsx.py`, som ikke trenger å gjette på noen av delene.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tfm_sjekk.modell import Funn

# «tfm» står før «verdi»: objektets identitet ved siden av de andre
# identitetsfeltene, ikke i den andre enden av raden. De to er like for de
# fleste funn — se beskrivelsene i `Funn`.
KOLONNER = [
    "kontroll",
    "alvorlighet",
    "melding",
    "global_id",
    "ifc_klasse",
    "kildefil",
    "tfm",
    "verdi",
]
SKILLETEGN = ";"


def skriv_csv(funn: list[Funn], sti: Path) -> Path:
    """Skriver funnene som semikolonseparert CSV i UTF-8 med BOM."""
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("w", encoding="utf-8-sig", newline="") as f:
        skriver = csv.DictWriter(f, fieldnames=KOLONNER, delimiter=SKILLETEGN)
        skriver.writeheader()
        for f_ in funn:
            rad = f_.model_dump(include=set(KOLONNER))
            rad["alvorlighet"] = f_.alvorlighet.value
            skriver.writerow(rad)
    return sti
