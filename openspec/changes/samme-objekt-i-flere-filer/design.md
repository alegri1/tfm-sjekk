## Context

Se proposal.md — Why. Identiteten brukes tre steder, og alle tre er dicter:

```
_etter_id   {global_id: IfcObjekt}   K2, K6, K8 fester funn til en fil
parsede     {global_id: TfmId}       de sju kontrollene som krever tolket ID
parsefeil   {global_id: str}         K2, og D2 siden i dag
```

Alle tre antar at GlobalId er unik i kjøringen. I én fil er den det — IFC krever
det. På tvers av filer krever ingen det, og Revit eksporterer delte objekter inn
i hver lenke.

## Goals / Non-Goals

**Goals:**
- Kollisjonen blir synlig, med filene navngitt.
- Delte objekter utenfor omfanget forblir stille.

**Non-Goals:**
- **Ingen sammenslåing eller forkasting.** Verktøyet skal si fra, ikke gjette.
- Ingen ny nøkkel som gjør identiteten entydig, for eksempel `(kildefil,
  global_id)`. Se under.
- Ingen endring i hvilke funn de øvrige kontrollene gir. Rapporten blir ikke
  riktigere av denne endringen — den blir ærlig om at den ikke er det.

## Decisions

### Vi retter symptomet, ikke årsaken — og det er et valg

Den «riktige» fiksen er å nøkle på `(kildefil, global_id)` overalt. Det ville
gjort funnene korrekte framfor å advare om at de ikke er det.

Vi gjør det ikke nå, av tre grunner:

For det første **rører det alt**: `_etter_id`, `parsede`, `parsefeil`, K2, K6, K8
og D2. En endring i identitetsbegrepet midt i en kodebase er ikke noe man gjør
mens man ser etter noe annet.

For det andre er **K6 tvetydig med begge nøkler.** To objekter med samme GlobalId
i to filer: er det ett objekt telt to ganger, eller to objekter som ved en feil
fikk samme ID? Med en sammensatt nøkkel blir de to objekter, og K6 melder
duplisert TFM — som kan være riktig eller helt misvisende. Ingen nøkkel svarer på
det; bare den som sendte inn filene vet.

For det tredje: er kollisjonen først synlig, er den vanligste årsaken **at noen
sendte inn samme modell to ganger**. Da er handlingen å fjerne den ene fila, ikke
å få verktøyet til å telle den dobbelt riktig.

Blir dette et gjentakende problem hos noen som *skal* ha overlappende filer, er
den sammensatte nøkkelen neste steg. Da vet vi også hva K6 skal svare.

### D3, ikke en utvidelse av D1 eller D2

D1 svarer på om noe var i omfanget. D2 på om det var lesbart. D3 på om
**resultatet er til å stole på** — undersøkelsen er gjort, men den kan ha festet
funn til feil fil.

Tre spørsmål, tre grader å styre hver for seg, og tre meldinger som ikke skal
blandes.

### Advarsel, ikke feil — og grunnen er praktisk

Sendes samme modell inn to ganger, fyrer K6 på hvert eneste merkede objekt.
Exit-koden er da 1 uansett, fra de funnene. D3 trenger ikke å endre porten; den
trenger å **forklare** hvorfor porten stengte.

En advarsel som forklarer et titalls feil er mer verdt enn en feil til.

### Bare objekter i omfanget teller

Snowdon-kjøringen deler to `IfcGrid` mellom tre fagmodeller. De kontrolleres
ikke, ingen funn festes til dem, og parseresultatet deres finnes ikke.
En advarsel der ville stått i hver eneste federerte kjøring — og en advarsel som
alltid står der, leses ikke. Samme vurdering som for unntatte fagmodeller i D1.

## Risks / Trade-offs

**Rapporten blir ikke riktigere** → Nei. Den blir ærlig om at den ikke er det.
Det er skillet mellom «ingen funn» og «ingenting sjekket», flyttet til «funn du
ikke kan stole på plasseringen av».

**En bruker kan lese advarselen som at verktøyet ikke virker** → Meldingen må si
hva som *er* pålitelig: antallet funn og hva de sier. Det er bare hvilken fil de
tilhører som er usikker, og bare for de objektene som deler identitet.

**Vi utsetter den ekte fiksen** → Bevisst, og det står over. Kommer det et
prosjekt som legitimt federerer overlappende filer, er den sammensatte nøkkelen
neste sak — og da vet vi hva K6 skal svare, som vi ikke gjør nå.
