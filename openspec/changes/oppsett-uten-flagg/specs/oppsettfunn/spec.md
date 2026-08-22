## Purpose

Beskriver hvordan verktøyet finner konfigurasjonen sin, hvordan stier i den
tolkes, hva som gjelder når både et flagg og fila sier noe, og hva som skjer når
en oppgitt sti ikke finnes.

Alt dette er usynlig for brukeren med mindre verktøyet sier fra. En fil som endrer
resultatet uten at noen vet at den ble lest, er verre enn ingen fil — og en sti
som peker feil må ikke kunne se ut som et bevisst valg.

## ADDED Requirements

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
