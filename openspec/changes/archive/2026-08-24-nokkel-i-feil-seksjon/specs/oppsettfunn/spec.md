## ADDED Requirements

### Requirement: Meldingen skal peke på seksjonen nøkkelen hører hjemme i

Finnes den ukjente nøkkelen som et gyldig felt et annet sted i konfigurasjonen,
SKAL meldingen si hvor.

Nøkkelen er da ikke ukjent — den står bare feil. Seksjonsinndelingen i TOML er
usynlig når man skriver: en nøkkel som havner under feil overskrift ser ut som
en nøkkel på riktig sted. Det er nettopp slik `ifc_klasser` havnet inne i
`[pset]` og ble lest som `pset.ifc_klasser`.

Forskjellen mellom «ukjent nøkkel» og «flytt den dit» er forskjellen mellom å
lete i dokumentasjonen og å rette én linje.

#### Scenario: Nøkkelen hører hjemme på toppnivå
- **WHEN** en nøkkel som er et toppnivåfelt står inne i en seksjon
- **THEN** meldingen sier at den hører hjemme på toppnivå

#### Scenario: Nøkkelen hører hjemme i en annen seksjon
- **WHEN** en nøkkel som hører til én seksjon står i en annen
- **THEN** meldingen navngir seksjonen den hører hjemme i

#### Scenario: Nøkkelen finnes ikke noe sted
- **WHEN** den ukjente nøkkelen ikke er et gyldig felt noe sted
- **THEN** meldingen oppfører seg som før

### Requirement: Å peke hjem skal gå foran å foreslå noe som ligner

Finnes nøkkelen et annet sted, SKAL meldingen si det framfor å foreslå en
lignende nøkkel i seksjonen den sto i.

Et navn som ligner er en gjetning. Et navn som er identisk et annet sted er et
svar. Å tilby gjetningen når svaret finnes, sender brukeren til feil sted — og
det er verre enn å si ingenting, fordi et forslag ser ut som en opplysning.

#### Scenario: Begge deler kunne vært sagt
- **WHEN** den ukjente nøkkelen både finnes i en annen seksjon og ligner en
  nøkkel i den den sto i
- **THEN** meldingen sier hvor nøkkelen hører hjemme
- **AND** den foreslår ikke den lignende nøkkelen
