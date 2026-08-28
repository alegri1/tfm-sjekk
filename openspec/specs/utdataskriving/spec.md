## Purpose

Beskriver hva verktøyet garanterer om filene det skriver: at en utmappe aldri
står igjen med filer fra to ulike runder, og at en fil som ikke lar seg skrive
blir sagt fra om framfor å etterlate en halv leveranse.

Rapportene er det som forlater maskinen. En BCF importeres i en viewer og
tildeles folk, et regneark deles i Teams. En fil fra forrige runde som ligger
ved siden av en fra denne, ser like fersk ut som naboen.

## Requirements

### Requirement: En utmappe skal ikke inneholde filer fra to runder

Fullfører ikke en kjøring skrivingen av alle rapportfilene, SKAL ingen av dem
være endret.

Utfallet skal være ett av to: alle filene er fra denne runden, eller alle er fra
den forrige. Aldri en blanding.

Dette er den vanligste hendelsen i en rettingsrunde. Rapporten åpnes, modellen
rettes, kjøringen gjentas — og på Windows nekter Excel andre å skrive til fila
den har åpen. Fanget ved å låse `funn.xlsx` og kjøre en runde til: HTML-en og
CSV-en ble nye, regnearket ble nullstilt, og BCF-en sto igjen fra forrige runde,
byte for byte. BCF-en er den som importeres og tildeles folk.

#### Scenario: En av filene kan ikke skrives
- **WHEN** en kjøring ikke får skrevet en av rapportfilene
- **THEN** er ingen av rapportfilene i utmappa endret
- **AND** er filene fra forrige runde fortsatt hele og lesbare

#### Scenario: En vellykket kjøring skriver alle
- **WHEN** en kjøring fullfører
- **THEN** er hver rapportfil i utmappa fra denne kjøringen

### Requirement: En fil som ikke lar seg skrives skal gi en melding

Kan ikke en rapportfil skrives, SKAL verktøyet avslutte med en melding som
navngir fila, og avslutte med koden som betyr at kjøringen ikke kunne
gjennomføres.

Meldingen SKAL nevne den vanligste årsaken: at fila er åpen i et annet program.

En traceback gjennom `openpyxl` og `zipfile` sier ikke at regnearket står åpent i
Excel. Exit-koden må heller ikke si «modellen har feil» — den som leser den ville
tro at merkingen fortsatt er avvist.

#### Scenario: Rapportfila er låst av et annet program
- **WHEN** en rapportfil ikke kan skrives fordi den er åpen i et annet program
- **THEN** navngir meldingen fila
- **AND** nevner den at fila kan være åpen i et annet program
- **AND** er exit-koden den samme som når en modellfil ikke lar seg lese

#### Scenario: Ingen traceback
- **WHEN** en kjøring stopper fordi en rapportfil ikke lot seg skrive
- **THEN** vises ingen traceback

### Requirement: Utmappa skal være en mappe

Peker stien for utdata på noe som finnes og ikke er en mappe, SKAL verktøyet si
det med en melding framfor å la operativsystemets feil boble opp.

#### Scenario: Stien peker på en fil
- **WHEN** stien for utdata peker på en fil som finnes
- **THEN** sier meldingen at stien ikke er en mappe
- **AND** er exit-koden den samme som når en modellfil ikke lar seg lese
