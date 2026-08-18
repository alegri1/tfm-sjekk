## Context

Se `proposal.md` for hvorfor. Kravet står i `specs/verdiuttrekk/spec.md`.

To ting i dagens kode former løsningen:

- Regexen bygges fra `Grammatikk` i `bygg_monster`, med sifferantall som data. Når
  den ikke matcher, vet vi at *noe* er galt, men ikke hva — `re` sier bare nei.
- `_forklar` går allerede gjennom strukturmarkørene og melder den første som
  mangler. Mønsteret finnes; det er innholdet i delene som ikke er dekket.

## Goals / Non-Goals

**Goals:**
- Meldingen skal peke på delen som svikter, med forventet og funnet verdi.
- Forventningene skal komme fra samme `Grammatikk` som regexen, slik at de ikke
  kan komme i utakt.

**Non-Goals:**
- Ingen endring i hva som *godtas*. Dette handler bare om hva som sies om det som
  allerede er avvist.
- Ingen liste over flere avvik. Avgjort med brukeren: første avvik, som i dag.

## Decisions

### En løs regex som fanger delene, og så sammenligning mot grammatikken

Regexen som avviser strengen kan ikke si hvor den ga opp. Løsningen er en
parallell, løs regex med samme form men uten kravene: sifferantall som `\d+`,
bokstaver som `[A-Za-zÆØÅæøå]+`. Den matcher enhver TFM-lignende streng og fanger
hver del for seg. Så sammenlignes hver del mot `Grammatikk`, i lesretning, og
første avvik meldes.

Vurdert og forkastet:

*Å bygge regexen trinnvis og prøve prefiks etter prefiks* — man ville da funnet
hvor matchingen ryker, men ikke hvorfor, og meldingen ville blitt «feilen er et
sted etter systemkoden».

*En egen regex per del* — samme resultat, men syv mønstre å holde i takt med
grammatikken i stedet for ett.

Den løse regexen bygges av samme funksjon som den strenge, fra samme
`Grammatikk`-objekt, med kvantorene som eneste forskjell. Da kan de ikke beskrive
ulik form.

### Delene har norske navn, ett sted

Meldingen trenger «plasseringen», «systemets løpenummer», «komponentkoden». Navnene
legges i én tabell ved siden av grammatikken, slik at en ny del i grammatikken ikke
kan få et navn i én melding og et annet i en annen.

### Den generiske meldingen beholdes

Matcher heller ikke den løse regexen, vet vi fortsatt ikke hvilken del som svikter.
Da er formmalen bedre enn ingenting, og kravet sier eksplisitt at den er siste
utvei. Det er ikke en teoretisk gren: en verdi kan ha alle tre markørene i feil
rekkefølge.

## Risks / Trade-offs

**To regexer å holde i takt** → Mildnes ved at begge bygges fra samme funksjon og
samme grammatikkobjekt. En test som sammenligner hva de to godtar for de samme
strengene fanger det om de likevel skulle sprike.

**Meldingene er brukersynlige og endres** → Ingen test låser dagens ordlyd som
forventet resultat, men K2-meldingen i demoen blir en annen. Det er hele hensikten;
demorapporten bør leses igjennom etterpå.

**Første avvik kan kreve flere runder** → Bevisst valgt. En modell med systematisk
feil sifferantall vil ha samme avvik overalt, så én runde retter alt; en modell med
spredte feil er uansett flere runder.
