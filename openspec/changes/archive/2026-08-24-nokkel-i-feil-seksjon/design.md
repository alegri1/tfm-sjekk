## Context

Se proposal.md — Why.

`_ukjente_nokler` i `config.py` oversetter pydantics `ValidationError` til norsk.
For hver `extra_forbidden` navngir den nøkkelen og seksjonen, og tilbyr så
nærmeste lignende nøkkel fra `_gyldige_nokler(loc)` — feltene i modellen der
nøkkelen sto.

Modellene kjenner sine egne felter gjennom `model_fields`. Det er derfor
forslaget ikke kan drive fra modellen, og det er den samme egenskapen dette
bygger videre på.

## Goals / Non-Goals

**Goals:**

- En nøkkel som bare står feil, skal få vite hvor den hører hjemme.
- Oppslaget skal komme fra modellene, ikke fra en liste noen vedlikeholder.

**Non-Goals:**

- Å flytte nøkkelen for brukeren. Verktøyet skal si hva som er galt, ikke gjette
  seg til hva som var ment og gjøre det. En konfigurasjon brukeren ikke skrev,
  er en konfigurasjon brukeren ikke kan stole på.
- Å håndtere at samme navn finnes i flere seksjoner samtidig. Se avveiningen
  under.

## Decisions

### Oppslaget går gjennom modellene, ikke gjennom en tabell

Feltnavnene finnes på `Konfigurasjon.model_fields` og på hver seksjonsmodell.
Å bygge kartet «feltnavn → hvor det hører hjemme» av dem koster ingenting og
kan ikke bli utdatert: legger noen til en nøkkel, er den med neste gang.

En håndskrevet tabell ville drevet fra modellen første gang noen la til et felt
— den samme grunnen til at `_gyldige_nokler` allerede leser `model_fields`.

### Å peke hjem går foran å foreslå noe som ligner

Rekkefølgen er ikke vilkårlig. Et identisk navn et annet sted er et svar; et
lignende navn i samme seksjon er en gjetning.

`krev_plassering` i `[elektro]` viser hvorfor det betyr noe: i dag foreslo
mekanismen `krets_klasser` med 0.67 i likhet, og det forslaget ble skrudd av
ved å heve terskelen til 0.85. Med dette kravet får den samme nøkkelen et
riktig svar i stedet for ingen — `[grammatikk]`.

### Samme navn i flere seksjoner

Det finnes ikke i dag, og hvis det oppstår skal meldingen nevne alle stedene
framfor å velge ett. Å peke på det første i en vilkårlig rekkefølge ville vært
en gjetning forkledd som et svar.

Det er billig å gjøre riktig fra starten, og dyrt å oppdage senere: en melding
som peker på feil seksjon er verre enn en som ikke peker noe sted.

## Risks / Trade-offs

**Meldingen blir lengre** → Tre linjer i stedet for to. Det er akseptabelt: den
tredje linja er den som gjør noe.

**Et felt kan hete det samme som et TOML-nøkkelord** → Ikke et problem her.
Oppslaget går mot feltnavn i pydantic-modellene, som er Python-identifikatorer,
og TOML har ingen reserverte nøkler.

**Brukeren kan tro at verktøyet flytter nøkkelen** → Meldingen sier «hører
hjemme i», ikke «flyttet til». Formuleringen er valgt for å beskrive, ikke for
å love.
