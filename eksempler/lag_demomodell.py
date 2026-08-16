"""Lager en liten demomodell med tilsiktede feil.

    uv run python eksempler/lag_demomodell.py
    uv run tfm-sjekk eksempler/demo-rie.ifc eksempler/demo-riv.ifc \
        --systemtabell eksempler/FIKTIV-systemkoder.csv \
        --komponenttabell eksempler/FIKTIV-komponentkoder.csv \
        --master eksempler/FIKTIV-tfm-master.csv

Modellene inneholder kun oppdiktede verdier. Se eksempler/LES-MEG.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))

from fixtures.syntetisk import lag_modell

HER = Path(__file__).parent

RIE = [
    ("IfcFlowTerminal", "++115080=4310.001.12-QLF001"),  # ok
    ("IfcFlowTerminal", "++115080=4310.001.00-QLF002"),  # K8: kursnummer mangler (+ K7)
    ("IfcFlowTerminal", "++115080=9999.001.12-QLF003"),  # K3: ukjent systemkode (+ K7)
    ("IfcFlowTerminal", "++115080=2300.001.12-QLF004"),  # K4: overordnet kode
    ("IfcFlowTerminal", "++11508=4310.001.12-QLF005"),  # K2: for få siffer
    ("IfcFlowTerminal", None),  # K1: ingen TFM
]

RIV = [
    ("IfcFlowTerminal", "++115080=3600.001.04-JVZ001%JVZ.001.008"),  # ok
    ("IfcFlowTerminal", "++115080=4310.001.12-QLF001"),  # K6: duplikat av RIE
    ("IfcFlowTerminal", "++115080=3600.001.04-XXX009"),  # K5: ukjent komponentkode
]

if __name__ == "__main__":
    for navn, objekter in (("demo-rie.ifc", RIE), ("demo-riv.ifc", RIV)):
        sti = lag_modell(objekter, HER / navn)
        print(f"skrev {sti}")
