#!/usr/bin/env bash
#
# Kjører et steg fra en GitHub-workflow lokalt, med de samme skallflaggene
# GitHub bruker.
#
#     verktoy/kjor-ci-steg.sh [workflow] [jobb] [stegnavn-prefiks]
#     verktoy/kjor-ci-steg.sh .github/workflows/bygg.yml binaer Røyktest
#
# Hvorfor dette finnes: «shell: bash» i en workflow kjører som
# «bash --noprofile --norc -eo pipefail». Under «set -e» river en tilordning
# fra en kommando som feiler hele steget, uten en eneste melding om hvorfor —
# og «tfm-sjekk sjekk» gir exit 1 hver gang den finner en feil. Røyktesten
# feilet på alle tre plattformer av nettopp den grunnen, mens de samme
# kommandoene kjørte fint i en vanlig terminal.
#
# Binæren erstattes med .venv-skriptet, så det er stegets logikk som prøves,
# ikke PyInstaller-bundelen. Vil du prøve den ekte binæren, bygg den først med
# «uv run pyinstaller tfm-sjekk.spec --noconfirm» og fjern kopieringa under.

set -euo pipefail

workflow="${1:-.github/workflows/bygg.yml}"
jobb="${2:-binaer}"
prefiks="${3:-Røyktest}"

rot="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$rot"

skript="$(mktemp -d)/steg.sh"

uv run --with pyyaml python - "$workflow" "$jobb" "$prefiks" "$skript" <<'PY'
import pathlib
import sys

import yaml

workflow, jobb, prefiks, ut = sys.argv[1:5]
d = yaml.safe_load(pathlib.Path(workflow).read_text(encoding="utf-8"))

steg = [s for s in d["jobs"][jobb]["steps"] if s.get("name", "").startswith(prefiks)]
if not steg:
    navn = [s.get("name") or s.get("uses") for s in d["jobs"][jobb]["steps"]]
    sys.exit(f"fant ikke et steg som begynner på «{prefiks}». Stegene er: {navn}")

s = steg[0]
if s.get("shell") != "bash":
    sys.exit(f"steget kjører med shell={s.get('shell')!r}, ikke bash — dette skriptet passer ikke")

# Matriseuttrykk finnes ikke lokalt. Bare filnavnet er i bruk i dag; treffer du
# flere, legg dem inn her framfor å la «${{ ... }}» stå og bli tolket som en
# skallvariabel.
innhold = s["run"].replace("${{ matrix.fil }}", "tfm-sjekk.exe")
if "${{" in innhold:
    sys.exit(f"steget har matriseuttrykk dette skriptet ikke kan sette inn: {innhold}")

# newline="\n": et CR i skriptet gjør at bash leter etter kommandoer med et
# usynlig vognretur-tegn på slutten.
pathlib.Path(ut).write_text(innhold, encoding="utf-8", newline="\n")
print(f"hentet ut «{s['name']}» fra {jobb}: {len(innhold.splitlines())} linjer")
PY

mkdir -p dist
cp .venv/Scripts/tfm-sjekk.exe dist/ 2>/dev/null || cp .venv/bin/tfm-sjekk dist/

echo "kjører med: bash --noprofile --norc -eo pipefail"
echo "---"
kode=0
bash --noprofile --norc -eo pipefail "$skript" || kode=$?
echo "---"
echo "steget avsluttet med $kode"
exit "$kode"
