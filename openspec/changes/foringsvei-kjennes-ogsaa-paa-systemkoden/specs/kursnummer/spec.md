## ADDED Requirements

### Requirement: Hvilke systemkoder som er føringsvei skal kunne oppgis

Verktøyet SKAL la prosjektet oppgi hvilke systemkoder som regnes som føringsvei,
og et objekt med en slik systemkode SKAL være unntatt fra kravet om kursnummer
uansett hvilken IFC-klasse det har.

Klassen sier hva eksporten fikk til. Systemkoden sier hva prosjektet har bestemt
at objektet er. Når de to er uenige, er det prosjektet som har svart på
spørsmålet — verktøyet spør etter et kursnummer for et objekt som allerede er
merket som noe som bærer kurser.

Dette er samme slags avlesning som avgjør om kontrollen gjelder i det hele tatt:
systemkoden bestemmer allerede at objektet er elektro. Det nye er at den også
kan si at objektet er en føringsvei.

Standardlista SKAL være tom. Hvilken kode som betyr føringsvei står i NS 3451,
som er en betalt standard, og innholdet skal ikke ligge i verktøyet. Mekanismen
hører hjemme her; koden hører hjemme hos prosjektet.

#### Scenario: Ingenting konfigurert
- **WHEN** ingen systemkoder er oppgitt, og et objekt uten føringsvei-klasse er
  merket `=4360.001.00`
- **THEN** det meldes som før

#### Scenario: Systemkoden er oppgitt
- **WHEN** `4360` er oppgitt som føringsvei-systemkode, og et objekt uten
  føringsvei-klasse er merket `=4360.001.00`
- **THEN** det meldes ikke

#### Scenario: Bare den oppgitte koden er unntatt
- **WHEN** `4360` er oppgitt, og et objekt uten føringsvei-klasse er merket
  `=4320.001.00`
- **THEN** det meldes som før

### Requirement: De to måtene å kjenne igjen en føringsvei på virker ved siden av hverandre

Et objekt SKAL være unntatt fra kravet om kursnummer hvis IFC-klassen eller
systemkoden sier at det er en føringsvei.

To uavhengige kjennetegn er ikke et valg mellom to regler. En modell kan ha
kabelrør som kom riktig ut av eksporten og koblingsbokser som ikke gjorde det,
i samme fil — og et prosjekt som konfigurerer systemkoden skal ikke miste
standardlista over klasser.

#### Scenario: Klassen alene holder
- **WHEN** ingen systemkoder er oppgitt, og objektet er av en føringsvei-klasse
- **THEN** det meldes ikke

#### Scenario: Systemkoden alene holder
- **WHEN** objektet ikke er av en føringsvei-klasse, men systemkoden er oppgitt
- **THEN** det meldes ikke

#### Scenario: Ingen av delene
- **WHEN** objektet verken er av en føringsvei-klasse eller har en oppgitt
  systemkode, og undernummeret er tomt
- **THEN** det meldes
