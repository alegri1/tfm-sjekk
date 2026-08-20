## Why

Kjørt på `eksempler/tidligfase.ifc` med standardoppsettet vet verktøyet dette:

```
5 objekter, 5 med TFM-verdi, 0 som parset
5 parsefeil — én eneste grunn: «Mangler «++»-delen: plassering (6 siffer)»
```

Uttrekket var perfekt. Hver verdi lå i det konfigurerte egenskapssettet, i det
konfigurerte feltet. Hundre prosent av dem feiler på nøyaktig én grammatikkregel,
og den regelen er nå konfigurerbar.

`tfm-sjekk oppsett` svarer likevel «Ingenting å foreslå: verdiene lå der oppsettet
sa». Formelt riktig — kommandoen foreslår bare egenskapssett, feltnavn og klasser
— men det er samme situasjon som ga opphav til hele kommandoen: **verktøyet sitter
på kunnskapen brukeren mangler, og lar hen stå der.**

Det treffer nøyaktig segmentet fra §11-samtalen. Små og mellomstore prosjekter
uten dRofus arbeider seg gjennom faser i Revit, og tidligfase er der de møter
verktøyet først. En RIE ville i dag fått fem feil, ingen anvisning, og ingen måte
å vite at én linje i et oppsett løser alt.

## What Changes

- `tfm-sjekk oppsett` foreslår også innstillinger under `[grammatikk]`.
- Bare de to bryterne som gjør en del valgfri: `krev_plassering` og
  `krev_komponenttype`. Sifferantall foreslås ikke — se avgrensningen under.
- En innstilling foreslås når det å slå den av får **hver eneste** verdi som i dag
  feiler, til å parse. Klarer den bare noen av dem, er det merkefeil og ikke fase,
  og ingenting foreslås.
- Forslaget bærer belegget som resten: hvor mange verdier innstillingen løser, og
  hvor mange som allerede parser fint. Er det 43 mot 2, ser brukeren selv at det
  er en fase; er det 3 mot 40, ser hen at det ikke er det.
- Et forslag som bare inneholder grammatikk skal ikke lenger meldes som
  «ingenting å foreslå».

**Avgrensning:** sifferantall foreslås ikke. Å gjøre en del valgfri er en uttalelse
om hvilken *fase* modellen er i — reversibel, og delen avvises fortsatt hvis den er
med og feil. Å endre et sifferantall er en uttalelse om *standarden*, og en
systematisk feilmerking ville blitt velsignet som konfigurasjon og deretter aldri
meldt igjen.

## Capabilities

### Modified Capabilities
- `oppsettforslag`: Nye krav om at forslaget også dekker grammatikk, hvilket belegg
  som kreves, og hva som holdes utenfor. Purpose-teksten dekker allerede dette —
  «hvilke observasjoner som kvalifiserer til å bli konfigurasjon» — og endres ikke.

### New Capabilities

Ingen.

## Impact

- **`oppsett/modell.py`:** `Oppsettforslag` får foreslåtte grammatikkinnstillinger,
  hver med antallet verdier den løser.
- **`oppsett/utled.py`:** prøver hver kandidat mot verdiene som feiler i dag.
- **`oppsett/toml_ut.py`:** skriver `[grammatikk]`-tabellen. Den er en toppnivå-
  tabell og må plasseres slik at `ifc_klasser` fortsatt havner før første tabell —
  den feilen har allerede kostet en runde her.
- **`Kontekst`:** har allerede `parsefeil`; ingen endring ventet, men verdiene som
  feiler må kunne prøves på nytt mot en annen grammatikk.
- **Uendret:** `tfm_sjekk.ifc`, parseren, kontrollene, rapportene.
- **Prøving:** `tidligfase.ifc` er allerede i demoen og er nettopp dette tilfellet.
  Rundturen skal gjelde her også — forslaget brukt som `--config` skal få de fem
  funnene til å forsvinne og duplikatet til å komme fram.
