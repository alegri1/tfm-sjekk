## Why

Demomappa på skrivebordet ser ut som en samling innhold. Den er det ikke:

    22 filer
    15  byte-identiske kopier av filer i repoet
     7  unike — og fire av dem er binærfiler på til sammen 110 MB
     3  ekte unikater: eksport.ifc, LES-MEG.txt, kjor.cmd

Den er med andre ord en **byggeartefakt som vedlikeholdes for hånd**, og det er
derfor den driver. Tre drifter ble funnet i én runde 24. august:

- avsnittet ba deg finne stien `rapport-2x3\funn.csv` i Dynamo-grafen. Den stien
  fantes ikke i fila — grafen hadde en annen
- `tidligfase.toml` var beskrevet og lå ikke i mappa
- «4 funn» for `foringsvei.ifc` var målt med tabellene i oppsettet. Uten dem er
  det 2. Tallet var skrevet en time tidligere, av meg

Ingen av dem kunne en test fange. Alle tre ble funnet ved å kjøre kommandoene i
dokumentet og sammenligne med tallene dokumentet lover — for hånd.

Det er tolvte gang i dette prosjektet at referansedata driver fra det de
beskriver. Mønsteret er alltid det samme: to steder sier det samme, og bare det
ene blir oppdatert.

## What Changes

- `verktoy/lag_demomappe.py` bygger hele mappa fra repoet: modellene genereres,
  tabellene, grafene og oppsettfragmentene kopieres, binæren hentes fra en
  utgivelse, og rapporten lages ved å kjøre verktøyet.
- **Tallene i `LES-MEG.txt` måles, ikke skrives.** Hver kommando dokumentet viser
  kjøres, og tallet som havner i teksten er det kjøringen ga. Et dokument som
  lover noe annet enn kommandoen gir, kan ikke lenger oppstå.
- Byggingen sier fra om alt den ikke kan svare på: en fil den ikke fant, en
  kommando som feilet, et tall den ikke fikk målt.
- Filer som ikke kan bygges — `Snowdon Towers Sample Electrical.rvt`,
  `snowdon-tfm.ifc`, `snowdon-eksport.ifc`, `eksport.ifc` — beholdes der de
  ligger og røres ikke. De er resultatet av kjøringer gjennom Revit som ikke lar
  seg gjenta i et skript.
- Malen for `LES-MEG.txt` legges i repoet, der den kan leses i en diff.

## Capabilities

### New Capabilities
- `demomappe`: at demomappa er en utdata og ikke et sted man redigerer — at den
  bygges av repoet, at hvert tall i dokumentasjonen er målt av kjøringen som
  skrev det, og at byggingen stopper framfor å levere en mappe den ikke kan stå
  inne for.

### Modified Capabilities

(ingen — verktøyets egen oppførsel er uendret.)

## Impact

- Nytt: `verktoy/lag_demomappe.py` og en mal for `LES-MEG.txt`.
- `verktoy/` har fra før `legg_til_tfm.py`, `oppdater-grafene.py` og
  `kjor-ci-steg.sh`. Dette er den samme slags fil: noe man kjører, ikke noe som
  pakkes.
- `eksempler/lag_demomodell.py` kalles av den nye, ikke endret.
- `dynamo/*.dyn` og `eksempler/*.toml` blir kilder byggingen kopierer fra.
- Ingen ny avhengighet. Binæren hentes med `gh`, som allerede brukes.
- Tester i `tests/`, mot en bygget mappe i `tmp_path`.

**Prøves hos konsumenten:** bygget må kjøres mot den ekte mappa, og resultatet må
åpnes — `LES-MEG.txt` i Notisblokk, `kjor.cmd` ved dobbeltklikk, BCF-en i en
viewer. En mappe som ble bygget uten feilmelding er ikke det samme som en mappe
som virker.
