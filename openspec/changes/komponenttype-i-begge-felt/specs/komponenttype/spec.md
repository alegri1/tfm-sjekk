## Purpose

Beskriver hvordan verktøyet fastslår et objekts komponenttype når opplysningen kan
stå to steder — i `%`-delen av TFM-ID-en og i et eget egenskapssett — hva som skjer
når de to er uenige, og hvilken kilde som gjelder når bare én finnes.

To felt med samme opplysning er nettopp der en modell går ut av synk med seg selv.
Uten en regel her ser verktøyet bare det ene, og et sprik forblir usynlig.

## ADDED Requirements

### Requirement: Komponenttypen skal være den samme i begge feltene

Når et objekt har komponenttype både i `%`-delen av TFM-ID-en og i det konfigurerte
type-egenskapssettet, og de to ikke er like, SKAL verktøyet melde det som en feil.

Det er en selvmotsigelse i merkingen: verdien lar seg ikke avgjøre uten å rette
modellen.

#### Scenario: De to feltene spriker
- **WHEN** TFM-ID-en ender på `%JVZ.001.008` og typefeltet inneholder `JVZ.001.009`
- **THEN** rapporten melder en feil
- **AND** meldingen oppgir begge verdiene

#### Scenario: De to feltene er like
- **WHEN** begge oppgir `JVZ.001.008`
- **THEN** gir det ingen funn

#### Scenario: Skrivemåte skiller dem ikke
- **WHEN** de to verdiene er like bortsett fra mellomrom rundt eller små og store
  bokstaver
- **THEN** regnes de som like

### Requirement: Objektets komponenttype har én kilde med forrang

Verktøyet SKAL fastsette objektets komponenttype slik at andre kontroller har én
verdi å forholde seg til:

1. Står den i `%`-delen av TFM-ID-en, gjelder den. `%`-delen er en del av selve
   TFM-ID-en, som er det merkingen egentlig er.
2. Ellers gjelder verdien i type-egenskapssettet.
3. Er ingen av dem til stede, har objektet ingen komponenttype.

#### Scenario: %-delen har forrang
- **WHEN** begge er til stede og like
- **THEN** er objektets komponenttype den verdien

#### Scenario: Typefeltet er eneste kilde
- **WHEN** TFM-ID-en er uten `%`-del, og typefeltet inneholder `JVZ.001.008`
- **THEN** er objektets komponenttype `JVZ.001.008`

#### Scenario: Ingen av delene
- **WHEN** verken `%`-delen eller typefeltet finnes
- **THEN** har objektet ingen komponenttype, og kontroller som trenger den hopper
  over objektet

### Requirement: Komponenttypen fra typefeltet sjekkes mot mastera

En komponenttype som bare står i type-egenskapssettet SKAL sjekkes mot prosjektets
TFM-master på samme måte som en som står i `%`-delen.

`krev_komponenttype` er `false` som standard fordi mange prosjekter utelater
`%`-delen. Uten dette kravet sjekkes komponenttyper mot mastera bare for den
forsvinnende delen av en modell som har `%`-del.

#### Scenario: Type bare i typefeltet, ukjent i mastera
- **WHEN** TFM-ID-en er uten `%`-del, typefeltet inneholder en komponenttype, og
  den ikke står i mastera
- **THEN** melder rapporten det på samme måte som for en type fra `%`-delen

#### Scenario: Type bare i typefeltet, kjent i mastera
- **WHEN** samme oppsett, men typen står i mastera
- **THEN** gir det ingen funn

### Requirement: Et sprik gir ikke funn om mastera i tillegg

Når de to feltene er uenige, SKAL verktøyet ikke i tillegg melde at komponenttypen
mangler i mastera.

Spørsmålet om hvilken av de to verdiene som gjelder er uavklart, og et funn om
mastera ville hvilt på et vilkårlig valg mellom dem. Spriket skal rettes først.

#### Scenario: Sprik melder bare spriket
- **WHEN** de to feltene er uenige, og ingen av verdiene står i mastera
- **THEN** melder rapporten spriket
- **AND** den melder ikke i tillegg at komponenttypen mangler i mastera
