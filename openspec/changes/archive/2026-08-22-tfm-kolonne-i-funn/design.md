## Context

Se `proposal.md` for hvorfor. Det som former løsningen er hvor verdien allerede
finnes.

`Funn.for_objekt` får objektet inn og setter i dag `verdi` til
`verdi if verdi is not None else objekt.tfm_forekomst`. Alt som trengs er å lese
`objekt.tfm_forekomst` én gang til, uten omveien om standardverdien. Ingen kontroll
må endres, og ingen kontroll kan overstyre det nye feltet — det er hele poenget.

`Funn` kan også lages direkte, uten objekt: K7 gjør det for meldingene om mastera.
De har verken `global_id` eller TFM, og skal ikke ha det.

## Goals / Non-Goals

**Mål:**
- Ett felt som alltid betyr det samme, uansett hvilken kontroll som meldte.
- De to maskinlesbare formatene skal tilby de samme feltene.
- Koblingen i Dynamo skal si hvilken vei den brukte, ikke bare hva den fant.

**Ikke mål:**
- Å endre hva `verdi` betyr. Den er riktig som den er; det var beskrivelsen som
  løy.
- Å utvide HTML-rapporten. Den leses av et menneske som allerede ser TFM-verdien.
- Å endre BCF. Den peker på objekter med GlobalId og trenger ingen tekstnøkkel.

## Decisions

### Feltet settes i `for_objekt`, ikke av kontrollene

`Funn.tfm` fylles av `for_objekt` fra `objekt.tfm_forekomst`, og har ingen
parameter kontrollene kan sende inn.

Det er en bevisst innsnevring. `verdi` er overstyrbar, og det er nettopp
overstyringen som gjorde den ubrukelig som nøkkel. Et felt som skal kunne stoles
på må ikke kunne settes av den som melder funnet.

*Vurdert og forkastet:* å la `tfm` være en vanlig parameter med
`tfm_forekomst` som standardverdi. Det ville sett symmetrisk ut og gjenskapt
akkurat den feilen vi retter.

### Kolonnen står før `verdi`

I CSV-en: `... kildefil, tfm, verdi`. Objektets identitet først, så det funnet
handler om. Den som leser fila i en teksteditor ser da nøkkelen ved siden av de
andre identitetsfeltene, ikke i den andre enden av raden.

### XLSX får norsk etikett, CSV får feltnavnet

CSV-kolonnene er modellens feltnavn, som er det skript forventer. XLSX har
allerede en egen tabell med norske etiketter og bredder, og følger den:
`TFM` ved siden av `TFM-verdi`.

De to etikettene ligner hverandre med vilje. Feltene *er* like for de fleste funn;
det er unntaket som er poenget, og et navn som skjulte likheten ville vært mer
forvirrende enn opplysende.

### Dynamo velger vei og sier fra

Skriptet leser `tfm`-kolonnen når den finnes. Mangler den, brukes dagens
søskenrad-utledning. Statistikken får et felt som sier hvilken av dem som ble
brukt.

Det følger prinsippet resten av verktøyet bygger på: **et resultat skal si hva det
hviler på.** En eldre `funn.csv` gir et svakere resultat, og forskjellen skal være
synlig framfor å måtte gjettes.

*Vurdert og forkastet:* å kreve kolonnen og fjerne utledningen. Enklere kode, men
en rapport fra i går slutter da å virke — og den som har en liggende, får en feil
i stedet for et resultat.

## Risks / Trade-offs

**To felter som ligner på hverandre** → `tfm` og `verdi` er like for de aller
fleste funn, og det er lett å velge feil. Spesifikasjonen prøver derfor eksplisitt
at de kan være ulike, og navnene er valgt for å ligne: skjuler man likheten, blir
forvirringen større, ikke mindre.

**Fallbacken blir sjelden brukt og lite prøvd** → Den er allerede dekket av
testene som finnes, og de kjører mot rader uten `tfm`-kolonne. Blir kolonnen en
gang obligatorisk, er det testene som avgjør om fallbacken kan fjernes.

**Kolonnerekkefølgen endres i en fil andre leser** → CSV-en er nøklet på
kolonnenavn, ikke posisjon, i alt vi selv skriver. En konsument som leser på
posisjon ville brutt — men den kontrakten har aldri vært lovet, og
`funnformat`-spesifikasjonen sier nå eksplisitt at felter er navngitte.

## Migration Plan

Ingen. Et felt kommer til; ingen forsvinner eller endrer betydning. En eksisterende
leser som plukker kolonner ved navn merker ingenting.

## Open Questions

Ingen som kan utsettes uten å endre spesifikasjonen eller oppgavene.
