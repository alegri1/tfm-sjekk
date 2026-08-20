## Purpose

Beskriver hvordan verktøyet utleder et konfigurasjonsforslag av det det faktisk
fant i modellene: hvilke observasjoner som kvalifiserer til å bli konfigurasjon,
hvilket belegg som kreves, hva som holdes utenfor, og hvordan forslaget gjør rede
for seg selv slik at et menneske kan overprøve det uten å kjøre verktøyet på nytt.

Et forslag er ikke en beslutning. Verktøyet har gjettet seg fram til verdier, og å
skrive gjetningen inn i et oppsett gjør den til noe verktøyet stoler på for alltid.
Derfor er beviset en del av leveransen, ikke en fotnote.

## Requirements

### Requirement: Forslaget skal utledes av observasjoner, ikke av standardverdier

Verktøyet SKAL bare foreslå verdier det har sett i modellene. En verdi som ikke er
observert SKAL ikke stå i forslaget, uansett hvor rimelig den måtte være.

Forslaget SKAL utelate alt som er likt standardverdiene. En fil som gjentar
standardverdiene fryser dem inn i prosjektet, og en senere retting i dem når da
aldri fram til prosjektet som trengte den.

#### Scenario: Modellen følger standardoppsettet
- **WHEN** alle TFM-verdier ble funnet i de konfigurerte egenskapssettene og feltene
- **THEN** forslaget inneholder ingen oppføringer om egenskapssett eller feltnavn

#### Scenario: Bare avviket skrives
- **WHEN** modellen krever ett egenskapssett utover standardverdiene, og ellers
  følger dem
- **THEN** forslaget inneholder den ene oppføringen
- **AND** det inneholder ikke grammatikk, MMI-skala eller andre uendrede deler

### Requirement: Hvordan verdien ble funnet avgjør hva som foreslås

Verktøyet SKAL utlede forslaget av hvor verdien lå i forhold til det konfigurerte
oppsettet:

- Verdien lå i konfigurert egenskapssett og felt: ingenting å foreslå.
- Verdien lå i et konfigurert felt i et ukonfigurert egenskapssett: egenskapssettet
  SKAL foreslås.
- Verdien lå i et konfigurert egenskapssett i et ukonfigurert felt: feltnavnet SKAL
  foreslås.

Forslaget skal lukke akkurat det hullet observasjonen avdekket, og ikke mer.

#### Scenario: Riktig felt i ukjent egenskapssett
- **WHEN** TFM-verdiene ble lest fra feltet `TFM` i et egenskapssett som heter `Data`
- **THEN** forslaget legger `Data` til blant egenskapssettene for forekomst
- **AND** det endrer ikke listen over feltnavn

#### Scenario: Ukjent felt i riktig egenskapssett
- **WHEN** TFM-verdiene ble lest fra feltet `Merking` i det konfigurerte
  egenskapssettet
- **THEN** forslaget legger `Merking` til blant feltnavnene for forekomst
- **AND** det endrer ikke listen over egenskapssett

#### Scenario: Verdien lå der den skulle
- **WHEN** alle verdier ble lest fra konfigurert egenskapssett og felt
- **THEN** forslaget foreslår verken egenskapssett eller feltnavn

### Requirement: En forkastet verdi skal aldri bli konfigurasjon

En verdi verktøyet forkastet fordi den ikke var gjenkjennelig som det feltet skal
inneholde, SKAL ikke gi opphav til et forslag.

En forkastelse er bevis for at verdien *ikke* hører hjemme der. Å foreslå feltet
ville gjøre en riktig avvisning til varig konfigurasjon, og verktøyet ville deretter
lese fabrikatnavn som TFM-ID-er uten å si fra.

#### Scenario: Fabrikatnavnet blir ikke et feltnavn
- **WHEN** det konfigurerte egenskapssettet har feltet `Fabrikat` med verdien
  `Systemair`, som ble forkastet
- **THEN** forslaget nevner ikke `Fabrikat`

### Requirement: En klasse foreslås til omfanget bare når objektene er merket

Verktøyet SKAL foreslå en IFC-klasse til omfanget bare når klassen ligger utenfor
det konfigurerte omfanget og objekter av den har en TFM-verdi.

At en klasse finnes i fila er ikke bevis for at den hører hjemme i omfanget — en
arkitektmodell er full av vegger ingen skal merke. At objektene *er* merket, er det:
noen har ment at de skulle ha TFM.

#### Scenario: Utstyr eksportert som proxy
- **WHEN** en fagmodell har objekter av `IfcBuildingElementProxy` med TFM-verdier,
  og klassen ligger utenfor omfanget
- **THEN** forslaget foreslår klassen lagt til i omfanget

#### Scenario: Umerkede klasser holdes utenfor
- **WHEN** samme modell i tillegg har hundrevis av `IfcWall` uten TFM-verdi
- **THEN** forslaget nevner ikke `IfcWall`

#### Scenario: Klassene er allerede i omfanget
- **WHEN** de merkede objektene ligger i klasser som allerede er i omfanget
- **THEN** forslaget inneholder ingen oppføring om omfanget

### Requirement: Hvert forslag skal bære sitt eget belegg

Hver foreslåtte verdi SKAL følges av hvor mange objekter den bygger på og hvordan
verdien ble funnet, i selve fila.

Et forslag skal kunne overprøves uten å kjøre verktøyet på nytt. Forskjellen mellom
et egenskapssett brukt på 840 objekter og ett brukt på 2 er hele forskjellen mellom
en prosjektkonvensjon og en tilfeldighet, og bare den som ser tallet kan avgjøre
hvilken av dem det er.

#### Scenario: Belegget står i fila
- **WHEN** et egenskapssett foreslås på grunnlag av 840 objekter der feltnavnet ble
  gjenkjent
- **THEN** fila oppgir antallet
- **AND** den oppgir at verdien ble funnet gjennom et gjenkjent feltnavn

#### Scenario: Svakt belegg er synlig som svakt
- **WHEN** et feltnavn foreslås på grunnlag av 2 gjettede objekter
- **THEN** fila oppgir begge deler, slik at forslaget kan forkastes ved lesing

### Requirement: Konfigurerte verdier skal beholde sin forrang

Foreslåtte verdier SKAL legges til etter de konfigurerte, aldri i stedet for dem og
aldri foran dem.

Rekkefølgen i konfigurasjonen er forrangen verdiuttrekket bruker. Et forslag som
satte en observert verdi først, ville gjøre en observasjon i én modell til
overstyring av prosjektets egen avtale i alle andre.

#### Scenario: Rekkefølgen bevares
- **WHEN** et egenskapssett foreslås i tillegg til de konfigurerte
- **THEN** de konfigurerte står først, i uendret innbyrdes rekkefølge
- **AND** det foreslåtte står etter dem

#### Scenario: Fagmodellene er uenige
- **WHEN** to fagmodeller bruker hvert sitt ukonfigurerte egenskapssett
- **THEN** begge foreslås
- **AND** det med flest objekter bak seg står først av de foreslåtte

### Requirement: Forslaget skal kunne leses tilbake av verktøyet

Et forslag verktøyet skriver SKAL være en gyldig konfigurasjon verktøyet kan lese.

En kjøring med forslaget som konfigurasjon SKAL gjøre de verdiene som lå til grunn
for det, til sikre verdier. Det er hele hensikten, og samtidig den eneste prøven som
viser at forslaget traff.

#### Scenario: Forslaget tas i bruk
- **WHEN** et forslag utledet av en modell brukes som konfigurasjon på samme modell
- **THEN** verdiene som før ble funnet gjennom et gjenkjent feltnavn eller en
  gjetning, er nå funnet gjennom konfigurert egenskapssett og felt

#### Scenario: Forslaget er stabilt
- **WHEN** verktøyet kjøres på nytt med sitt eget forslag som konfigurasjon
- **THEN** det nye forslaget har ingenting å foreslå

### Requirement: Et tomt forslag skal si hva tomheten betyr

Når verktøyet ikke har noe å foreslå, SKAL det si om det er fordi modellene fulgte
oppsettet, eller fordi det ikke fant noe å bygge på.

De to har motsatt betydning og ser like ut. En modell uten et eneste TFM-merket
objekt gir samme tomme forslag som en modell der alt lå akkurat der det skulle, og
uten å skille dem er tomheten et svar brukeren ikke kan bruke til noe.

#### Scenario: Alt lå der det skulle
- **WHEN** modellene ble lest, og alle verdier lå i konfigurerte egenskapssett og felt
- **THEN** verktøyet sier at oppsettet dekker modellene som de er

#### Scenario: Ingenting å bygge på
- **WHEN** modellene ble lest, og ingen objekter hadde TFM-verdier
- **THEN** verktøyet sier at det ikke fant TFM-verdier å utlede noe av
- **AND** det oppgir hvor mange objekter det leste

### Requirement: En eksisterende fil skal ikke overskrives utilsiktet

Verktøyet SKAL skrive forslaget til standard ut med mindre en fil er oppgitt, og
SKAL nekte å overskrive en fil som finnes uten at brukeren uttrykkelig har bedt om
det.

Fila forslaget er nærmest å hete er `tfm-sjekk.toml` — den samme fila prosjektet
allerede har lagt arbeid i.

#### Scenario: Uten filnavn
- **WHEN** kommandoen kjøres uten at en fil er oppgitt
- **THEN** forslaget skrives til standard ut

#### Scenario: Fila finnes fra før
- **WHEN** det oppgis en fil som allerede finnes
- **THEN** verktøyet skriver ikke over den
- **AND** det sier hva som må til for å gjøre det likevel

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
