## REMOVED Requirements

### Requirement: De maskinlesbare rapportene skal ha samme felter

**Reason**: Kravet gjaldt bare formatene som er ment for videre behandling, og
fritok uttrykkelig rapporten til lesing fra å bære objektets TFM-verdi. Fritaket
hvilte på at leseren ser TFM-verdien likevel. Det stemmer bare når funnet handler
om TFM-verdien; melder en kontroll om noe annet, står det andre der i stedet.
Avgrensningen til «maskinlesbare» formater er dermed ikke lenger riktig, og
kravet erstattes av ett som gjelder alle rapportformatene.

**Migration**: Ingen. Erstattet av kravet «Alle rapportformatene skal bære
objektets TFM-verdi», som stiller samme krav til CSV og XLSX som før og utvider
det til rapporten til lesing og til emnene for en viewer.

## ADDED Requirements

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
