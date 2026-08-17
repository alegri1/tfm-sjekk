"""CSV-rapport — for videre analyse (§5).

Semikolon som skilletegn, fordi norsk Excel på skrivebordet bruker
listeskilletegnet fra regionsinnstillingene. Excel på web gjør ikke det: den
antar komma uansett, og da havner hele rapporten i kolonne A.

Derfor står det en `sep=;`-linje øverst. Den er en Excel-konvensjon, ikke en
del av CSV-standarden, men den er det eneste som får både skrivebords- og
webutgaven til å dele i kolonner ved dobbeltklikk. Skal fila leses av et
program i stedet, gir `--ren-csv` en fil uten linja.
"""

from __future__ import annotations

import csv
from pathlib import Path

from tfm_sjekk.modell import Funn

KOLONNER = ["kontroll", "alvorlighet", "melding", "global_id", "ifc_klasse", "kildefil", "verdi"]
SKILLETEGN = ";"


def skriv_csv(funn: list[Funn], sti: Path, sep_linje: bool = True) -> Path:
    """Skriver funnene som semikolonseparert CSV.

    `sep_linje=False` utelater `sep=;`-linja og gir en fil som `csv`-modulen,
    pandas og `Import-Csv` leser rett fram.
    """
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("w", encoding="utf-8-sig", newline="") as f:
        if sep_linje:
            # Må stå før overskriftsraden, og Excel vil ha den avsluttet med
            # vanlig linjeskift.
            f.write(f"sep={SKILLETEGN}\r\n")
        skriver = csv.DictWriter(f, fieldnames=KOLONNER, delimiter=SKILLETEGN)
        skriver.writeheader()
        for f_ in funn:
            rad = f_.model_dump(include=set(KOLONNER))
            rad["alvorlighet"] = f_.alvorlighet.value
            skriver.writerow(rad)
    return sti
