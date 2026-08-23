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

### Requirement: Alle rapportformatene skal bære objektets TFM-verdi

Hvert rapportformat SKAL vise TFM-verdien til objektet funnet gjelder, uavhengig
av hva funnet handler om.

Et felt som finnes i ett format og ikke i et annet er en felle for den som bytter
mellom dem — og de brukes side om side: skript og Dynamo leser det ene, mennesker
filtrerer i det andre, og en BIM-koordinator åpner det tredje i en viewer.

Rapporten til lesing og emnene til vieweren var tidligere fritatt, med den
begrunnelsen at leseren ser TFM-verdien likevel. Det holder bare når funnet
handler om TFM-verdien. Ellers identifiserer raden ikke lenger objektet sitt, og
funnet er ikke til å handle på.

#### Scenario: Samme funn i to maskinlesbare formater
- **WHEN** de samme funnene skrives i begge de maskinlesbare formatene
- **THEN** begge inneholder objektets TFM-verdi for hvert funn

#### Scenario: Rapporten til lesing
- **WHEN** funnene vises i rapporten som er ment for lesing
- **THEN** hvert funn viser objektets TFM-verdi

#### Scenario: Emnene til vieweren
- **WHEN** funnene skrives som emner for en BCF-viewer
- **THEN** hvert emne oppgir objektets TFM-verdi

#### Scenario: Et K9-funn identifiserer objektet sitt
- **WHEN** et K9-funn om et MMI-avvik vises i rapporten til lesing
- **THEN** raden viser objektets TFM-verdi
- **AND** MMI-verdien framgår av meldinga

### Requirement: Et felt merket som TFM skal inneholde en TFM-verdi

Ingen rapport SKAL merke en kolonne, en linje eller et felt som TFM når innholdet
er noe annet enn objektets TFM-verdi.

Dette gjelder uavhengig av om formatet er ment for lesing, for videre behandling
eller for en viewer. Et verktøy som ikke kan svare skal si at det ikke kan svare;
å svare feil under en selvsikker etikett er verre enn å la feltet være tomt. En
leser som ser «TFM» over en verdi har ingen grunn til å tvile på den, og oppdager
ikke at kolonnen av og til bærer noe helt annet.

#### Scenario: Kontrollen melder om en annen verdi enn TFM
- **WHEN** en kontroll melder om en verdi som ikke er objektets TFM-verdi
- **THEN** feltet merket som TFM inneholder objektets TFM-verdi
- **AND** ikke verdien kontrollen meldte om

#### Scenario: Objektet mangler TFM-verdi
- **WHEN** et funn gjelder et objekt uten TFM-verdi
- **THEN** feltet merket som TFM er tomt
- **AND** det er tomt framfor å vise en plassholdertekst

#### Scenario: Funnet gjelder ikke et objekt
- **WHEN** et funn ikke gjelder noe objekt i modellen
- **THEN** feltet merket som TFM er tomt
