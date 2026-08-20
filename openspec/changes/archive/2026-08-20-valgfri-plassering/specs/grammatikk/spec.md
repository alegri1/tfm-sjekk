## Purpose

Beskriver hvilke deler en TFM-ID må ha for å bli godtatt, hvilke av dem et
prosjekt kan gjøre valgfrie, og hva som identifiserer én komponent når en valgfri
del mangler.

De to henger uløselig sammen. Gjør man en del valgfri, endrer man samtidig hva
som skiller to komponenter fra hverandre — og en unikhetskontroll som ikke følger
med på det, melder enten duplikater som ikke finnes eller tier om dem som gjør.

## ADDED Requirements

### Requirement: Plassering skal kunne gjøres valgfri

Verktøyet SKAL kunne konfigureres til å godta en TFM-ID uten plasseringsdelen.
Standardverdien SKAL kreve plasseringen, slik at et eksisterende oppsett ikke
endrer oppførsel.

En tidlig modell har ikke alltid fått byggnummer, mens systemet og komponenten er
merket og skal kunne kontrolleres. Uten dette får hvert eneste objekt et
syntaksfunn om en del prosjektet ennå ikke har bestemt, og de ekte feilene
drukner.

#### Scenario: Tidligfase godtar ID uten plassering
- **WHEN** plassering er konfigurert som valgfri, og verdien er
  `=3600.001.04-JVZ001`
- **THEN** verdien godtas
- **AND** den gir ikke noe syntaksfunn

#### Scenario: Plassering godtas fortsatt når den er med
- **WHEN** plassering er valgfri, og verdien er `++115080=3600.001.04-JVZ001`
- **THEN** verdien godtas
- **AND** plasseringen leses som `115080`

#### Scenario: Standardoppsettet er uendret
- **WHEN** ingenting er konfigurert, og verdien er `=3600.001.04-JVZ001`
- **THEN** verdien avvises som før

#### Scenario: Ugyldig plassering avvises selv når delen er valgfri
- **WHEN** plassering er valgfri, og verdien er `++11508=3600.001.04-JVZ001` med
  fem siffer
- **THEN** verdien avvises
- **AND** meldingen navngir plasseringen

Valgfri betyr at delen kan utelates, ikke at den kan være feil.

### Requirement: De bærende delene skal ikke kunne gjøres valgfrie

Systemkoden, systemets løpenummer, undernummeret, komponentkoden og komponentens
løpenummer SKAL alltid kreves. Bare plasseringen og komponenttypen kan gjøres
valgfrie.

En TFM-ID uten system eller komponent er ikke en TFM-ID, og en konfigurasjon som
tillot det ville gjort oppsettsfila til et sted man kan skru seg ut av standarden
uten å merke det.

#### Scenario: Bare de perifere delene har en bryter
- **WHEN** konfigurasjonen leses
- **THEN** plasseringen og komponenttypen kan settes valgfrie
- **AND** ingen innstilling gjør systemkoden eller komponentkoden valgfri

### Requirement: Identiteten bygges av delene som finnes

Identiteten K6 måler unikhet på SKAL bygges av de delene TFM-ID-en faktisk har.
En ID med plassering og en uten SKAL ikke regnes som samme komponent.

To objekter kan ha samme system og komponent i hvert sitt bygg uten at noe er
galt. Ble plasseringen normalisert bort for alle, ville en federering på tvers av
bygg meldt duplikater som ikke finnes — og et falskt funn i en unikhetskontroll
er dyrere enn et uteblitt, fordi det lærer brukeren å overse kontrollen.

#### Scenario: Med og uten plassering er ulike komponenter
- **WHEN** ett objekt er merket `++115080=3600.001.04-JVZ001` og et annet
  `=3600.001.04-JVZ001`
- **THEN** de regnes ikke som duplikater av hverandre

#### Scenario: Duplikat uten plassering fanges fortsatt
- **WHEN** to objekter i ulike fagmodeller begge er merket `=3600.001.04-JVZ001`
- **THEN** K6 melder dem som duplikater
- **AND** meldingen navngir begge fagmodellene

#### Scenario: Ulikt bygg er ikke duplikat
- **WHEN** to objekter er merket `++115080=3600.001.04-JVZ001` og
  `++115081=3600.001.04-JVZ001`
- **THEN** de regnes ikke som duplikater

### Requirement: Meldingen skal ikke etterlyse en del som ikke kreves

Når en del er konfigurert som valgfri, SKAL ingen melding be brukeren om å legge
den til.

Forventningene kommer fra den konfigurerte grammatikken. En melding som etterlyste
plasseringen i et prosjekt som har bestemt at den ikke gjelder ennå, ville sendt
brukeren for å rette noe som ikke er feil.

#### Scenario: Valgfri del nevnes ikke
- **WHEN** plassering er valgfri, og verdien er `=3600.001.04-JVZ0001` der
  komponentens løpenummer har ett siffer for mye
- **THEN** meldingen navngir komponentens løpenummer
- **AND** den nevner ikke plasseringen

#### Scenario: Formmalen viser den grammatikken som gjelder
- **WHEN** plassering er valgfri, og verktøyet må falle tilbake på å oppgi den
  forventede formen
- **THEN** formen begynner med `=`, ikke med `++`

#### Scenario: Påkrevd del navngis som før
- **WHEN** plassering er påkrevd, og verdien er `=3600.001.04-JVZ001`
- **THEN** meldingen navngir plasseringen som den manglende delen

### Requirement: En ID uten plassering skal fortsatt kjennes igjen som en TFM-ID

Verktøyet SKAL kjenne igjen en verdi uten plasseringsdel som en TFM-ID, slik at
den kan godtas fra gjetningsveien og få en spesifikk feilmelding.

Gjenkjenningen og formkravet er to ulike dommer, og de må ikke gli fra hverandre:
en verdi grammatikken godtar, men gjenkjenningen forkaster, ville blitt lest som
fraværende av verdiuttrekket.

#### Scenario: Gjenkjennes uten plassering
- **WHEN** verdien er `=3600.001.04-JVZ001`
- **THEN** den regnes som gjenkjennelig som en TFM-ID

#### Scenario: Fremmed verdi er fortsatt fremmed
- **WHEN** verdien er `Systemair`
- **THEN** den regnes ikke som en TFM-ID, uansett hvilke deler som er valgfrie
