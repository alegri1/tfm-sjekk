## Why

`tfm-sjekk.toml` tar imot hva som helst. En nøkkel verktøyet ikke kjenner blir
lest, forkastet og aldri nevnt.

Prøvd på fire nivåer, alle stille:

| Fila inneholder | I dag |
|---|---|
| `foring_systemkode` i `[elektro]` — mangler en `r` | leses uten innsigelse |
| `[elektrp]` — feilstavet seksjon | leses uten innsigelse |
| `tfm_mastr` på toppnivå | leses uten innsigelse |
| `ifc_klasser` inne i `[pset]` | leses uten innsigelse |

Den siste er ikke oppdiktet. `oppsett`-kommandoen skrev en gang `ifc_klasser`
etter `[pset]`, og TOML leste den da som `pset.ifc_klasser`. Fila var gyldig
TOML, konfigurasjonen var gyldig, og halve forslaget var borte. Feilen ble
funnet fordi en test tilfeldigvis kjørte forslaget gjennom verktøyet igjen.

Konsekvensen er den samme hver gang: **rapporten blir laget med andre regler enn
du ba om, og den ser like ren ut.** Det er nøyaktig tvetydigheten
`oppsettfunn` allerede har et krav mot — «En oppgitt sti som ikke finnes skal
være en feil» — men det kravet gjelder bare stier, ikke nøkler.

Saken blir mer aktuell, ikke mindre. Regelsettet leveres som data (§14), og hver
nye nøkkel er en ny ting å skrive feil. `foring_systemkoder` kom i går.

## What Changes

- En ukjent nøkkel i `tfm-sjekk.toml` **stopper kjøringen** med exit 2, på samme
  måte som en sti som peker feil gjør i dag.
- Meldingen navngir nøkkelen, seksjonen den sto i, og den nærmeste gyldige
  nøkkelen når det finnes en:

      Feil i tfm-sjekk.toml:
        Ukjent nøkkel «foring_systemkode» i [elektro].
        Mente du «foring_systemkoder»?

- Alle sju modellene i `config.py` avviser ukjente nøkler, så en feilstavet
  seksjon og en nøkkel i feil seksjon fanges like godt som en feilstavet nøkkel.
- `[kontroller.K4]` og de andre kontrollnøklene er uendret — `kontroller` er en
  ordbok med kontroll-ID som nøkkel, og ID-ene skal ikke være en fast liste.

**BREAKING:** en konfigurasjon som i dag leses uten innsigelse kan nå stoppe
kjøringen. Det er hensikten — men det rammer også en fil skrevet for en nyere
utgave av verktøyet enn den som leser den. Se design.md.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `oppsettfunn`: Nytt krav om at en ukjent nøkkel i konfigurasjonen skal stoppe
  kjøringen med en melding som navngir nøkkelen og seksjonen. Søsken til det
  eksisterende kravet om stier som ikke finnes, og med samme begrunnelse: en
  rapport laget på andre premisser enn brukeren tror, ser ikke annerledes ut.
  De fem eksisterende kravene står uendret.

## Impact

- **`config.py`:** `model_config = ConfigDict(extra="forbid")` på de sju
  modellene, og en oversetter fra pydantics `ValidationError` til en norsk
  melding. Forslaget om nærmeste nøkkel kommer fra `difflib` i standardbiblioteket
  — ingen ny avhengighet.
- **`cli.py`:** feilen fanges og blir exit 2, som stifeil i dag.
- **`oppsett/toml_ut.py`:** ingen endring i koden, men fila den skriver må
  fortsatt kunne leses. Det er allerede prøvd av en test som kjører forslaget
  gjennom `--config`, og den blir nå strengere av seg selv.
- **Uendret:** kontrollene, rapportene, `tfm_sjekk.ifc`, Dynamo-skriptene.
- **Prøving:** de fire tilfellene i tabellen over skal alle stoppe kjøringen, og
  hver av dem skal navngi det som er galt. En riktig skrevet fil — og
  repoets egen `tfm-sjekk.toml`, og fila `oppsett` skriver — skal fortsatt leses.
