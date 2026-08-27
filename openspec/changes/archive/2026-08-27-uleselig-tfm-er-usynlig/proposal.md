## Why

En TFM-verdi som ikke lar seg tolke gjør objektet **usynlig for sju kontroller**.

`med_tfm()` returnerer bare objekter som parset. Alt annet havner i `parsefeil`,
og de sju kontrollene som leser `med_tfm()` — K3, K4, K5, K6, K7, K8, K9 — ser
dem aldri. K2 melder at syntaksen er gal. Ingenting melder hva det koster.

    ++11508=4310.001.12-QLF005
    → K2: «Plasseringen «11508» har 5 siffer, forventet 6.»

Objektet er nå også uunderøkt for ukjent systemkode, ukjent komponentkode,
duplisert forekomst, master-avvik, kursnummer og MMI. Rapporten sier det ikke.

**Konsekvensen skalerer stygt.** Ett objekt med skrivefeil er en detalj. Men en
systematisk forskjell i merkekonvensjonen — et prosjekt som bruker fem sifre i
plasseringen der oppsettet venter seks — gjør at **hvert eneste objekt faller
ut**. Rapporten viser da en haug K2-funn og ingenting annet, og det ser ut som
om syntaks er det eneste problemet. Alt K3–K9 kunne ha funnet er usynlig.

Det er den samme tvetydigheten `dekning` finnes for å fjerne — «ingen funn» mot
«ingenting sjekket» — én etasje inn. Dekningen svarer i dag på om objektet var i
omfanget. Den svarer ikke på om det var **lesbart nok til å bli kontrollert**.

## What Changes

- Rapporten og konsollen oppgir hvor mange objekter i omfanget som har en
  TFM-verdi verktøyet ikke kunne tolke — per fagmodell, som dekningen ellers.
- K2-meldingen sier hva det koster: at objektet ikke er kontrollert av de
  øvrige kontrollene. Én setning, ikke en liste over kontrollnumre.
- **Faller alle objektene i en fagmodell ut, er det et eget funn.** Da er det
  ikke enkeltfeil, det er en konvensjon som ikke stemmer med oppsettet — og
  handlingen er å se på `[grammatikk]`, ikke å rette objekter ett for ett.

## Capabilities

### Modified Capabilities
- `dekning`: evnen svarer i dag på hvor mye som ble undersøkt og hvilke
  kontroller som ikke kjørte. Den utvides med objekter som var i omfanget, men
  hvis TFM ikke lot seg tolke — de er lest, de er i omfanget, og de er likevel
  ukontrollert av sju kontroller.

## Impact

- `src/tfm_sjekk/kontekst.py`: `dekning()` gir et tall til, eller en ny metode.
- `src/tfm_sjekk/kontroller/k2_syntaks.py`: meldingen sier konsekvensen.
- Ny kontroll for «alt falt ut», eller en utvidelse av D1. Se design.md.
- `src/tfm_sjekk/cli.py` og `rapport/html.py`: tallet vises.

**Prøves hos konsumenten:** kjør demomodellene med `plassering_siffer = 5` i
oppsettet. Da faller alt ut, og rapporten må si det tydelig — ikke bare vise
atten K2-funn. Det er den kjøringen som avgjør om endringen virker.
