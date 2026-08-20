"""Konfigurasjonsforslag utledet av det verktøyet faktisk fant.

Verktøyet vet allerede hvor hver TFM-verdi lå, og hvor sikkert det kunne vite
at det var riktig verdi — se `Verdikilde`. Den kunnskapen brukes i dag til å
forklare ett enkelt funn, og forsvinner så. Her samles den opp og blir til et
utkast til `tfm-sjekk.toml`.

Et forslag er ikke en beslutning. Verktøyet har gjettet seg fram til verdier,
og å skrive gjetningen inn i et oppsett gjør den til noe verktøyet stoler på
for alltid. Derfor følger beviset med — antall objekter og hvordan verdien ble
funnet — helt ut i fila som skrives.
"""

from __future__ import annotations

from tfm_sjekk.oppsett.modell import (
    Foreslatt,
    ForeslattGrammatikk,
    Oppsettforslag,
    Verditype,
)
from tfm_sjekk.oppsett.toml_ut import til_toml
from tfm_sjekk.oppsett.utled import utled

__all__ = [
    "Foreslatt",
    "ForeslattGrammatikk",
    "Oppsettforslag",
    "Verditype",
    "til_toml",
    "utled",
]
