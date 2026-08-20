## Context

Se `proposal.md` for hvorfor. Det som former løsningen er at `Kontekst` allerede
har begge halvdelene: `parsede` for verdiene som gikk igjennom, og `parsefeil` for
dem som ikke gjorde det.

`utled` er allerede en ren funksjon `Kontekst -> Oppsettforslag`, og
`Oppsettforslag` er allerede en delta mot `kontekst.config`. Grammatikk føyer seg
inn i den formen uten å endre den.

## Goals / Non-Goals

**Mål:**
- Avgjørelsen skal hvile på noe verifiserbart, ikke på tekstsammenligning av
  feilmeldinger.
- Et sammensatt forslag skal leses tilbake i sin helhet — hver verdi i riktig
  tabell.
- Ingen ny avhengighet, ingen endring bak ifcopenshell-grensa.

**Ikke mål:**
- Å foreslå sifferantall eller andre formkrav. Se avgrensningen i proposal.
- Å foreslå noe når bare noen av feilene løses. Da er det merkefeil, ikke fase.
- Å søke bredt etter kombinasjoner. Kandidatene er to, altså tre sett å prøve.
  Kommer det flere til, må dette tas opp igjen framfor å vokse eksponentielt.

## Decisions

### Kandidaten prøves, den gjettes ikke

For hvert kandidat*sett* bygges en grammatikk med innstillingene slått av, og hver
verdi som i dag feiler forsøkes parset på nytt. Går alle igjennom, foreslås settet.
Settene prøves fra minst til størst, og det første som holder vinner — da blir
ingen innstilling med uten å trengs.

```
verdier som feiler i dag
  ->  {krev_plassering}              alle parser?  nei
  ->  {krev_komponenttype}           alle parser?  nei
  ->  {krev_plassering, krev_komponenttype}  ja  ->  foreslå settet
```

*Vurdert og forkastet:* å sammenligne feilmeldingene og se om de er like. Meldingen
er norsk brukertekst som skal kunne omformuleres uten at oppførsel endres; å bygge
en beslutning på ordlyden ville gjort hver språkretting til en potensiell feil.
Prøven over spør dessuten om nøyaktig det vi vil vite — *løser denne innstillingen
problemet?* — framfor et stedfortredende spørsmål om hvorfor det oppsto.

### Kandidatene er de to bryterne som ikke allerede er slått av

`krev_plassering` og `krev_komponenttype`, hver bare når den er slått på i
`kontekst.config`. Er den allerede av, er det ingenting å foreslå — samme regel som
for egenskapssett og feltnavn, og det som gjør at et forslag brukt om igjen blir
tomt.

### Begge tallene følger med

Forslaget bærer antallet verdier innstillingen løser **og** antallet som allerede
parser. Ett tall alene kan ikke skille en fase fra en feil: «43 verdier løses» ser
likt ut enten de to øvrige parser fint eller det er 40 av dem.

Det er samme lærdom som `dekning` bærer, og som `Oppsettforslag` allerede bruker
til å skille «ingenting å foreslå» fra «ingenting å bygge på».

### `[grammatikk]` skrives etter `ifc_klasser`, før `[pset]`

Skriveren har allerede en kommentar om hvorfor `ifc_klasser` må stå før første
tabell: en toppnivånøkkel etter en tabelloverskrift leses som en nøkkel *i* den
tabellen, fila er fortsatt gyldig TOML og gyldig konfigurasjon, og verdien
forsvinner uten et ord. Den feilen kostet en runde her.

Rekkefølgen blir derfor: toppnivånøkler, så `[grammatikk]`, så `[pset]`. Kravet i
spesifikasjonen er skrevet som en prøve på at *alle* deler av et sammensatt forslag
overlever en tur gjennom `Konfigurasjon.les` — ikke som en påstand om rekkefølge,
slik at den fanger feilen uansett hvordan skriveren senere bygges om.

## Risks / Trade-offs

**En feilmerket modell kan se ut som en tidlig fase** → Er hver eneste verdi merket
uten plassering fordi noen har satt opp malen feil, foreslår verktøyet å godta det.
Det er derfor begge tallene står i fila, og derfor forslaget er et utkast som skal
leses. Verktøyet kan ikke skille «ikke bestemt ennå» fra «gjort feil overalt» —
bare et menneske vet hvilken fase prosjektet er i.

**Forslaget kan skjule en enkeltfeil** → Løser innstillingen alle feilene, tier
verktøyet om hvert enkelt objekt etterpå. Men da var det heller ingen enkeltfeil
å skjule: kravet er nettopp at *alle* skal løses.

**Kombinasjonene vokser eksponentielt** → Med to kandidater er det tre sett, og det
er billig. Kommer en tredje bryter til, blir det sju. Grensen er ikke nådd, men den
finnes, og da skal dette tas opp igjen framfor å legges stille på.

Det var her implementeringen rettet designet: første utkast prøvde kandidatene
uavhengig, og påsto samtidig at en modell uten både plassering og komponenttype
ville få begge foreslått. De to kunne ikke begge stemme. En modell som mangler
begge deler er den tidligste av alle, og å tie der ville vært å svikte i nettopp
det tilfellet dette er laget for.

## Migration Plan

Ingen. Utvidelse av en eksisterende kommando; et forslag uten grammatikk ser ut
som før.

## Open Questions

Ingen som kan utsettes uten å endre spesifikasjonen eller oppgavene.
