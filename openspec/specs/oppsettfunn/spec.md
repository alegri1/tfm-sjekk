## Purpose

Beskriver hvordan verktøyet finner konfigurasjonen sin, hvordan stier i den
tolkes, hva som gjelder når både et flagg og fila sier noe, og hva som skjer når
en oppgitt sti ikke finnes.

Alt dette er usynlig for brukeren med mindre verktøyet sier fra. En fil som endrer
resultatet uten at noen vet at den ble lest, er verre enn ingen fil — og en sti
som peker feil må ikke kunne se ut som et bevisst valg.

## Requirements

### Requirement: Konfigurasjonen skal kunne finnes uten et flagg

Verktøyet SKAL lete etter `tfm-sjekk.toml` når `--config` ikke er oppgitt: først i
mappa til den første modellen, deretter i arbeidskatalogen. Den første som finnes
brukes.

Rekkefølgen følger av hvor brukeren er. Verktøyet legger allerede rapporten ved
siden av modellen ved dra-og-slipp, fordi det er der arbeidet foregår —
arbeidskatalogen er da programmets egen mappe, som ikke har noe med prosjektet å
gjøre.

#### Scenario: Oppsettet ligger hos modellen
- **WHEN** `tfm-sjekk.toml` ligger i samme mappe som modellen, og `--config` ikke
  er oppgitt
- **THEN** den brukes

#### Scenario: Oppsettet ligger i arbeidskatalogen
- **WHEN** modellens mappe ikke har noen `tfm-sjekk.toml`, men arbeidskatalogen har
- **THEN** den i arbeidskatalogen brukes

#### Scenario: Modellens mappe har forrang
- **WHEN** begge mappene har en `tfm-sjekk.toml`
- **THEN** den som ligger hos modellen brukes

#### Scenario: Ingen finnes
- **WHEN** ingen av stedene har en `tfm-sjekk.toml`
- **THEN** standardverdiene brukes, som før

### Requirement: Verktøyet skal si hvilket oppsett det leste

Verktøyet SKAL oppgi hvilken konfigurasjonsfil kjøringen bygger på, eller at ingen
ble funnet.

Uten det kan to kjøringer av samme kommando gi ulikt svar uten at noe forklarer
hvorfor. Et oppsett som virker i det skjulte er den samme feilen som en kontroll
som hopper over i stillhet.

#### Scenario: En fil ble funnet
- **WHEN** en konfigurasjonsfil er funnet eller oppgitt
- **THEN** kjøringen oppgir hvilken

#### Scenario: Ingen fil ble funnet
- **WHEN** ingen konfigurasjonsfil finnes
- **THEN** kjøringen sier at standardverdiene brukes

### Requirement: Stier i konfigurasjonen skal tolkes relativt til fila

En relativ sti i konfigurasjonen SKAL tolkes relativt til konfigurasjonsfila selv,
ikke til arbeidskatalogen.

Oppsettet hører til prosjektet, sammen med tabellene det peker på. Tolket mot
arbeidskatalogen ville den samme fila gitt ulikt resultat avhengig av hvor
terminalen tilfeldigvis sto, og den kunne ikke sendes til en kollega.

#### Scenario: Kjørt fra en annen mappe
- **WHEN** konfigurasjonen oppgir `tabeller/ns3451.csv`, og verktøyet kjøres fra en
  helt annen mappe
- **THEN** tabellen leses fra mappa ved siden av konfigurasjonsfila

#### Scenario: Absolutt sti
- **WHEN** konfigurasjonen oppgir en absolutt sti
- **THEN** den brukes som den står

### Requirement: Et flagg skal vinne over konfigurasjonen

Er en sti oppgitt både på kommandolinja og i konfigurasjonen, SKAL flagget gjelde.

Flagget er det brukeren skrev nettopp nå. Å la en fil overstyre det ville gjort
kommandolinja uvirksom uten forklaring.

#### Scenario: Begge oppgir mastera
- **WHEN** både `--master` og konfigurasjonen oppgir en TFM-master
- **THEN** fila fra flagget brukes

### Requirement: En oppgitt sti som ikke finnes skal være en feil

Peker konfigurasjonen på en fil som ikke finnes, SKAL kjøringen stoppe med en
melding som navngir stien. Kontrollen SKAL ikke hoppe over som om filen aldri var
oppgitt.

Uten dette ville en skrivefeil i en sti gitt «K7: hoppet over» — nøyaktig det
samme som verktøyet melder når du bevisst kjørte uten master. Brukeren ville trodd
hun kjørte med master og fått en rapport uten K7-funn som ser ren ut. Det er samme
tvetydighet som «ingen funn» mot «ingenting sjekket».

#### Scenario: Skrivefeil i stien
- **WHEN** konfigurasjonen peker på en TFM-master som ikke finnes
- **THEN** kjøringen stopper
- **AND** meldingen navngir stien som ble forsøkt

#### Scenario: Ikke oppgitt er fortsatt et valg
- **WHEN** konfigurasjonen ikke oppgir noen TFM-master
- **THEN** kjøringen fortsetter
- **AND** kontrollene som krever master hopper over, som før

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
