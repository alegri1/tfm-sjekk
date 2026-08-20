## ADDED Requirements

### Requirement: Grammatikkinnstillinger skal kunne foreslås

Verktøyet SKAL foreslå det minste settet av grammatikkinnstillinger som får hver
eneste TFM-verdi som i dag ikke lar seg parse, til å parse. Finnes ikke et slikt
sett, SKAL ingenting foreslås.

Uttrekket kan være feilfritt mens grammatikken avviser alt. Da har verktøyet all
kunnskapen som trengs — det vet hvilke verdier som finnes og hvilken regel som
avviser dem — og å tie om det etterlater brukeren med feil uten anvisning.

#### Scenario: Tidligfase uten plassering
- **WHEN** hver verdi som ikke parser, gjør det bare fordi plasseringsdelen mangler
- **THEN** forslaget setter plassering som valgfri

#### Scenario: Blandede feil gir ingen anvisning
- **WHEN** noen verdier feiler fordi plasseringen mangler og andre fordi
  systemkoden har feil sifferantall
- **THEN** forslaget foreslår ingen grammatikkinnstilling

En innstilling som bare løser noen av feilene peker på merkefeil, ikke på fase.

#### Scenario: Innstillingen er allerede i bruk
- **WHEN** plassering allerede er konfigurert som valgfri
- **THEN** den foreslås ikke på nytt

#### Scenario: Ingen enkeltinnstilling er nok
- **WHEN** verdiene mangler både plassering og komponenttype, i et prosjekt som
  krever begge, og ingen av de to alene får dem til å parse
- **THEN** begge foreslås

#### Scenario: Det minste settet vinner
- **WHEN** én innstilling alene får alle verdiene til å parse
- **THEN** bare den foreslås
- **AND** ingen innstilling som ikke trengs blir med

### Requirement: Bare deler som kan gjøres valgfrie skal foreslås

Verktøyet SKAL bare foreslå innstillinger som gjør en del valgfri. Sifferantall og
andre formkrav SKAL aldri foreslås.

Å gjøre en del valgfri sier hvilken fase modellen er i. Den er reversibel, og delen
avvises fortsatt når den er med og feil. Å endre et sifferantall sier derimot hva
standarden er: en systematisk feilmerking ville blitt velsignet som konfigurasjon,
og verktøyet ville aldri meldt den igjen.

#### Scenario: Avvikende sifferantall foreslås ikke
- **WHEN** hver eneste plassering i modellen har sju siffer der seks er konfigurert
- **THEN** forslaget endrer ikke sifferantallet
- **AND** verdiene meldes fortsatt som avvik

### Requirement: Et grammatikkforslag skal bære belegget sitt

Et foreslått grammatikkvalg SKAL oppgi hvor mange verdier det løser, og hvor mange
som allerede parser uten det.

De to tallene sammen er det som skiller en fase fra en feil. 43 mot 2 er en modell
som ikke har fått byggnummer ennå; 3 mot 40 er tre objekter som er merket feil, og
da skal brukeren se det og forkaste forslaget.

#### Scenario: Begge tallene står i fila
- **WHEN** en innstilling foreslås på grunnlag av 43 verdier som feiler, mens 2
  parser som de skal
- **THEN** fila oppgir begge tallene

### Requirement: Et forslag med bare grammatikk er ikke tomt

Når verktøyet har en grammatikkinnstilling å foreslå, SKAL det ikke melde at det
ikke har noe å foreslå.

#### Scenario: Bare grammatikk å foreslå
- **WHEN** verdiene lå i konfigurert egenskapssett og felt, men ingen av dem parser
- **THEN** verktøyet melder ikke at oppsettet dekker modellene som de er
- **AND** forslaget inneholder grammatikkinnstillingen

### Requirement: Grammatikk skal skrives slik at den leses tilbake

Et forslag som inneholder både grammatikk og andre deler SKAL skrives slik at hver
verdi havner i den tabellen den hører til når fila leses.

TOML tilordner en nøkkel til den tabellen som står over den. En toppnivånøkkel
skrevet etter en tabelloverskrift havner inne i tabellen, fila er fortsatt gyldig,
og innstillingen forsvinner uten et ord. Det har allerede skjedd én gang her.

#### Scenario: Alle deler av et sammensatt forslag overlever
- **WHEN** forslaget inneholder både en grammatikkinnstilling, et egenskapssett og
  en klasse utenfor omfanget
- **THEN** alle tre er i kraft når fila leses som konfigurasjon

#### Scenario: Grammatikken tas i bruk
- **WHEN** et forslag med en grammatikkinnstilling brukes som konfigurasjon på
  samme modell
- **THEN** verdiene som før ikke parset, parser nå
- **AND** et nytt forslag har ingenting å foreslå
