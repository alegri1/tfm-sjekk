## Why

En runde fra funn til rettet modell krever i dag sju stasjoner og seks
verktøybytter: Revit → IFC-eksport → filutforsker → tfm-sjekk → rapport →
Dynamo → schedule. Hypotesen fra RIE-siden er at det ikke passer inn i et
hektisk prosjekt, og rekonstruksjonen av sløyfen bekrefter at den er lang.

To av stasjonene er ikke nødvendige, og de koster mest:

**Engangsjobben ser ut som rundejobben.** «Bygg grafen, steg for steg» fyller
180 linjer i `dynamo/LES-MEG.md` og leses som om den hører til hver runde. Den
hører til én gang per prosjekt — og de to grafene er *allerede bygget og kjørt*
mot Snowdon i Revit 2027. De ligger på ett skrivebord og finnes ikke i repoet.
Neste bruker bygger dem opp igjen fra ti steg som ingen skulle trengt å gå.

**Filutforskeren er ren friksjon.** Hver runde må eksporten finnes igjen og
sendes til verktøyet for hånd, selv om den lander på samme sted hver gang.
`tfm-sjekk.toml` kan allerede peke på tabeller og master, men ikke på modellene
den skal lese eller mappa rapporten skal i.

## What Changes

- De to Dynamo-grafene legges i `dynamo/` som `.dyn`-filer, uten hardkodede
  stier og med det samme oppsettet i begge.
- En test knytter skriptkopien inne i hver `.dyn` til kildefila i repoet.
  Python-noden lagrer en **kopi**, ikke en peker, og kopien har allerede drevet:
  `tfm-sjekk-tfm-fra-revit.dyn` beskriver seg selv med en nodekobling repoet
  dokumenterer som feil. Ledningene er riktige, beskrivelsen er én generasjon
  gammel, og ingenting sier fra.
- `tfm-sjekk.toml` får to nye nøkler: `modeller` (hvilke IFC-filer som sjekkes)
  og `ut` (hvor rapporten legges).
- `tfm-sjekk sjekk` uten filargumenter leser `modeller` fra oppsettet i stedet
  for å avvise kallet. Med filargumenter er alt som før — flagget vinner over
  fila, samme regel som for `--master`.
- En sti i `modeller` som ikke treffer noen fil er en **feil**, ikke en tom
  kjøring. En kjøring på null modeller ser ut som en ren modell.
- `dynamo/LES-MEG.md` skiller de to sløyfene: engangsoppsett per prosjekt, og
  runden som gjentas.

## Capabilities

### New Capabilities
- `fastrute`: at en kjøring kan beskrives ferdig i `tfm-sjekk.toml` — hvilke
  modeller som leses og hvor rapporten havner — slik at runden er én kommando
  uten argumenter, og slik at et oppsett som ikke treffer noe sier fra i stedet
  for å levere en tom rapport.

### Modified Capabilities
- `oppsettfunn`: en oppsettfil som ikke lar seg lese skal gi en melding, ikke en
  Python-tilbakesporing — og en BOM skal ikke være en lesefeil. Funnet mens den
  faste ruten ble prøvd med den frosne binæren, og det gjelder v0.6.2 like mye.
  Tas med her fordi ruten gjør oppsettet til fila brukeren redigerer i hvert
  prosjekt, og Notisblokk skriver BOM.

  (De nye nøklene selv arver den eksisterende oppførselen for ukjente og
  feilplasserte nøkler uten at de kravene endres.)

## Impact

- `src/tfm_sjekk/config.py`: to felter på `Konfigurasjon`, og lesingen av TOML.
  Nøkkeloppslaget som gir forslag ved skrivefeil leser modellen selv, så de nye
  navnene kom med uten en linje kode.
- `src/tfm_sjekk/cli.py`: `modeller` blir valgfritt argument i `sjekk`, og `--ut`
  får samme «flagget vinner over fila»-regel som tabellstiene. `finn_oppsett([])`
  faller allerede tilbake til arbeidskatalogen, så oppsettet finnes uten at en
  modell peker det ut.
- `dynamo/`: to nye `.dyn`-filer. Ingen ny avhengighet — de leses som JSON.
- `tests/test_dynamo.py`, `tests/test_cli.py`, `tests/test_oppsettfunn.py`.
- `dynamo/LES-MEG.md` og `README.md`.
- Demomappa: `.cmd`-fila og `tfm-sjekk.toml` viser den korte ruten.

**Prøves hos konsumenten:** grafene må åpnes i Dynamo i Revit før de kan sies å
virke — en `.dyn` med gyldig JSON kan fortsatt ha en ledning som ikke fester
seg. Det er noe bare du kan se.
