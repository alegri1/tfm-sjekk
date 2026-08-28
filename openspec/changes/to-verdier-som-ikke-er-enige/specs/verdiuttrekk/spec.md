## ADDED Requirements

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
