## Why

Alle TFM-verdier der de tre strukturmarkørene finnes, får samme melding, uansett
hva som faktisk er galt. Målt på ni ulike innholdsfeil:

```
++11508=3600.001.04-JVZ001      5 siffer i plasseringen
++1150800=3600.001.04-JVZ001    7 siffer
++115080=360.001.04-JVZ001      3 siffer i systemkoden
++115080=3600.1.04-JVZ001       1 siffer i løpenummeret
++115080=3600.001.4-JVZ001      1 siffer i undernummeret
++115080=3600.001.04-jvz001     små bokstaver
++115080=3600.001.04-JV001      2 bokstaver i komponentkoden
++115080=3600.001.04-JVZ01      2 siffer i komponentløpenummeret
…%JVZ.1.008                     kort typeløpenummer
```

Alle ni gir: *«… følger ikke TFM-grammatikken. Forventet formen
++NNNNNN=NNNN.NNN.NN-BBBNNN (N=siffer, B=bokstav)»*

Verktøyet vet nøyaktig hva som er galt — regexen som avviste strengen er bygget
fra grammatikken, og hver del har et forventet antall tegn — men meldingen sier
det ikke. Mottakeren må selv telle sifre mot en formmal for å finne ut hvilken av
de sju delene som svikter.

`_forklar` sin egen docstring lover noe annet:

> *En melding som «forventet 6 siffer etter ++, fant 5» er verdt mer i en BCF-sak
> enn «matcher ikke mønsteret».*

Det løftet er ikke innfridd. Dette er tredje og siste trinn i stigen fra kravet
«Meldingens presisjon skal svare til hva verktøyet vet»: de to første skiller
fremmede verdier fra nesten-treff, dette skiller nesten-treffene fra hverandre.

## What Changes

- **Meldingen navngir delen som svikter og hva som var forventet.** «Plasseringen
  har 5 siffer, forventet 6» i stedet for en formmal mottakeren må telle mot.
- **Bare den første feilen meldes.** Har verdien flere avvik, nevnes det første;
  neste kjøring tar det neste. Det følger mønsteret `_forklar` allerede har for
  manglende markører, og holder meldingen kort nok for en BCF-tittel, som kuttes
  på 100 tegn.
- **Forventningene hentes fra grammatikken, ikke fra en ny liste.** Sifferantallene
  er allerede data i `tfm-sjekk.toml` (§14). En egen tekstmal ville kunne komme i
  utakt med regexen som faktisk avviser strengen.
- **Den generiske meldingen beholdes som siste utvei.** Klarer verktøyet ikke å
  peke på en bestemt del, er formmalen fortsatt bedre enn ingenting.

## Capabilities

### New Capabilities
<!-- Ingen. Dette utvider et krav som allerede finnes. -->

### Modified Capabilities
- `verdiuttrekk`: kravet «Meldingens presisjon skal svare til hva verktøyet vet»
  utvides med tredje trinn i stigen. Det dekker i dag at en fremmed verdi ikke skal
  beskrives som om den mangler en bestemt del, og at et nesten-treff skal få
  spesifikk anvisning. Nå skal også en verdi der alle delene finnes få vite hvilken
  del som er feil, og hva som var forventet.

## Impact

**Kode:** `parser.py` — `_forklar` alene. Ingen kontroll, rapport eller
konfigurasjon berøres.

**Meldingene endres.** Tekstene er brukersynlige og går i BCF, HTML, XLSX og CSV.
Ingen test låser dagens generiske ordlyd fast som forventet resultat, men
K2-meldingen i demoen endres, og det er verdt å se på.

**Determinismen er urørt.** Samme verdi gir samme melding; BCF-fila er fortsatt
byte-identisk med fast `--opprettet`.

**Prøving:** de ni strengene over dekker hver del av grammatikken. Den ekte prøven
er en modell med reelle merkefeil — men til forskjell fra tidligere endringer er
det her lite som kan overraske: inndataene er strenger, ikke IFC-struktur.
