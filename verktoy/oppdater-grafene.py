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

import argparse
import json
import re
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
DYNAMO = ROT / "dynamo"

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


PLASSHOLDER = 'VERSJON = "ukjent"'


def pakkeversjon() -> str:
    """Versjonen fra pyproject.toml.

    Pakkens versjon, ikke en egen teller. En egen teller ville krevd at noen
    husker å øke den — samme slags regel som allerede sviktet tre ganger.
    Denne endres uansett ved hver utgivelse, og brukeren ser den fra før i
    LES-MEG.txt og i BCF-forfatteren. Ett tall å sammenligne.
    """
    tekst = (ROT / "pyproject.toml").read_text(encoding="utf-8")
    treff = re.search(r'^version = "([^"]+)"', tekst, re.M)
    if treff is None:
        raise SystemExit("fant ingen «version» i pyproject.toml")
    return treff.group(1)


def med_versjon(skript: str, versjon: str, py: Path) -> str:
    """Setter versjonen på vei inn i .dyn-fila.

    Kilden beholder «ukjent». Da kan de to ikke bli uenige: kopien får
    versjonen sin i samme operasjon som skriptet, og det finnes ingen
    rekkefølge å huske.
    """
    if PLASSHOLDER not in skript:
        raise SystemExit(
            f"{py.name} har ingen «{PLASSHOLDER}» å sette versjonen i. En graf uten versjon er "
            "nettopp tilstanden dette skal fjerne."
        )
    return skript.replace(PLASSHOLDER, f'VERSJON = "{versjon}"', 1)


def oppdater(dyn: Path, py: Path, versjon: str) -> bool:
    graf = json.loads(dyn.read_text(encoding="utf-8"))
    node = python_noden(graf)
    skript = med_versjon(py.read_text(encoding="utf-8"), versjon, py)
    ny = linjeskift_som_i(node["Code"], skript)
    if node["Code"] == ny:
        return False
    node["Code"] = ny
    dyn.write_text(json.dumps(graf, ensure_ascii=False, indent=2), encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--demomappe",
        type=Path,
        help=(
            "Oppdater ogsaa .dyn-filene her. Demomappa er ikke i git, og dens "
            "kopi kan vaere eldre enn repoets mellom to utgivelser — det var "
            "nettopp den som bet 25. august."
        ),
    )
    args = ap.parse_args()

    versjon = pakkeversjon()
    endret = []
    for navn, kilde in PAR.items():
        py = DYNAMO / kilde
        if not py.is_file():
            raise SystemExit(f"finnes ikke: {py}")
        for mappe in [DYNAMO] + ([args.demomappe] if args.demomappe else []):
            dyn = mappe / navn
            if mappe is not DYNAMO and not dyn.is_file():
                # Mappa er ikke i git, og de fleste som klonet repoet har den
                # ikke. Fravaer er ikke en feil.
                continue
            if not dyn.is_file():
                raise SystemExit(f"finnes ikke: {dyn}")
            if oppdater(dyn, py, versjon):
                endret.append(f"{dyn} <- {kilde}")

    for linje in endret:
        print("  oppdatert:", linje)
    print(f"{len(endret)} fil(er) endret, versjon {versjon}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
