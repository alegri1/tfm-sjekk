## Context

To kortformer, ett problem. Se proposal.md — Why.

`_tittel` i `rapport/bcf.py` har allerede en setningsgrense-regel, lagt inn i
0.8.2 etter at K2-meldingen ble til «… Objektet er derfor ikk». Den regelen
virker; det som mangler er hva som skjer når den ikke finner noen grense. Da
faller den tilbake på `tekst[: MAKS_TITTEL - 1]`, altså et hardt kutt.

Oppsummeringslinja i `cli.py` er én f-streng som teller to av tre grader og
navngir to av fire filer.

## Goals / Non-Goals

**Goals:**

- Fallback-en i `_tittel` skal gi en avslutning som ser villet ut.
- Oppsummeringslinja skal stemme med rapporten den nettopp skrev.

**Non-Goals:**

- Ikke omskrive kontrollmeldingene så de blir korte nok. Meldingene er skrevet
  for å bli lest i sin helhet i rapporten; å tvinge dem under hundre tegn ville
  gjort dem dårligere der de faktisk leses.
- Ikke endre BCF-ens `Description`. Den er hel i dag og skal forbli det.
- Ikke røre CSV, XLSX eller HTML. De teller allerede alle tre gradene.

## Decisions

### Kuttet gjøres i tre trinn, i denne rekkefølgen

    1. hele teksten             passer den, ingen kutting
    2. siste setningsslutt      finnes en «. » innenfor grensen
    3. siste ordgrense          siste mellomrom innenfor grensen
    4. hardt kutt               siste utvei

Trinn 1 og 2 er dagens oppførsel, uendret. Trinn 3 er det nye, trinn 4 blir
liggende som utvei.

Trinn 4 kan ikke fjernes, og det er verdt å si hvorfor: en tekst uten ett eneste
mellomrom innenfor grensen har ingen ordgrense å kutte ved. Det er ikke
hypotetisk — en TFM-ID er 26 tegn uten mellomrom, og et funn som ramser opp fire
av dem passerer hundre tegn før første mellomrom nødvendigvis dukker opp. Da er
et hardt kutt riktig svar: en halvert identifikator er tydeligere avkuttet enn
en halvert setning, fordi ingen leser en identifikator som språk.

**Vurdert og forkastet:** å øke `MAKS_TITTEL`. Hundre er BCF 2.1-formatets egen
grense, ikke vår.

**Vurdert og forkastet:** å kutte ved komma eller semikolon i tillegg. Det ville
gitt «… er brukt på 2 objekter,» — en avslutning som lover en fortsettelse i
samme setning, og som derfor leses som avkuttet uansett. Ordgrensen er nok.

### Et åpent tegn til slutt fjernes etter kuttet, ikke før

Tegn som `(`, `«` og `-` åpner noe som aldri lukkes. De strippes fra enden av
det som ble igjen, etter at kuttet er gjort.

Rekkefølgen har en grunn: stripper man først, flytter grensen seg og man må
regne på nytt. Etter kuttet er det ett enkelt trinn som bare gjør teksten
kortere, og kortere kan aldri bryte lengdekravet.

### Ellipsen teller med i lengden

`…` er ett tegn og skal inn i budsjettet, ikke legges på etterpå. Dagens kode
gjør dette riktig med `MAKS_TITTEL - 1`, og det skal fortsette å gjelde for alle
trinnene som kutter.

Setningsgrensen (trinn 2) får ingen ellipse. En hel setning som slutter på
punktum er ikke avkuttet — den er kort.

### Oppsummeringslinja bygges fra gradene som finnes

Linja settes sammen av de gradene som faktisk har funn, i rekkefølgen feil,
advarsel, info — alvorligst først, som i resten av verktøyet.

Entallsformen løses med et oppslag per grad framfor en regel. Norsk flertall er
ikke en `+s`: «1 feil / 13 feil», «1 advarsel / 3 advarsler», «1 info / 3 info».
En generell pluraliseringsfunksjon for tre kjente ord ville vært mer maskineri
enn ord.

**Vurdert og forkastet:** å skrive «0 info» når det ikke finnes noen. Det ville
gjort linja lengre uten å si noe. Fraværet av ordet er beskjeden.

### Stiene bygges med `pathlib`, ikke med limte skråstreker

`f"{ut}/rapport.html"` gir `C:\...\rapport\/rapport.html`-blandingen. `ut / navn`
gjør det plattformen gjør.

Filnavnene finnes allerede som fire kall rett over linja. De samles i en liste
når de skrives, så linja ikke kan komme i utakt med hva som faktisk ble skrevet
— det er nøyaktig den utakten som er feilen her.

## Risks / Trade-offs

**Lengre oppsummeringslinje** → Med tre grader og fire filnavn blir linja lang
nok til å brytes i en smal terminal. Filene står allerede på egen linje etter en
pil; gradene er det korte leddet. En kjøring uten infofunn får en linje like
lang som i dag.

**Titlene endrer seg for eksisterende funn** → En BCF laget med denne utgaven
har andre titler enn en laget med forrige, for de emnene som ble kuttet hardt.
Emne-GUID-ene er uendret, så en viewer som allerede har importert en sak kobler
den fortsatt riktig. `funnformat` krever byte-identiske filer for samme funn og
samme utgave av verktøyet; det kravet gjelder innenfor en utgave, og er ikke
brutt.

**Ordgrensen gir kortere titler** → Kutter man ved siste mellomrom, mister man i
snitt et halvt ord plass. Det er byttet: mindre tekst, men teksten som står er
lesbar.
