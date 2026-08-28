## Context

Se proposal.md — Why. `_finn` har tre nivåer, og alle tre returnerer på første
treff:

```
1  konfigurert sett + konfigurert felt      løkke over pset_navn  — rekkefølgen er OPPSETTETS
2  konfigurert felt i hvilket som helst sett løkke over egenskaper — rekkefølgen er FILAS
3  konfigurert sett + gjenkjennelig verdi    leser alle felter, så velger
```

Steg 1 er allerede stabilt: rekkefølgen er brukerens egen liste i
`tfm-sjekk.toml`, og at den første vinner er en dokumentert regel.

Steg 2 er det som gjør utfallet avhengig av fila. Steg 3 leser alt før den
velger — det er den løsningen som allerede finnes i koden for samme problem.

## Goals / Non-Goals

**Goals:**
- Samme modell gir samme verdi, uansett hvordan eksportøren sorterte.
- To uenige verdier blir synlige framfor at én velges i stillhet.

**Non-Goals:**
- **Verktøyet skal fortsatt velge én.** Uten en valgt verdi kan ingen kontroll
  kjøre, og «vi vet ikke» er et dårligere svar enn «vi valgte denne, og her er
  den andre».
- Ingen ny regel for hvilken verdi som er den rette. Det vet bare den som merket
  modellen.
- Steg 1 røres ikke. Rekkefølgen der er brukerens egen.

## Decisions

### Steg 2 sorterer på egenskapssettets navn

Finnes feltet i flere ukonfigurerte sett, velges det med alfabetisk første navn.

Alternativene var å velge det korteste navnet, eller det som ligner mest på et
konfigurert. Begge er regler noen må lære seg. Alfabetisk er vilkårlig, men
**forutsigbart og forklarlig i én setning** — og valget er uansett ikke et svar
på hvilken verdi som er riktig. Det er bare en garanti for at svaret ikke endrer
seg.

Det er samme slag valg som at det lengste mønsteret vinner i `[fagmodell]`: en
regel som ikke trenger å være klok, bare stabil og skrevet ned.

### Meldingen er et funn, ikke en linje i dekningen

To uenige TFM-verdier er noe galt i **modellen**, ikke i kjøringen. D1, D2 og D3
handler om hva verktøyet fikk gjort; dette handler om hva som står i fila.

Det tilsier en K- eller T-kontroll. `T1` er allerede «komponenttypen står to
steder og de er ikke enige» — samme form, ett hakk ut: to *verdier* står to
steder og er ikke enige. En T2 ved siden av T1 er den ærligste plasseringen.

### Graden er feil, ikke advarsel

D1–D3 er advarsler fordi de handler om kjøringen og ikke skal stenge porten.
Dette er en motsigelse i modellen: to påstander om samme objekt som ikke kan være
sanne samtidig. T1 er feil av samme grunn.

### `Verdikilde` bærer den forkastede kandidaten

Feltet finnes allerede — `forkastet_verdi` brukes av `FORKASTET`. Her trengs
også hvilket sett den sto i, så det må utvides eller få et søsken.

At kilden bæres gjennom prosessgrensa som ren data er en bærende regel i
`modell.py`, og den holder: dette er strenger, ikke IFC-objekter.

## Risks / Trade-offs

**Steg 2 blir tregere** → Den må nå se alle settene framfor å stoppe på første.
Antallet egenskapssett per objekt er lite — Snowdon har fire til seks — og
uttrekket er ikke der tiden går.

**En modell etter en Revit-runde kan ha mange like par** → Derfor meldes bare
uenige. Det er hele grunnen til at «like meldes ikke» er et eget krav.

**T2 kan bli støyende på en modell med systematisk dobbeltmerking** → Er alle
uenige, er det samme mønster som D2: en konvensjonsfeil framfor enkeltfeil. Men
her vet vi ikke nok til å si det ennå, og en terskel ville vært et tall uten
begrunnelse. Ser vi det i praksis, er det en egen sak.
