## ADDED Requirements

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
