## Purpose

Lar omfanget settes per fagmodell framfor per kjøring. En federering blander
filer med ulikt ansvar — arkitekten tegner armaturer og servanter for å vise
rommet, og de skal ikke merkes av RIE — og uten dette er valget mellom å
federere og drukne, eller å la være og miste kontrollene som virker på tvers.

## Requirements

### Requirement: Omfanget kan settes per fagmodell

Oppsettet SKAL kunne knytte et filnavnmønster til sitt eget sett IFC-klasser.
Objekter i en fil som treffer et mønster SKAL vurderes mot det settet framfor mot
det som gjelder for kjøringen.

En fil som ikke treffer noe mønster SKAL bruke omfanget på toppnivå, som før.
Uten den nye nøkkelen SKAL verktøyet oppføre seg nøyaktig som i dag.

#### Scenario: En fagmodell har sitt eget omfang
- **WHEN** oppsettet gir et mønster som treffer én fil et eget sett klasser
- **THEN** objektene i den fila vurderes mot det settet
- **AND** objektene i de andre filene vurderes mot omfanget på toppnivå

#### Scenario: Ingen mønstre er satt
- **WHEN** oppsettet ikke gir noen fagmodell sitt eget omfang
- **THEN** alle filer vurderes mot omfanget på toppnivå

### Requirement: Et tomt omfang er et bevisst unntak

Et tomt sett klasser for en fagmodell SKAL bety at fila ikke kontrolleres for
TFM. Verktøyet SKAL IKKE melde det som manglende dekning.

Dette er hele grunnen til at evnen finnes. Meldes det som mangel, får hver
bevisst unntatt fagmodell en advarsel om at ingenting ble kontrollert — og da har
den advarselen sluttet å bety noe. Fravær av dekning skal fortsatt være et funn
når det er en forglemmelse; forskjellen er at prosjektet nå kan si hva det er.

#### Scenario: En fagmodell er unntatt med vilje
- **WHEN** en fil er gitt et tomt sett klasser
- **THEN** ingen kontroll som følger omfanget gir funn på objektene i fila
- **AND** rapporten melder ikke manglende dekning for den fila

#### Scenario: En fagmodell er tom ved et uhell
- **WHEN** en fil ikke er nevnt i oppsettet, og ingen av objektene er i omfanget
  på toppnivå
- **THEN** rapporten melder manglende dekning for den fila, som før

### Requirement: En fil som ikke kontrolleres skal si fra om det

Kjøringen SKAL oppgi hvilke fagmodeller som er unntatt, sammen med dekningen for
de øvrige.

En fil som er unntatt og ellers usynlig er verre enn en som ikke ble lest: den
ser ut som en fagmodell uten feil. Det er samme tvetydighet som «ingen funn» mot
«ingenting sjekket», og et bevisst unntak skal ikke kunne skjule seg i den.

#### Scenario: Unntaket står i utskriften
- **WHEN** en fil er unntatt med et tomt sett klasser
- **THEN** kjøringen oppgir fila og at den ikke ble kontrollert for TFM

### Requirement: Kontroller på tvers av filer følger ikke omfanget

Kontroller som sammenligner objekter fra flere fagmodeller SKAL virke også på
objekter i en unntatt fil.

Å unnta en fagmodell betyr at den ikke måles mot merkekravene, ikke at den er
usynlig for resten. En duplisert komponentforekomst mellom ARK og RIE er nettopp
det federeringen finnes for å finne, og den ville forsvunnet om unntaket gjaldt
alt.

#### Scenario: Et duplikat på tvers av en unntatt fil
- **WHEN** en unntatt fagmodell og en kontrollert fagmodell har samme
  komponentforekomst
- **THEN** duplikatet meldes, med begge filene navngitt

#### Scenario: Den unntatte fila får ingen krav om egen merking
- **WHEN** objekter i en unntatt fagmodell mangler TFM
- **THEN** det meldes ikke
