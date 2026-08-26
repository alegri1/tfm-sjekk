## Why

Dynamos Python-node lagrer skriptet som en **streng inne i `.dyn`-fila**. Den
leser ikke fra `dynamo/*.py`, og den vet ikke at kilden har endret seg. Kopien
har derfor drevet fra kilden tre ganger — alle tre 24.–25. august 2026:

    en graf manglet feltet «nokkel_fra», som kom inn dagen før.
        Alt i sammendraget så riktig ut, og tallene stemte

    fra-revit-grafen beskrev seg selv med en nodekobling repoet
        dokumenterte som feil. Ledningene var riktige

    demomappas kopi manglet VVS-tabellen. Grafen svarte
        «ingen av de 2590 familienavnene står i tabellen» — og
        familienavnet den viste STO i tabellen, i repoet

Den siste kostet en Dynamo-kjøring, en feilsøkingsrunde og en omkjøring.

`tests/test_dynamo.py` vokter `dynamo/*.dyn` mot `dynamo/*.py`. **Men den
kopien er ikke den som kjører.** Kjeden er fire ledd:

    dynamo/tfm_fra_revit.py          kilden
    dynamo/*.dyn                     kopi 1 — voktet av en test
    demomappa/*.dyn                  kopi 2 — bygget, kan være eldre
    noden i Dynamo hos brukeren      kopi 3 — INGEN test når hit

Det er kopi 3 som produserer merkingen, og den er usynlig for oss.

**Regelen «husk å lime inn på nytt» holder ikke.** Den står allerede i
`dynamo/LES-MEG.md` med tre eksempler, og den sviktet likevel tre ganger på to
dager — for den som skrev den.

## What Changes

- Skriptet bærer en **versjonsstreng**, og `OUT[1]` skriver den ut. En gammel
  kopi røper seg selv i sammendraget brukeren allerede leser før hun stoler på
  resultatet.
- Versjonen settes ett sted og følger med når `oppdater-grafene.py` limer inn,
  så den kan ikke bli uenig med skriptet den står i.
- En test knytter versjonsstrengen til pakkens versjon, slik at den ikke blir
  stående igjen når alt annet er oppdatert. Referansedata som driver fra det de
  beskriver er samme mønster én etasje ned.
- `verktoy/oppdater-grafene.py` oppdaterer også demomappas kopi når den finnes,
  så kopi 2 slutter å være et eget ledd å huske på.
- `dynamo/LES-MEG.md` sier hva brukeren skal se etter, og hva hun gjør når
  tallet er lavere enn ventet.

## Capabilities

Ingen. `tfm-sjekk` leser aldri disse skriptene — de kjøres i Dynamo, og
verktøyets oppførsel er uendret. `skip_specs: true`.

## Impact

- `dynamo/tfm_fra_revit.py` og `dynamo/tfm_til_revit.py`: versjonsstreng, og en
  linje i `sammendrag`.
- `verktoy/oppdater-grafene.py`: skriver versjonen inn, og tar demomappa.
- `verktoy/lag_demomappe.py`: kopierer allerede `.dyn`-filene; må ikke komme i
  konflikt med skriveren.
- `tests/test_dynamo.py`, `tests/test_merking.py`.
- `dynamo/LES-MEG.md` og `verktoy/demomappe-LES-MEG.mal.txt`.

**Prøves hos konsumenten:** en bevisst gammel kopi må limes inn i Dynamo og
kjøres, og sammendraget må avsløre den. En test kan bare vise at strengen
finnes — ikke at den er lesbar der den skal leses.
