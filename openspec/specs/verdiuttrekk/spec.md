## Purpose

Beskriver hvordan verktøyet finner TFM-forekomst, TFM-type og MMI i et objekts
egenskapssett, hvor sikkert det kan vite at det fant riktig verdi, og hva det har
lov til å påstå om den. Uttrekket er inngangen til alle kontrollene, så en verdi
som leses feil her blir til et funn som er presist og usant lenger ute.

Det samme skjønnet — ligner denne strengen i det hele tatt på en TFM-ID? — brukes
to steder: som port for en verdi verktøyet har gjettet seg til, og som valg av
hvor spesifikk en feilmelding kan være. Det er én dom, brukt to ganger.

## Requirements

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

### Requirement: Meldingens presisjon skal svare til hva verktøyet vet

Når verktøyet melder om en verdi som ikke følger grammatikken, SKAL meldingen
gjenspeile hvor mye det faktisk kan avgjøre. En verdi som ikke er gjenkjennelig som
en TFM-ID SKAL ikke beskrives som om den mangler en bestemt del av grammatikken.

Kravet gjelder uansett hvordan verdien ble funnet, også når den sto i det
konfigurerte egenskapssettet og feltet. En mal som legger fabrikatnavnet i
TFM-feltet gir i dag «Mangler «++»-delen: plassering (6 siffer)» — en presis
anvisning om et felt som aldri inneholdt en TFM-ID.

Presisjonen har tre trinn, og verktøyet SKAL bruke det høyeste det har grunnlag
for:

1. Verdien er ikke gjenkjennelig som en TFM-ID — meldingen sier nettopp det.
2. Verdien mangler en strukturmarkør — meldingen navngir delen som mangler.
3. Alle delene finnes, men innholdet i én av dem bryter grammatikken — meldingen
   SKAL navngi den delen og oppgi både det forventede og det som faktisk står der.

Har verdien flere avvik, SKAL meldingen omtale det første. Forventningene SKAL
komme fra den konfigurerte grammatikken, slik at de ikke kan komme i utakt med
regelen som faktisk avviser verdien.

#### Scenario: Fremmed verdi beskrives som fremmed
- **WHEN** verdien i det konfigurerte feltet er `Systemair`
- **THEN** meldingen sier at verdien ikke ser ut som en TFM-ID
- **AND** den navngir ikke en bestemt manglende del av grammatikken

#### Scenario: Nesten-treff får spesifikk anvisning
- **WHEN** verdien er `++115080-3600.001.04`, altså gjenkjennelig som en TFM-ID der
  bare `=`-delen mangler
- **THEN** meldingen navngir den manglende delen

#### Scenario: Samme verdi gir samme dom begge veier
- **WHEN** en verdi vurderes som gjenkjennelig nok til å godtas fra gjetningsveien
- **THEN** den er også gjenkjennelig nok til å få en spesifikk feilmelding, og motsatt

#### Scenario: Feil sifferantall navngis med forventet og funnet
- **WHEN** verdien er `++11508=3600.001.04-JVZ001`, der plasseringen har fem siffer
- **THEN** meldingen navngir plasseringen
- **AND** den oppgir både forventet antall og antallet som faktisk står der

#### Scenario: Hver del av grammatikken kan navngis
- **WHEN** avviket ligger i systemkoden, systemets løpenummer, undernummeret,
  komponentkoden, komponentens løpenummer eller komponenttypen
- **THEN** meldingen navngir den delen avviket ligger i
- **AND** to verdier med avvik i ulike deler gir ulike meldinger

#### Scenario: Komponentkoden krever store bokstaver
- **WHEN** verdien er `++115080=3600.001.04-jvz001`, der komponentkoden er skrevet
  med små bokstaver
- **THEN** meldingen sier at komponentkoden skal være store bokstaver

#### Scenario: Flere avvik gir det første
- **WHEN** verdien har avvik i både plasseringen og komponentkoden
- **THEN** meldingen omtaler avviket i plasseringen
- **AND** den lister ikke opp begge

#### Scenario: Forventningen følger konfigurasjonen
- **WHEN** grammatikken er konfigurert med et annet antall siffer i plasseringen enn
  standardverdien
- **THEN** meldingen oppgir det konfigurerte antallet

#### Scenario: Generisk melding som siste utvei
- **WHEN** verdien er gjenkjennelig som en TFM-ID, men verktøyet ikke kan peke på
  én bestemt del som svikter
- **THEN** meldingen oppgir den forventede formen

### Requirement: Egenskapssett på typeobjektet skal leses

Verktøyet SKAL lete etter verdier i egenskapssettene på objektets typeobjekt, i
tillegg til objektets egne.

En Revit-familietype kan bære merkingen som typeparameter, og for komponenttypen
er det det naturlige stedet: alle forekomstene av en familietype *er* samme
komponenttype. Å gjenta verdien på hver av dem er duplisering, og et
eksportoppsett kan derfor merke på typen med full rett.

Uten dette ser verktøyet ingenting og melder at hvert eneste objekt mangler TFM.
Det er den verste slags feil: rapporten ser ut som en modell uten merking, ikke
som et verktøy som ikke leste etter.

Koblingen heter forskjellige ting i de to skjemaene. Begge SKAL følges.

#### Scenario: Verdien ligger bare på typen
- **WHEN** et objekt uten egne egenskapssett har en type med TFM-verdi
- **THEN** verdien leses

#### Scenario: Begge skjemaene
- **WHEN** modellen er IFC4, og når den er IFC 2x3
- **THEN** typekoblingen følges i begge

#### Scenario: Objektet har ingen type
- **WHEN** et objekt ikke er knyttet til noe typeobjekt
- **THEN** uttrekket virker som før

#### Scenario: Typen har ingen egenskapssett
- **WHEN** typeobjektet finnes, men bærer ingen egenskapssett
- **THEN** uttrekket virker som før

### Requirement: Forekomstens egen verdi skal vinne over typens

Finnes den samme opplysningen både på objektet og på typen, SKAL objektets egen
verdi brukes.

Det er hva et typeobjekt er i IFC: et utgangspunkt en forekomst kan overstyre.
Den som har skrevet en verdi på selve objektet, har gjort det for å si noe om
nettopp det objektet.

Forrangen mellom konfigurert egenskapssett, gjenkjent feltnavn og gjetning
gjelder uendret. Den gjelder nå bare på to steder, og typens verdier stiller
sist når forekomsten har noe å si.

#### Scenario: Begge har verdien
- **WHEN** både objektet og typen bærer en TFM-verdi
- **THEN** objektets verdi brukes

#### Scenario: Bare typen har den
- **WHEN** objektet ikke bærer verdien, men typen gjør det
- **THEN** typens verdi brukes

#### Scenario: Kilden skal fortsatt kunne leses
- **WHEN** en verdi er lest fra et egenskapssett
- **THEN** verktøyet oppgir hvilket egenskapssett og hvilket felt den kom fra

### Requirement: Utvalget skal ikke avhenge av rekkefølgen i fila

Finnes flere kandidatverdier på samme styrkenivå, SKAL valget mellom dem være
uavhengig av hvilken rekkefølge egenskapssettene har i IFC-fila.

To eksporter av samme modell kan legge egenskapssettene i ulik rekkefølge. Gjør
rekkefølgen utslaget, gir samme modell ulikt svar fra én kjøring til den neste,
og et funn kan forsvinne eller dukke opp uten at noe i modellen er endret.

Det er samme resonnement evnen allerede gjør for felter innen ett egenskapssett,
anvendt på tvers av sett.

#### Scenario: Samme modell med ombyttet rekkefølge
- **WHEN** to filer har samme objekt med samme to kandidatverdier, men
  egenskapssettene i motsatt rekkefølge
- **THEN** leses den samme verdien i begge

### Requirement: Kandidater som ikke er enige skal meldes

Har et objekt flere kandidatverdier for samme felt, og de er ikke like, SKAL
verktøyet melde det. Meldingen SKAL oppgi begge verdiene og hvilke
egenskapssett de sto i.

Verktøyet velger én av dem for å kunne kontrollere noe. Men valget er ikke et
svar på hvilken som er den rette — det vet bare den som merket modellen. Den
andre verdien blir stående i fila, og et annet verktøy kan lese den.

Uten meldingen validerer rapporten den ene verdien mens den andre er usynlig, og
rapporten ser like ren ut som om det bare fantes én.

#### Scenario: To ulike verdier i to egenskapssett
- **WHEN** et objekt har ulike verdier for samme felt i to egenskapssett
- **THEN** meldes det, med begge verdiene og begge egenskapssettene

#### Scenario: Verktøyet kontrollerer likevel
- **WHEN** to kandidater er uenige
- **THEN** velges én, og de øvrige kontrollene kjører på den som før

### Requirement: Like verdier i flere egenskapssett skal ikke meldes

Er kandidatene like, SKAL det ikke meldes.

Den samme TFM-en i to egenskapssett er normalt etter en runde gjennom Revit:
kartleggingsfila skriver den ene, og importen kan legge igjen den andre. En
melding om det ville stått på hvert eneste objekt i en slik modell, og en melding
som alltid står der leses ikke.

#### Scenario: Samme verdi to steder
- **WHEN** et objekt har samme verdi for samme felt i to egenskapssett
- **THEN** meldes det ikke
