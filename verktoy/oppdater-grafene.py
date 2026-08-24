"""Limer skriptene i dynamo/ inn i Python-nodene i .dyn-filene ved siden av.

Dynamos Python-node lagrer skriptet som en **streng inne i .dyn-fila**. Den
leser ikke fra dynamo/*.py, og den vet ikke at fila har endret seg. To filer
beskriver derfor det samme, og de kan drive fra hverandre — det har allerede
skjedd: en graf beskrev seg selv med en nodekobling repoet dokumenterte som
feil, mens ledningene var riktige. Ingenting sa fra.

Ansvaret er delt: `.py`-fila er fasit for skriptet, `.dyn`-fila for ledningene.
Denne skriveren og `tests/test_dynamo.py` er samme regel sett fra to sider —
skriveren limer inn, testen sier fra når noen glemte å kjøre den.

    uv run python verktoy/oppdater-grafene.py

Skriver bare filer som faktisk er ulike, så en kjøring uten endringer lar
tidsstemplene være i fred.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DYNAMO = Path(__file__).resolve().parent.parent / "dynamo"

# Grafen og skriptet den bærer en kopi av.
PAR = {
    "tfm-sjekk-tfm-fra-revit.dyn": "tfm_fra_revit.py",
    "tfm-sjekk-tfm-til-revit.dyn": "tfm_til_revit.py",
}


def python_noden(graf: dict) -> dict:
    """Den ene Python-noden i grafen.

    Kaster ved null eller flere. En graf med to Python-noder ville fått
    skriptet limt inn i en vilkårlig av dem, og det er en gjetning forkledd
    som et svar.
    """
    noder = [n for n in graf["Nodes"] if n.get("NodeType") == "PythonScriptNode"]
    if len(noder) != 1:
        raise SystemExit(f"venter én Python-node, fant {len(noder)}")
    return noder[0]


def linjeskift_som_i(mal: str, tekst: str) -> str:
    """Skriptet skrives med de linjeskiftene grafen allerede bruker."""
    return tekst.replace("\r\n", "\n").replace("\n", "\r\n" if "\r\n" in mal else "\n")


def oppdater(dyn: Path, py: Path) -> bool:
    graf = json.loads(dyn.read_text(encoding="utf-8"))
    node = python_noden(graf)
    ny = linjeskift_som_i(node["Code"], py.read_text(encoding="utf-8"))
    if node["Code"] == ny:
        return False
    node["Code"] = ny
    dyn.write_text(json.dumps(graf, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main() -> int:
    endret = []
    for navn, kilde in PAR.items():
        dyn, py = DYNAMO / navn, DYNAMO / kilde
        for sti in (dyn, py):
            if not sti.is_file():
                raise SystemExit(f"finnes ikke: {sti}")
        if oppdater(dyn, py):
            endret.append(f"{navn} <- {kilde}")

    for linje in endret:
        print("  oppdatert:", linje)
    print(f"{len(endret)} av {len(PAR)} grafer endret")
    return 0


if __name__ == "__main__":
    sys.exit(main())
