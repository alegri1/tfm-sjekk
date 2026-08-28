## Purpose

Beskriver hva verktøyet garanterer om å lese en modellfil: at en fil det ikke
kan lese blir sagt fra om framfor å krasje, at det sies med koden som betyr
«kunne ikke kjøre» og ikke den som betyr «modellen er underkjent», og at en
ufullstendig fil ikke blir lest som om den var hel.

Grensen mot omverdenen er der et verktøy oftest lyver uten å mene det. Alt
innenfor er kontrollert av kontrollene; fila som kommer inn er det ingen som har
kontrollert, og den kommer fra en eksport som kan ha blitt avbrutt.

## Requirements

### Requirement: En fil som ikke lar seg lese skal gi en melding

Kan ikke en oppgitt modellfil åpnes eller tolkes som IFC, SKAL verktøyet
avslutte med en melding som navngir fila og sier hva som gikk galt.

Meldingen SKAL være verktøyets egen. En traceback fra et bibliotek er ikke en
melding: den peker på en linje i `ifcopenshell`, og den som leser den er en
BIM-koordinator som skal finne ut om det er modellen eller maskinen som er
problemet.

#### Scenario: Fila er tom
- **WHEN** en oppgitt modellfil er tom
- **THEN** avslutter verktøyet med en melding som navngir fila
- **AND** vises ingen traceback

#### Scenario: Fila er ikke IFC
- **WHEN** en oppgitt modellfil ikke lar seg tolke som IFC
- **THEN** sier meldingen at fila ikke kunne leses som IFC
- **AND** navngir den fila det gjelder

### Requirement: En ulesbar fil skal ikke se ut som en underkjent modell

Avslutter verktøyet fordi en fil ikke lot seg lese, SKAL exit-koden være den som
betyr at kjøringen ikke kunne gjennomføres — den samme som når en oppgitt sti
ikke finnes. Den SKAL ikke være koden som betyr at modellen har feil.

Exit-koden er porten i en leveranseprosess (§5). To utfall som krever helt ulik
handling — rett merkingen, eller skaff en hel fil — må ikke være samme tall.

#### Scenario: Koden skiller seg fra en underkjent modell
- **WHEN** en kjøring stopper fordi en fil ikke lot seg lese
- **THEN** er exit-koden den samme som når en oppgitt sti ikke finnes
- **AND** er den ikke den samme som når kontrollene fant feil

#### Scenario: Koden er ikke tilfeldig
- **WHEN** en kjøring stopper fordi en fil ikke lot seg lese
- **THEN** er exit-koden den samme uansett hvorfor fila ikke lot seg lese

### Requirement: En kjøring som ikke kom i mål skal ikke etterlate en rapport

Stopper kjøringen fordi en fil ikke lot seg lese, SKAL ingen rapportfil skrives.

En rapport fra en kjøring som ikke kom i mål ser ut som enhver annen rapport, og
den blir delt. Ligger det en fra en tidligere runde i mappa, er det tydeligere at
den er gammel enn at den er halv.

#### Scenario: Ingen rapport skrives
- **WHEN** en kjøring stopper fordi en fil ikke lot seg lese
- **THEN** finnes det ingen ny rapportfil i utmappa

### Requirement: En ufullstendig fil skal ikke leses som en hel

Mangler en IFC-fil avslutningen formatet krever, SKAL verktøyet behandle den som
uleselig og si at fila ser avkuttet ut.

En avbrutt eksport gir en fil som åpner seg fint og inneholder en brøkdel av
modellen. Verktøyet rapporterer da sant om det det så — «1 av 1 objekter i
omfanget, alle TFM-verdiene lot seg tolke» — og hver linje er misvisende. Det er
det farligste utfallet av de tre, fordi det ikke ser ut som en feil.

#### Scenario: Fila mangler avslutningen
- **WHEN** en oppgitt modellfil mangler avslutningsmarkøren IFC-formatet krever
- **THEN** stopper kjøringen med en melding om at fila ser avkuttet ut
- **AND** rapporteres det ikke et objekttall for fila

#### Scenario: En hel fil går gjennom
- **WHEN** en oppgitt modellfil har avslutningsmarkøren på plass
- **THEN** leses den som før

### Requirement: I en federert kjøring skal meldingen navngi fila

Leses flere fagmodeller i samme kjøring og én av dem ikke lar seg lese, SKAL
meldingen oppgi hvilken fil det gjelder.

Kjøringen SKAL stoppe framfor å svare på de øvrige filene. K6 og D3 ser på tvers
av fagmodellene, og et svar der én modell mangler er feil uten å se feil ut: en
komponentforekomst som finnes i to filer ser unik ut når bare den ene ble lest.

#### Scenario: Én av flere filer er uleselig
- **WHEN** en kjøring leser seks fagmodeller og den fjerde ikke lar seg lese
- **THEN** navngir meldingen den fjerde fila
- **AND** skrives det ingen rapport for de fem andre

#### Scenario: Filnavnet overlever parallell lesing
- **WHEN** filene leses i flere prosesser samtidig
- **THEN** er filnavnet i meldingen fortsatt det til fila som feilet
