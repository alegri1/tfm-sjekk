## Purpose

Lar en hel kjøring beskrives ferdig i prosjektets oppsett — hvilke modeller som
leses, og hvor rapporten legges — slik at runden er én kommando uten argumenter.
Runden gjentas mange ganger mens en modell rettes, og hver gjentakelse skal ikke
kreve at eksporten finnes igjen for hånd.

## Requirements

### Requirement: Oppsettet kan peke på modellene som skal sjekkes

Oppsettet SKAL kunne oppgi hvilke IFC-filer en kjøring leser. Oppgis ingen filer
på kommandolinjen, SKAL verktøyet lese dem fra oppsettet.

Stiene SKAL løses mot oppsettfila, ikke mot arbeidskatalogen — samme regel som
for tabellene og mastera. Oppsettet hører til prosjektet og skal kunne sendes til
en kollega uten at det betyr noe hvor terminalen sto.

Filer oppgitt på kommandolinjen SKAL vinne over oppsettet. Det er samme regel som
for de andre stiene i oppsettet, og den lar en enkeltfil sjekkes uten å røre
prosjektets faste rute.

#### Scenario: Kjøring uten filargumenter leser modellene fra oppsettet
- **WHEN** `sjekk` kjøres uten filargumenter, og oppsettet oppgir modeller
- **THEN** de oppgitte modellene leses, og rapporten lages av dem

#### Scenario: Filargumenter vinner over oppsettet
- **WHEN** `sjekk` kjøres med filargumenter, og oppsettet også oppgir modeller
- **THEN** bare filene fra kommandolinjen leses

#### Scenario: Stiene løses mot oppsettfila
- **WHEN** oppsettet oppgir en relativ sti til en modell
- **THEN** stien tolkes fra mappa oppsettfila ligger i, uansett hvor kommandoen
  kjøres fra

### Requirement: En rute som ikke treffer noen modell er en feil

Oppgir oppsettet modeller, og ingen av dem finnes, SKAL verktøyet stoppe med en
feilmelding som navngir det som ble lett etter. Verktøyet SKAL IKKE lage en
rapport på null modeller.

En kjøring på null objekter gir en rapport uten funn, og den ser ut som en modell
uten feil. Det er samme tvetydighet som «ingen funn» kontra «ingenting sjekket»,
og en fast rute gjør den farligere: ruten er skrevet én gang og leses aldri igjen,
så en eksport som havnet et annet sted ville gitt grønt hver runde.

#### Scenario: Oppsettet peker på en modell som ikke finnes
- **WHEN** oppsettet oppgir en modellsti som ikke finnes på disk
- **THEN** kjøringen stopper med en feil som oppgir stien slik den sto i
  oppsettet og stien den ble løst til
- **AND** ingen rapport skrives

#### Scenario: Ingen modeller noe sted
- **WHEN** `sjekk` kjøres uten filargumenter, og oppsettet ikke oppgir modeller
- **THEN** kjøringen stopper med en melding om at det ikke er oppgitt noen modell
- **AND** ingen rapport skrives

### Requirement: Oppsettet kan peke på rapportmappa

Oppsettet SKAL kunne oppgi hvor rapportene legges. Oppgis `--ut` på
kommandolinjen, SKAL flagget vinne.

Rapportmappa er den andre halvdelen av den faste ruten: skriver hver runde til
samme sted, kan neste ledd — Dynamo-grafen som leser `funn.csv` — peke dit én
gang og aldri endres.

#### Scenario: Rapportmappa hentes fra oppsettet
- **WHEN** `sjekk` kjøres uten `--ut`, og oppsettet oppgir en rapportmappe
- **THEN** rapportene skrives dit

#### Scenario: Flagget vinner over oppsettet
- **WHEN** `sjekk` kjøres med `--ut`, og oppsettet også oppgir en rapportmappe
- **THEN** rapportene skrives der flagget peker
