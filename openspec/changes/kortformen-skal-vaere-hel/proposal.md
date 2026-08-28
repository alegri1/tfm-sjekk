## Why

To steder gir verktøyet en kortform av noe lengre, og begge kortformene mister
noe uten å si fra.

Et BCF-emne har en tittel på maks 100 tegn, og tittelen er alt en viewer viser i
emnelista. Er første setning i meldingen lengre enn grensen, kuttes den på tegn
nummer 99. I demokjøringen ga det tre emner som dette:

    K8: … men er merket med system…
    K9: … (fordeling: 200…
    K6: … på tvers av 2 filer (…

Ordet er halvert, og parentesen lukkes aldri. Meldingen er hel i «Description»,
så ingenting er tapt — men den som blar i emnelista leser en tittel som ser ut
som en ødelagt fil, ikke som en forkortet setning.

Oppsummeringslinja i konsollen har samme problem. Den sier «13 feil, 1
advarsler» etter en kjøring som la 17 funn i rapporten. De tre info-funnene
finnes i HTML-rapporten, i CSV-en, i XLSX-en og i BCF-en — bare ikke i linja
brukeren leser først. Den navngir også to av de fire filene den nettopp skrev.

Begge deler er samme feil: **kortformen later som den er hel.** En leser som
bare ser kortformen har ingen måte å vite at det finnes mer.

## What Changes

- BCF-titler som må kuttes, kuttes ved en **ordgrense** framfor midt i et ord,
  og avslutter ikke på et åpent skilletegn. Setningsgrensen som finnes i dag
  prøves fortsatt først; dette er fallback-en når det ikke finnes noen.
- Oppsummeringslinja i konsollen teller **alle alvorlighetsgradene** som finnes
  i rapporten, ikke bare feil og advarsler. En grad med null funn nevnes ikke.
- Entallsformen er riktig: «1 advarsel», ikke «1 advarsler».
- Linja navngir **hver fil kjøringen skrev**, ikke et utvalg.
- Stien skrives med plattformens eget skilletegn hele veien. I dag blander linja
  omvendt skråstrek fra stien med skråstrek limt på i formatstrengen.

Ingen kontroll endrer oppførsel, og ingen exit-kode endres.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `funnformat`: BCF-emnets tittel får et krav om hva som skjer når meldingen er
  lengre enn formatets grense. Formatet er en kontrakt, og i dag sier den
  ingenting om kutting.
- `dekning`: oppsummeringen av en kjøring får krav om at den teller alt den har
  funnet og navngir alt den har skrevet. Kapabiliteten handler allerede om at
  fravær av funn ikke skal være tvetydig; en grad som ikke telles er den samme
  tvetydigheten et hakk lenger ned.

## Impact

- `src/tfm_sjekk/rapport/bcf.py` — `_tittel`
- `src/tfm_sjekk/cli.py` — oppsummeringslinja i `sjekk`
- `tests/test_bcf.py`, `tests/test_cli.py`
- README-en beskriver konsollutdata flere steder og må følge med

Ingen avhengigheter, ingen nye filer, intet dataformat endres. CSV, XLSX og HTML
er urørt — de teller allerede alle tre gradene.
