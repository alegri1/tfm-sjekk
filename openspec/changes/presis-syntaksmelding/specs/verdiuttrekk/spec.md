## MODIFIED Requirements

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
