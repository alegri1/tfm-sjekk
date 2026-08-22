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
