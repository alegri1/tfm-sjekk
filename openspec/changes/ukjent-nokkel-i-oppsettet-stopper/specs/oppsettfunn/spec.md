## ADDED Requirements

### Requirement: En ukjent nøkkel i konfigurasjonen skal være en feil

Inneholder konfigurasjonen en nøkkel verktøyet ikke kjenner, SKAL kjøringen
stoppe med en melding som navngir nøkkelen og hvilken seksjon den sto i.
Nøkkelen SKAL ikke forkastes i stillhet.

Dette er samme sak som en sti som peker feil, én etasje ned. En forkastet nøkkel
betyr at kjøringen brukte andre regler enn den som skrev fila ba om — og
rapporten ser like ren ut. Brukeren har ingen måte å oppdage det på: fila er
gyldig, kjøringen går, tallene kommer.

Det har skjedd. `ifc_klasser` skrevet etter `[pset]` leses av TOML som
`pset.ifc_klasser`, og halve konfigurasjonen var borte uten et ord.

Kravet gjelder alle nivåer i fila: en feilstavet nøkkel, en feilstavet seksjon,
og en gyldig nøkkel i feil seksjon er den samme feilen for den som skrev den.

#### Scenario: Feilstavet nøkkel
- **WHEN** konfigurasjonen inneholder en nøkkel som ligner en gyldig, men ikke er det
- **THEN** kjøringen stopper
- **AND** meldingen navngir nøkkelen og seksjonen

#### Scenario: Feilstavet seksjon
- **WHEN** konfigurasjonen inneholder en seksjon verktøyet ikke kjenner
- **THEN** kjøringen stopper

#### Scenario: Gyldig nøkkel i feil seksjon
- **WHEN** en nøkkel som hører hjemme på toppnivå står inne i en seksjon
- **THEN** kjøringen stopper

#### Scenario: En riktig skrevet fil leses som før
- **WHEN** konfigurasjonen bare inneholder nøkler verktøyet kjenner
- **THEN** kjøringen fortsetter

#### Scenario: Kontroll-ID-er er ikke en fast liste
- **WHEN** konfigurasjonen setter alvorlighet for en kontroll
- **THEN** kontrollens ID godtas som nøkkel

### Requirement: Meldingen skal peke på den nærmeste gyldige nøkkelen

Finnes det en kjent nøkkel som ligner den ukjente, SKAL meldingen nevne den.

En melding som bare sier at noe er ukjent, etterlater brukeren med å lese
dokumentasjonen på nytt for å finne ett tegn. Meldingene i dette verktøyet leses
av en BIM-koordinator, ikke av en utvikler, og forskjellen mellom «ukjent
nøkkel» og «mente du dette» er forskjellen mellom å lete og å rette.

#### Scenario: Det finnes en som ligner
- **WHEN** den ukjente nøkkelen ligner en gyldig nøkkel i samme seksjon
- **THEN** meldingen nevner den gyldige nøkkelen

#### Scenario: Det finnes ingen som ligner
- **WHEN** den ukjente nøkkelen ikke ligner noen gyldig nøkkel
- **THEN** meldingen navngir den ukjente nøkkelen uten å foreslå noe
