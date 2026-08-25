## Purpose

Demomappa er det prosjektet leverer til noen som ikke har repoet — en RIE med en
minnepinne. Denne evnen sier at mappa er en **utdata**, ikke et sted man
redigerer, og at hvert tall i dokumentasjonen er målt av kjøringen som skrev det.
Uten det driver mappa fra det den beskriver, og det har den gjort hver gang den
er blitt vedlikeholdt for hånd.

## Requirements

### Requirement: Demomappa bygges av repoet

Alt i demomappa som finnes i repoet SKAL kopieres eller genereres av byggingen,
ikke vedlikeholdes i mappa. Etter en bygging SKAL hver slik fil være identisk med
kilden sin i repoet.

Femten av tjueto filer var byte-identiske kopier. En kopi som redigeres på ett av
to steder er ikke en kopi lenger, og ingenting sier fra: filene ser like ut, og
forskjellen ligger i en linje ingen leser.

#### Scenario: En kilde er endret i repoet
- **WHEN** en fil byggingen kopierer er endret i repoet, og demomappa bygges
- **THEN** fila i demomappa er lik den i repoet etterpå

#### Scenario: Noen har redigert en kopi i demomappa
- **WHEN** en kopiert fil er endret i demomappa, og mappa bygges på nytt
- **THEN** endringen overskrives av kilden i repoet

### Requirement: Tallene i dokumentasjonen måles av kjøringen

Hvert funntall, objekttall og dekningstall i demomappas `LES-MEG.txt` SKAL komme
fra en kommando byggingen faktisk kjørte. Tall SKAL IKKE skrives inn i malen.

Dette er kravet hele evnen finnes for. Et tall skrevet av et menneske er sant i
det øyeblikket det skrives og aldri etterpå; tre slike tall var gale samtidig i
august 2026, og ett av dem var skrevet en time før det ble oppdaget.

#### Scenario: En kontroll endrer hva en demomodell gir
- **WHEN** en endring i verktøyet gjør at en demomodell gir et annet funntall,
  og mappa bygges
- **THEN** tallet i `LES-MEG.txt` er det nye

#### Scenario: Malen inneholder ikke tall
- **WHEN** malen for `LES-MEG.txt` leses
- **THEN** hvert tall som beskriver et kjøringsresultat står som en plassholder
  byggingen fyller ut

### Requirement: Byggingen stopper framfor å levere noe den ikke kan stå inne for

Kan byggingen ikke fullføre et steg — en kilde som ikke finnes, en kommando som
feiler, en plassholder den ikke fikk målt — SKAL den stoppe med en melding som
navngir steget. Den SKAL IKKE levere en delvis bygget mappe.

En mappe som mangler én fil ser ut som en ferdig mappe. Det er samme tvetydighet
som «ingen funn» mot «ingenting sjekket», og her er den verre: mappa sendes til
noen som ikke kan se hva som skulle vært der.

#### Scenario: En kilde mangler
- **WHEN** en fil byggingen skal kopiere ikke finnes i repoet
- **THEN** byggingen stopper og navngir fila

#### Scenario: En dokumentert kommando feiler
- **WHEN** en kommando byggingen kjører for å måle et tall feiler uventet
- **THEN** byggingen stopper og navngir kommandoen

#### Scenario: En plassholder ble ikke fylt ut
- **WHEN** malen har en plassholder byggingen ikke fant en verdi til
- **THEN** byggingen stopper og navngir plassholderen
- **AND** `LES-MEG.txt` skrives ikke

### Requirement: Byggingen sier hvilken versjon mappa er

Demomappa SKAL oppgi hvilken utgivelse binæren er fra, og versjonen SKAL være den
samme i `LES-MEG.txt` som i binæren byggingen la der.

Mappa er ikke i versjonskontroll, og den er den eneste kilden mottakeren har.
Sier dokumentet én versjon og binæren en annen, er hvert tall i dokumentet
ubekreftet — og en BCF laget av en eldre utgave kan se helt riktig ut.

#### Scenario: Versjonen står begge steder
- **WHEN** mappa er bygget fra en utgivelse
- **THEN** `LES-MEG.txt` oppgir den versjonen
- **AND** binæren i mappa svarer med den samme

### Requirement: Filer som ikke kan bygges røres ikke

Filer som er resultatet av en kjøring gjennom Revit SKAL bevares slik de ligger.
Byggingen SKAL IKKE slette eller skrive over dem, og den SKAL stoppe om en av dem
mangler.

De kan ikke gjenskapes av et skript — de krever Revit, en modell og et menneske.
En bygging som ryddet mappa ville tatt med seg det eneste i den som ikke lot seg
lage på nytt.

#### Scenario: En Revit-avledet fil ligger der
- **WHEN** mappa bygges
- **THEN** filene fra Revit-runden er uendret etterpå

#### Scenario: En Revit-avledet fil mangler
- **WHEN** en av dem ikke finnes når mappa bygges
- **THEN** byggingen stopper og navngir fila
