## Context

Se `proposal.md` for hvorfor. Det som former løsningen er at mekanismen allerede
finnes, og at `plassering` er brukt færre steder enn man skulle tro.

`bygg_monster` pakker allerede `%`-delen i `(?:...)?` når `krev_komponenttype` er
usann. Plasseringen er samme grep på den andre enden av strengen.

Og `plassering` leses bare tre steder utenfor parseren selv: feltet på `TfmId`,
`global_forekomst`, og feilmeldingene. `global_forekomst` har én bruker — K6.
Hele rippelen går altså gjennom ett uttrykk.

To dommer må dessuten holde følge med hverandre: `bygg_monster` avgjør om en verdi
er *gyldig*, `ligner_tfm_id` avgjør om den er *gjenkjennelig*. Sistnevnte krever to
av tre markører (`++`, `=`, `-`). Uten `++` gjenstår `=` og `-`, altså to — så
gjenkjenningen tåler endringen uten at noe røres. Det er prøvd, ikke antatt.

## Goals / Non-Goals

**Mål:**
- Standardoppsettet skal oppføre seg nøyaktig som i dag. Endringen skal være
  usynlig for alle som ikke slår den på.
- Ett sted som avgjør hvilke deler som kreves, delt av mønsteret og av meldingene,
  slik at de ikke kan komme i utakt.
- K6 skal fortsatt finne duplikater på tvers av fagmodeller — det er evnen som
  gjør kontrollen verdt noe.

**Ikke mål:**
- En generell påkrevd-bryter per del. Systemet og komponenten er selve TFM-en;
  en konfigurasjon som kunne slå dem av ville vært et sted å skru seg ut av
  standarden uten å merke det.
- MMI-styrt krav. «Tidlig modell», ikke «tidlig objekt» — se beslutningen under.
- Å endre hva K6 gjør når plassering er påkrevd. Dagens oppførsel er riktig der.

## Decisions

### Kravet styres flatt, ikke av MMI

`krev_plassering` er en innstilling for kjøringen, ikke en regel per objekt. Du
kjører med et oppsett som passer fasen modellen er i — `tidligfase.toml` og
`leveranse.toml` er to filer, ikke to grener i koden.

*Vurdert og forkastet:* å kreve plassering først over et gitt MMI-nivå. Mer tro
mot virkeligheten, siden en modell sjelden er i én fase overalt, men det
forutsetter MMI som ikke alltid finnes, og det ville flettet dette sammen med
K7s uavklarte MMI-spørsmål. To uavklarte ting i én endring er én for mye.

Det er verdt å merke at MMI nå har dukket opp som faseport to ganger — her, og i
K7s TODO om «prosjektert, ikke tegnet». Blir svaret fra en RIE klart, kan det
være ett design og ikke to. Denne endringen stenger ikke for det.

### Identiteten bygges av delene som finnes

`global_forekomst` utelater `++`-leddet når plasseringen mangler:

```
++115080=3600.001.04-JVZ001   ->  "++115080=3600.001.04-JVZ001"
        =3600.001.04-JVZ001   ->  "=3600.001.04-JVZ001"
```

De to nøklene er ulike, så en ID med plassering og en uten kolliderer aldri.

*Vurdert og forkastet:* å normalisere plasseringen bort for alle når den er
valgfri. Det ville fanget en halvferdig merking der noen objekter har fått
byggnummer og andre ikke — men til gjengjeld meldt to bygg med samme system og
komponent som duplikater. Et falskt funn i en unikhetskontroll er dyrere enn et
uteblitt: det lærer brukeren å overse kontrollen, og da er også de ekte funnene
tapt.

*Vurdert og forkastet:* å la kildefila tre inn for manglende plassering. Fjerner
falske positiver på tvers av bygg, men da finner ikke K6 lenger duplikater på
tvers av RIE og RIV — nettopp det demoen viser at den kan.

### Én kilde til hvilke deler som kreves

`bygg_monster` og `_forklar` skal lese samme sted. Skrevet hver for seg kunne
mønsteret avvist en verdi mens meldingen etterlyste noe annet — den feilen er
allerede rettet én gang i dette prosjektet, da de to regexene ble slått sammen
til én funksjon med kvantorene som eneste forskjell.

Konkret: `_forste_avvik` hopper over en del som ikke kreves, framfor å ha sin egen
liste over hva som kan mangle.

## Risks / Trade-offs

**En verdi kan bli gyldig og ugjenkjennelig samtidig** → `=3600.001.04` har bare
én markør og faller under terskelen i `ligner_tfm_id`, mens `=3600.001.04-JVZ001`
har to og går klar. Terskelen er altså trygg for hele TFM-ID-er, men en kraftig
forkortet verdi vil bli lest som fraværende framfor som ugyldig. Det er riktig
oppførsel — en streng med ett skilletegn er ikke bevis for noe — men det er verdt
å kjenne, og det er derfor spesifikasjonen prøver gjenkjenningen eksplisitt.

**Halvferdig merking skjuler duplikater** → Har ett objekt fått byggnummer og et
annet ikke, er de to nøkler og K6 tier. Bevisst valgt, se beslutningen over. Verdt
å ta opp igjen hvis noen faktisk brenner seg på det; da vet vi at det er ekte.

**`TfmId.plassering` blir valgfri for alle** → Også for prosjekter som krever den.
Typen sier da ikke lenger at verdien finnes, selv når konfigurasjonen garanterer
det. Prisen er at kode som leser feltet må tåle `None`. Alternativet — to typer,
eller en påstand ved parsing — er dyrere enn det ene uttrykket som faktisk bruker
feltet.

## Migration Plan

Ingen. Standardverdien er `true`, som er dagens oppførsel. Et prosjekt tar
endringen i bruk ved å sette `krev_plassering = false` i sitt eget oppsett.

## Open Questions

Ingen som kan utsettes uten å endre spesifikasjonen eller oppgavene.
