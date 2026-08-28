"""Federering — les flere fagmodeller og slå dem sammen til én objektliste.

Her, og bare her, er parallellitet verdt det. Kontrollene er millisekunder
på ferdig uttrukket data; `ifcopenshell.open()` er sekunder til minutter per
fil. Én prosess per fil, og resultatet krysser prosessgrensen som ren data.
"""

from __future__ import annotations

import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.ifc.loader import ModellFeil, les_modell
from tfm_sjekk.modell import IfcObjekt


def les_modeller(
    stier: list[Path],
    config: Konfigurasjon | None = None,
    parallelt: bool = True,
) -> list[IfcObjekt]:
    """Leser alle filene og returnerer én samlet objektliste.

    Rekkefølgen følger `stier` uansett om lesingen er parallell — K6-funn
    må komme i samme rekkefølge hver kjøring (golden files, §7).
    """
    config = config or Konfigurasjon()

    if not parallelt or len(stier) < 2:
        return [o for sti in stier for o in les_modell(sti, config)]

    arbeidere = min(len(stier), os.cpu_count() or 1)
    with ProcessPoolExecutor(max_workers=arbeidere) as pool:
        resultater = pool.map(_les_en, [(sti, config) for sti in stier])
    return [o for gruppe in resultater for o in gruppe]


def _les_en(argument: tuple[Path, Konfigurasjon]) -> list[IfcObjekt]:
    """Toppnivåfunksjon — kreves for at pickle skal nå den i arbeiderprosessen."""
    sti, config = argument
    try:
        return les_modell(sti, config)
    except ModellFeil:
        # Bærer allerede stien; den skal ikke pakkes inn en gang til.
        raise
    except Exception as feil:
        # Stien legges på HER, i arbeideren. Utledet i hovedprosessen måtte den
        # kommet av rekkefølgen på resultatene fra `pool.map` — og den
        # rekkefølgen finnes ikke når kartet avbrytes av et unntak.
        raise ModellFeil(sti, f"lot seg ikke lese: {feil}") from feil
