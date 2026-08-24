## Purpose

Beskriver hva et BCF-emne garanterer om synsvinkelen det gjenoppretter: at det
finnes et kamera, at det peker på objektet funnet gjelder, og at det står i den
enheten formatet krever.

Et utvalg alene er ikke nok. En viewer gjenoppretter en synsvinkel, og uten
kamera svarer den at emnet ikke har noe å zoome til — utvalget blir aldri brukt.
Med et kamera i feil enhet er det verre: da flytter den seg dit den blir bedt om,
og modellen forsvinner ut av bildet uten at noe sier hvorfor.

## ADDED Requirements

### Requirement: Kameraet skal stå i den enheten formatet krever

Koordinatene i et BCF-viewpoint SKAL være i meter, uavhengig av hvilken
lengdeenhet modellen er tegnet i.

En modell kan være i fot. Skrives koordinatene rått, tolker vieweren dem som
meter og flytter kameraet dit — for en amerikansk modell med byggeplass-
koordinater ble avstanden 969 kilometer, og modellen forsvant ut av synsfeltet.

Dette er en av feilene et skjema ikke fanger. Fila er gyldig BCF, emnet har et
kamera, og alt ser riktig ut helt til noen åpner det.

#### Scenario: Modellen er i meter
- **WHEN** modellen bruker meter som lengdeenhet
- **THEN** kameraets koordinater er objektets koordinater

#### Scenario: Modellen er i en annen enhet
- **WHEN** modellen bruker fot som lengdeenhet
- **THEN** kameraets koordinater er regnet om til meter

#### Scenario: Modellen oppgir ingen enhet
- **WHEN** modellen mangler en lengdeenhet
- **THEN** koordinatene leses som meter
- **AND** kjøringen fortsetter

### Requirement: Kameraet skal stå i nærheten av objektet

Kameraet SKAL stå så nær objektet at objektet er i synsfeltet, målt i meter og
ikke i modellens egen enhet.

Avstanden er valgt for et menneske: langt nok unna til at naboobjektene er med,
høyt nok til å se hva som står rundt. Den avstanden betyr det samme i alle
modeller bare hvis den er i en fast enhet — i en fot-modell ville «åtte» blitt
to og en halv meter.

#### Scenario: Avstanden er den samme i to modeller med ulik enhet
- **WHEN** det samme objektet finnes i en modell i meter og en i fot
- **THEN** kameraet står like langt fra objektet i begge

#### Scenario: Objektet er i synsfeltet
- **WHEN** et emne åpnes for et objekt med kjent posisjon
- **THEN** kameraet står innenfor noen titalls meter fra objektet

### Requirement: Et emne uten kjent posisjon skal fortsatt kunne åpnes

Kan ikke posisjonen fastslås, SKAL emnet skrives uten kamera framfor med et
kamera som peker feil.

Et emne uten synsvinkel sier fra: vieweren melder at det ikke er noe å zoome
til. Et emne med feil synsvinkel sier ingenting — det ser ut som verktøyet
fant noe, og etterlater brukeren med å lure på om modellen er ødelagt.

#### Scenario: Posisjonen lar seg ikke fastslå
- **WHEN** et objekts plassering ikke kan leses
- **THEN** emnet skrives uten kamera
- **AND** kjøringen fortsetter

#### Scenario: Funnet gjelder ikke et objekt
- **WHEN** funnet peker på modellen som helhet
- **THEN** emnet skrives uten kamera
