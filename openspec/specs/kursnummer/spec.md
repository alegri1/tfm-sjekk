## Purpose

Beskriver når undernummeret i en TFM-ID skal leses som et kurs-/sløyfenummer, og
hvilke objekter kravet om et utfylt kursnummer ikke gjelder for.

To slags objekter er unntatt, og av samme grunn: fordelingen er roten kursene går
ut fra, og føringsveien er det som bærer dem. Ingen av dem ligger på en kurs.
Kravet om kursnummer gjelder det som *mates* av en kurs — lamper, stikk,
brytere, utstyr.

## Requirements

### Requirement: Kursnummer kreves av elektroobjekter

Verktøyet SKAL melde fra når et objekt i et NS 3451 kapittel 4- eller
5-system ikke har et utfylt undernummer.

For disse systemene er undernummeret kurs-/sløyfenummeret. Uten det kan ingen se
hvilken kurs et objekt hører til, og hele kursopplegget er umulig å ettergå fra
modellen.

#### Scenario: Lampe uten kursnummer
- **WHEN** et objekt i system `4320` har undernummeret `00`
- **THEN** det meldes som feil

#### Scenario: Lampe med kursnummer
- **WHEN** samme objekt har undernummeret `12`
- **THEN** det meldes ikke

#### Scenario: Andre fag er upåvirket
- **WHEN** et objekt i system `3600` har undernummeret `00`
- **THEN** det meldes ikke, for undernummeret betyr noe annet der

### Requirement: Objekter som ikke ligger på en kurs er unntatt

Kravet SKAL ikke gjelde objekter som bærer eller mater kurser framfor å ligge på
en. Det omfatter fordelinger og føringsveier.

Et kabelrør ligger ikke på en kurs — det fører dem. Å kreve kursnummer av det er
å stille et spørsmål som ikke har noe svar, og i en ekte modell er det den slags
objekter det er flest av: 850 av 1029 funn i en modell med 2439 objekter.

#### Scenario: Fordelingen er roten
- **WHEN** en fordeling er merket `=4310.001.00`
- **THEN** den meldes ikke

#### Scenario: Føringsvei bærer kurser
- **WHEN** et kabelrør er merket `=4360.001.00`
- **THEN** det meldes ikke

#### Scenario: Utstyr er ikke unntatt
- **WHEN** en lampe i samme system er merket `=4320.001.00`
- **THEN** den meldes som før

### Requirement: Hvilke klasser som er føringsvei skal være konfigurerbart

Verktøyet SKAL la prosjektet oppgi hvilke IFC-klasser som regnes som føringsvei,
og SKAL ha en standardliste som virker uten at noe konfigureres.

Første kjøring er der inntrykket dannes. En liste prosjektet må fylle ut før
rapporten blir lesbar, blir ikke fylt ut — den blir lagt bort sammen med
verktøyet.

#### Scenario: Standardlista dekker det vanlige
- **WHEN** ingenting er konfigurert, og modellen har `IfcFlowSegment` og
  `IfcFlowFitting` i et elektrosystem
- **THEN** de regnes som føringsvei

#### Scenario: Prosjektet utvider lista
- **WHEN** en klasse er lagt til i oppsettet
- **THEN** objekter av den klassen regnes som føringsvei

#### Scenario: Et klassenavn som ikke finnes i skjemaet er ufarlig
- **WHEN** lista inneholder en klasse som ikke finnes i IFC-skjemaet fila bruker
- **THEN** kjøringen fortsetter, og navnet treffer ingenting

### Requirement: Unntaket gjelder bare kravet om kursnummer

Et objekt som er unntatt fra kravet om kursnummer SKAL fortsatt inngå i de
øvrige elektrokontrollene.

Føringsveien er en del av kursopplegget selv om den ikke ligger på en kurs. Den
kobler utstyr til fordelinger, og en kontroll som utelot den ville mistet
sammenhengen den finnes for å se.

#### Scenario: Føringsvei teller fortsatt i koblingsgrafen
- **WHEN** en lampe er koblet til en fordeling gjennom et kabelrør
- **THEN** lampen regnes som matet fra den fordelingen

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
