## Purpose

Beskriver hvordan verktøyet finner TFM-forekomst, TFM-type og MMI i et objekts
egenskapssett, hvor sikkert det kan vite at det fant riktig verdi, og hva som skjer
når verdien ikke ligger der den var forventet. Uttrekket er inngangen til alle
kontrollene, så en verdi som leses feil her blir til et funn som er presist og
usant lenger ute.

## ADDED Requirements

### Requirement: Konfigurert egenskapssett og felt har forrang

Verktøyet SKAL lete etter verdien i de egenskapssettene og feltnavnene
konfigurasjonen oppgir, i den rekkefølgen de er oppgitt, før noen annen strategi
tas i bruk.

#### Scenario: Verdien ligger der den skal
- **WHEN** objektet har det konfigurerte egenskapssettet med det konfigurerte feltet
- **THEN** verdien leses derfra

#### Scenario: Flere konfigurerte navn
- **WHEN** flere egenskapssett i konfigurasjonen finnes på objektet
- **THEN** det første i konfigurasjonens rekkefølge vinner

### Requirement: Et gjenkjent feltnavn godtas i hvilket som helst egenskapssett

Verktøyet SKAL godta en verdi fra et egenskapssett med et annet navn enn det
konfigurerte, forutsatt at feltet har et av de konfigurerte feltnavnene. Norske
modeller legger ofte riktig verdi i et egenskapssett ingen forutså, og et
gjenkjent feltnavn er tilstrekkelig bevis for at verdien er den rette.

#### Scenario: Riktig felt i feil egenskapssett
- **WHEN** objektet mangler det konfigurerte egenskapssettet, men har et annet sett
  med et konfigurert feltnavn
- **THEN** verdien leses derfra

### Requirement: En verdi uten gjenkjent feltnavn må være gjenkjennelig

Når et egenskapssett har riktig navn, men ingen av de konfigurerte feltnavnene
finnes, SKAL verktøyet bare godta en verdi som er gjenkjennelig som det den utgir
seg for å være. En verdi som ikke er det SKAL behandles som fraværende.

Uten dette avgjøres utfallet av hvilken rekkefølge egenskapene tilfeldigvis har i
IFC-fila, og verktøyet rapporterer et syntaksavvik i en verdi som aldri var en
TFM-ID.

#### Scenario: Fremmed verdi forkastes
- **WHEN** egenskapssettet heter `TFM11_Forekomst`, mangler et konfigurert feltnavn,
  og første felt inneholder `Systemair`
- **THEN** objektet regnes som å mangle TFM-verdi
- **AND** rapporten sier at verdien mangler, ikke at den har feil syntaks

#### Scenario: Ødelagt TFM-ID godtas og flagges
- **WHEN** samme egenskapssett i stedet inneholder `++11508=3600.001.04-JVZ001`,
  som er gjenkjennelig som en TFM-ID med for få siffer
- **THEN** verdien tas i bruk
- **AND** rapporten melder syntaksavviket

#### Scenario: Rekkefølgen i fila endrer ingenting
- **WHEN** de samme feltene ligger i motsatt rekkefølge i egenskapssettet
- **THEN** verktøyet leser samme verdi som før

### Requirement: Feltnavn brukt til søk på tvers skal være distinkte

Et feltnavn som brukes til å lete på tvers av alle egenskapssett SKAL være distinkt
nok til at et treff er bevis for at verdien er den rette. Generiske navn som finnes
i standard egenskapssett SKAL ikke stå i standardkonfigurasjonen.

#### Scenario: Generisk feltnavn gir ikke treff
- **WHEN** objektet har `Pset_ManufacturerTypeInformation` med feltet `Type` satt til
  et fabrikatnavn, og ingen TFM-type noe sted
- **THEN** verktøyet rapporterer ingen TFM-type for objektet

### Requirement: Verktøyet skal gjøre rede for en usikker verdi

Verktøyet SKAL holde rede på hvordan hver verdi ble funnet — fra konfigurert
egenskapssett og felt, fra et gjenkjent feltnavn andre steder, eller forkastet — og
et funn som hviler på noe annet enn den konfigurerte veien SKAL si det i meldingen.

Meldingen skal peke på årsaken brukeren kan gjøre noe med: at feltet ikke ble funnet
der det var forventet.

#### Scenario: Funnet forklarer hvor verdien kom fra
- **WHEN** en verdi ble funnet gjennom et gjenkjent feltnavn i et annet
  egenskapssett enn det konfigurerte, og gir opphav til et funn
- **THEN** meldingen navngir egenskapssettet og feltet verdien faktisk ble lest fra

### Requirement: MMI tolkes bare når verdien er en nivåangivelse

Verktøyet SKAL tolke en MMI-verdi som et nivå bare når verdien er en
nivåangivelse. Vilkårlig tekst som inneholder siffer SKAL ikke bli til et nivå.

#### Scenario: Skrivemåter av samme nivå
- **WHEN** verdien er `MMI 300`, `mmi300` eller `300`
- **THEN** nivået er 300 i alle tre tilfellene

#### Scenario: Fritekst er ikke et nivå
- **WHEN** verdien er `sjekket av RIE 12.03`
- **THEN** den regnes ikke som et MMI-nivå
- **AND** den blir ikke til nivå `1203`

### Requirement: En forkastet verdi skal ikke påvirke slutninger om andre objekter

Slutninger som gjelder en hel fagmodell SKAL bygge bare på verdier verktøyet har
godtatt. En forkastet verdi SKAL ikke telle som at feltet er i bruk i fila.

Uten dette forurenser én feillest verdi ikke bare sitt eget objekt, men produserer
funn om objekter som ikke har noe med saken å gjøre.

#### Scenario: Ett bortkommet felt vipper ikke hele fila
- **WHEN** det eneste objektet med en MMI-lignende verdi i fila fikk den forkastet
- **THEN** fila regnes som å ikke bruke MMI
- **AND** de øvrige objektene får ingen funn om manglende MMI
