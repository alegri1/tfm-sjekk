## Purpose

Beskriver hva de maskinlesbare rapportene garanterer om hvert funn: hvilke felter
som alltid betyr det samme, hvilke som avhenger av hvilken kontroll som meldte, og
hva som er tomt når et funn ikke gjelder et objekt.

Formatet er en kontrakt. Fila leses av skript, av en Dynamo-graf og av Excel, og
et felt som betyr to ting avhengig av avsenderen kan ikke brukes til noen av dem.

## Requirements

### Requirement: Hvert funn skal bære objektets egen TFM-verdi

De maskinlesbare rapportene SKAL ha et felt som alltid inneholder TFM-verdien til
objektet funnet gjelder, uavhengig av hva funnet handler om.

Uten det kan et funn ikke knyttes til objektet sitt av noe utenfor verktøyet. En
kobling som må utlede nøkkelen av andre rader, virker for noen funn og ikke for
andre — og feiler i stillhet for dem den ikke virker for.

#### Scenario: Funnet handler om TFM-verdien
- **WHEN** et K2-funn melder om syntaksen i objektets TFM-verdi
- **THEN** feltet inneholder objektets TFM-verdi

#### Scenario: Funnet handler om noe annet
- **WHEN** et K9-funn melder om objektets MMI-verdi
- **THEN** feltet inneholder objektets TFM-verdi, ikke MMI-verdien

#### Scenario: Objektet mangler TFM
- **WHEN** et K1-funn melder at objektet ikke har noen TFM-verdi
- **THEN** feltet er tomt

#### Scenario: Funnet gjelder ikke et objekt
- **WHEN** et K7-funn melder at en oppføring i mastera ikke er modellert
- **THEN** feltet er tomt
- **AND** feltet for objektets identitet er også tomt

### Requirement: Feltet for funnets verdi skal beholde sin betydning

Feltet som bærer verdien funnet handler om SKAL fortsette å gjøre det, og SKAL
ikke endres til å bety noe annet.

De to feltene svarer på hvert sitt spørsmål: *hvilket objekt gjelder dette?* og
*hvilken verdi er det noe galt med?* For de fleste funn er svaret det samme, og
nettopp derfor er det lett å forveksle dem — men for K9 er det ikke det, og en
leser som antar at de er like tar feil uten å merke det.

#### Scenario: De to feltene kan være ulike
- **WHEN** et K9-funn melder om et MMI-avvik på et objekt med TFM-verdi
- **THEN** feltet for funnets verdi inneholder MMI-verdien
- **AND** feltet for objektets TFM-verdi inneholder TFM-verdien
- **AND** de to er ulike

### Requirement: De maskinlesbare rapportene skal ha samme felter

Rapportformatene som er ment for videre behandling SKAL tilby de samme feltene om
hvert funn.

Et felt som finnes i ett format og ikke i et annet er en felle for den som bytter
mellom dem — og de brukes side om side: skript og Dynamo leser det ene, mennesker
filtrerer i det andre.

#### Scenario: Samme funn i to formater
- **WHEN** de samme funnene skrives i begge de maskinlesbare formatene
- **THEN** begge inneholder objektets TFM-verdi for hvert funn

#### Scenario: Rapporten til lesing er unntatt
- **WHEN** funnene vises i rapporten som er ment for lesing
- **THEN** den trenger ikke feltet

### Requirement: En konsument skal kunne se hvor nøkkelen kom fra

Et verktøy som knytter funn til objekter utenfor tfm-sjekk SKAL oppgi om det
brukte det garanterte feltet eller utledet nøkkelen på annen måte.

En eldre rapport uten feltet skal fortsatt kunne brukes, men den gir et svakere
resultat — og forskjellen skal være synlig framfor å måtte gjettes.

#### Scenario: Rapporten har feltet
- **WHEN** koblingen leser en rapport som inneholder objektets TFM-verdi
- **THEN** den bruker det feltet
- **AND** den oppgir at nøkkelen kom derfra

#### Scenario: Rapporten mangler feltet
- **WHEN** koblingen leser en eldre rapport uten feltet
- **THEN** den utleder nøkkelen som før
- **AND** den oppgir at nøkkelen ble utledet
