## Why

En nøkkel i feil seksjon stopper nå kjøringen, men meldingen sier ikke hvor den
hører hjemme:

    Ukjent nøkkel «ifc_klasser» i [pset].

Nøkkelen er ikke ukjent. Den finnes — på toppnivå. Meldingen forteller at noe er
galt, og lar brukeren lete i dokumentasjonen etter hvor det skulle stått.

Det er ikke et konstruert tilfelle. `oppsett`-kommandoen skrev en gang
`ifc_klasser` etter `[pset]`, og TOML leste den da som `pset.ifc_klasser`.
Feilen kostet en halv dag, og fila den lagde så helt riktig ut. Da kravet om
ukjente nøkler kom i 0.6.0, ble akkurat den feilen fanget — men meldingen den
gir peker ikke hjem.

Tre tilfeller, alle med samme svakhet:

| Fila inneholder | Meldingen sier i dag | Fasit |
|---|---|---|
| `ifc_klasser` i `[pset]` | Ukjent nøkkel i [pset] | hører på toppnivå |
| `krev_plassering` i `[elektro]` | Ukjent nøkkel i [elektro] | hører i `[grammatikk]` |
| `gyldige_verdier` i `[master]` | Ukjent nøkkel i [master] | hører i `[mmi]` |

Forslagsmekanismen finnes allerede, men den leter bare etter nøkler som *ligner*
i den samme seksjonen. En nøkkel som er skrevet helt riktig, bare på feil sted,
faller utenfor — og det er det tilfellet som er lettest å rette hvis noen sier
hvor.

Seksjonsinndelingen i TOML er ikke synlig når man skriver. En nøkkel som havner
under feil overskrift ser ut som en nøkkel på riktig sted, og det er hele
grunnen til at feilen skjedde i utgangspunktet.

## What Changes

- Finnes den ukjente nøkkelen i en annen seksjon, SKAL meldingen si hvilken:

      Ukjent nøkkel «ifc_klasser» i [pset].
      Den hører hjemme på toppnivå.

  og for en nøkkel som hører i en annen seksjon:

      Ukjent nøkkel «krev_plassering» i [elektro].
      Den hører hjemme i [grammatikk].

- Det eksisterende forslaget om nærmeste *lignende* nøkkel er uendret, og
  brukes fortsatt der ingen nøkkel med samme navn finnes andre steder.
- **Uendret:** at kjøringen stopper, exit-koden, og hvilke filer som godtas.
  Bare meldingen blir mer presis.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `oppsettfunn`: Nytt krav om at meldingen skal peke på seksjonen nøkkelen hører
  hjemme i, når nøkkelen finnes et annet sted. Søsken til det eksisterende
  kravet om nærmeste lignende nøkkel, og med samme begrunnelse: forskjellen
  mellom «ukjent nøkkel» og «flytt den dit» er forskjellen mellom å lete og å
  rette. De sju eksisterende kravene står uendret.

## Impact

- **`config.py`:** `_ukjente_nokler` slår opp nøkkelnavnet i de andre modellene
  før den faller tilbake på `difflib`. Modellene kjenner sine egne felter, så
  oppslaget kan ikke drive fra dem.
- **Uendret:** `cli.py`, kontrollene, rapportformatene, alt annet.
- **Prøving:** de tre tilfellene i tabellen over skal alle navngi riktig
  seksjon. En nøkkel som ikke finnes noe sted skal fortsatt få det gamle
  forslaget, og en som ikke ligner noe skal fortsatt få meldingen uten forslag.
