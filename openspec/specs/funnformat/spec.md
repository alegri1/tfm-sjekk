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

### Requirement: Et BCF-emne skal bære versjonen av verktøyet som lagde det

Hvert emne SKAL oppgi hvilken utgave av verktøyet som skrev det.

En rapport kan være eldre enn koden som lagde den, og det ser man ikke på den.
En BCF laget før en rettelse har GUID-er som stemmer og emner som åpner seg —
den gjør bare noe galt, og vieweren har ingen grunn til å si fra.

Det skjedde: en fil laget før kamerafeilen ble rettet lå ved siden av to ferske,
og den eneste måten å skille dem på var å regne ut avstanden fra kameraet til
objektet.

Versjonen hører hjemme der et menneske ser den, ikke i en fil bare et skript
leser. `bcf.version` er unntatt: `DetailedVersion` der er BCF-formatets versjon,
og å skrive verktøyets versjon i det feltet ville vært å svare på et annet
spørsmål enn det som stilles.

#### Scenario: Emnet oppgir versjonen
- **WHEN** funnene skrives som emner for en BCF-viewer
- **THEN** hvert emne oppgir versjonen av verktøyet
- **AND** versjonen er synlig i emnet, ikke bare i en fil ved siden av

#### Scenario: Formatets egen versjon er ikke verktøyets
- **WHEN** BCF-fila oppgir hvilken versjon av BCF-formatet den følger
- **THEN** det feltet er uendret av hvilken versjon verktøyet har

#### Scenario: Fila er fortsatt reproduserbar
- **WHEN** de samme funnene skrives to ganger med samme tidsstempel og samme
  utgave av verktøyet
- **THEN** filene er byte-identiske

### Requirement: En forkortet tittel skal slutte et sted den kan slutte

Må et emnes tittel kortes ned for å holde seg innenfor formatets grense, SKAL
den avsluttes ved en grense i teksten — en setning eller et ord — og ikke midt
inne i et ord.

Tittelen SKAL ikke avsluttes på et tegn som åpner noe: en parentes, et
anførselstegn eller en bindestrek som venter på det som kommer etter. Åpner
tittelen en parentes uten å lukke den, SKAL parentesen ikke stå igjen.

En sammenhengende streng uten mellomrom SKAL ikke regnes som et ord. Et objekts
TFM-ID er 26 tegn uten mellomrom, og en melding som ramser opp flere av dem har
ingen ordgrense å kutte ved.

Tittelen er det eneste en viewer viser i emnelista. Hele meldingen står i
beskrivelsen, så ingenting går tapt — men den som blar gjennom hundre emner
leser bare titlene, og «merket med system…» ser ut som en ødelagt fil framfor en
forkortet setning. En avslutning som lukker seg selv sier tydelig at det finnes
mer å lese; en som stopper midt i et ord sier at noe er galt.

#### Scenario: Meldingen har en setningsgrense innenfor grensen
- **WHEN** meldingen er for lang og første setning slutter innenfor grensen
- **THEN** er tittelen den første setningen, hel

#### Scenario: Første setning er selv for lang
- **WHEN** meldingen er for lang og det ikke finnes noen setningsgrense innenfor
  grensen
- **THEN** avsluttes tittelen ved siste hele ord som får plass
- **AND** det siste ordet i tittelen er ikke halvert

#### Scenario: Kuttet lander like etter en åpen parentes
- **WHEN** teksten fram til grensen slutter på en parentes eller et
  anførselstegn som ikke er lukket
- **THEN** tas det tegnet ikke med i tittelen

#### Scenario: Kuttet lander inne i en parentes
- **WHEN** tittelen åpner en parentes og grensen nås før den lukkes
- **THEN** er hele den åpne parentesen utelatt fra tittelen
- **AND** avsluttes tittelen ved siste hele ord foran den

#### Scenario: Teksten er én lang identifikator
- **WHEN** teksten fram til grensen ikke inneholder noen ordgrense verdt navnet
- **THEN** kuttes den likevel, og tittelen holder seg innenfor grensen
- **AND** er tittelen ikke redusert til de første tegnene alene

#### Scenario: Tittelen holder seg innenfor grensen
- **WHEN** en melding av hvilken som helst lengde blir til en tittel
- **THEN** er tittelen aldri lengre enn det formatet tillater

#### Scenario: Det er synlig at tittelen er forkortet
- **WHEN** en tittel er kortet ned fordi meldingen var for lang
- **THEN** viser tittelen selv at den fortsetter et annet sted
