## 1. Skriptene bærer en versjon

- [x] 1.1 `VERSJON = "ukjent"` i `dynamo/tfm_fra_revit.py`, med en kommentar om
      at `oppdater-grafene.py` setter den på vei inn i `.dyn`-fila
- [x] 1.2 Samme i `dynamo/tfm_til_revit.py`
- [x] 1.3 `sammendrag` skriver «Skript <versjon>.» som egen linje
- [x] 1.4 Linja står i hver kjøring, også når alt er i orden — en linje som bare
      vises av og til blir ikke lest når den først dukker opp
- [x] 1.5 Test: linja finnes i sammendraget fra begge skriptene

## 2. Skriveren setter versjonen

- [x] 2.1 `oppdater-grafene.py` leser versjonen fra `pyproject.toml`
- [x] 2.2 Bytter `VERSJON = "ukjent"` til den, på vei inn i `.dyn`
- [x] 2.3 Finner den ikke plassholderen, stopper den og navngir fila. En graf
      uten versjon er den tilstanden vi prøver å fjerne
- [x] 2.4 Test: `.dyn`-filene bærer pakkens versjon, `.py`-filene «ukjent»
- [x] 2.5 Test: skriptkopien er ellers lik kilden — den eksisterende testen må
      justeres, siden versjonslinja nå skal skille seg

## 3. Demomappa slutter å være et eget ledd

- [x] 3.1 `oppdater-grafene.py` skriver også til demomappa når stien finnes,
      og sier hvilke filer den rørte
- [x] 3.2 Stien oppgis med et flagg, ikke hardkodet hjem til mitt skrivebord
- [x] 3.3 Mappa finnes ikke: ikke en feil. Den er ikke i git
- [x] 3.4 Sjekk at `lag_demomappe.py` og skriveren ikke kommer i konflikt —
      begge skriver `.dyn` til demomappa

## 4. Dokumentasjonen

- [x] 4.1 `dynamo/LES-MEG.md`: hva linja betyr, og hva man gjør når tallet er
      lavere enn utgivelsen man hentet
- [x] 4.2 Avsnittet «Grafen holder en kopi, ikke en peker» peker på den nye
      linja som måten å se det på — i dag sier det «tell feltene i OUT[1]»
- [x] 4.3 `verktoy/demomappe-LES-MEG.mal.txt`: samme, for den som ikke har repoet

## 5. Prøvd der det brukes

- [x] 5.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 5.2 Kjør `oppdater-grafene.py` og se at begge `.dyn` bærer riktig versjon
**ADVARSEL — grafen SKRIVER til modellen.** `Element.SetParameterByName` kjører
hver gang. Med en gammel kopi limt inn merkes alt med elektro-restkoden 4390
eller med ugyldige firesifrede løpenummer, og den lagrede merkingen er borte.
Prosjekteieren fanget dette; oppgaven sto opprinnelig uten advarselen.

- [x] 5.3 Prøvd av brukeren 2026-08-26: `VERSJON` redigert til «0.7.0» i noden,
      skrivenoden frakoblet, grafen kjørt. Sammendraget svarte «Skript 0.7.0.»
      Varselet leses der det skal, og ingen TFM-verdi ble rørt
- [ ] 5.4 **Til brukeren:** lim inn den ferske, se at tallet endrer seg, og
      koble skrivenoden tilbake
