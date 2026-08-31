## Why

To objekter i **samme fil** med samme `GlobalId` får verktøyet til å melde en
feil som ikke finnes.

IFC krever unik GlobalId innenfor én fil. Eksportører har likevel produsert
brudd, og filer slått sammen av tredjepartsverktøy bærer dem videre.

```
lest: 0VDuf0V5LOYxfWmWWEBzNF   ++115080=3600.001.04-JVZ001%JVZ.001.008
lest: 0VDuf0V5LOYxfWmWWEBzNF   ++115080=3600.001.04-JVZ002
```

To ulike TFM-er. `parsede` er nøklet på GlobalId, så det andre objektet
overskriver det første — og `med_tfm()` parer da **objekt 1 med objekt 2s
parseresultat**:

```
(IfcObjekt(tfm_forekomst='…JVZ001%JVZ.001.008'),  TfmId(raa='…JVZ002'))
```

Utfallet:

```
K6 feil   Komponentforekomsten «…JVZ002» er brukt på 2 objekter
K6 feil   Komponentforekomsten «…JVZ002» er brukt på 2 objekter
```

**Duplikatet finnes ikke.** De to objektene har hver sin TFM. Verktøyet
konstruerte det ved å slå dem sammen, meldte det som `feil` to ganger, og nevnte
aldri JVZ001 — som står ukontrollert. Dekningen sier «2 av 2 objekter i
omfanget».

D3 fyrer ikke. Den ser bare på tvers av filer, og `delt_identitet` sier det
uttrykkelig:

> Samme identitet flere ganger i SAMME fil er ikke dette. IFC krever unikhet
> der; bryter en fil det, er det en annen sak enn to filer som overlapper.

Det var en bevisst avgrensning, og den var ærlig — men «en annen sak» ble aldri
tatt. Dette er den saken.

**Dette er en annen slags feil enn de fire foregående utgavene rettet.** De
handlet om noe verktøyet ikke sa. Dette er noe det *sier som ikke er sant*, og
en koordinator ville lett etter et duplikat som ikke finnes.

## What Changes

- Går en `GlobalId` igjen i samme fil blant objekter i omfanget, meldes det —
  med **grad advarsel**, som D3, og med filnavnet og antallet.
- Meldingen sier at funnene om de objektene ikke er til å stole på, og at
  årsaken ligger i eksporten framfor i merkingen.
- `tfm-sjekk oppsett` får samme håndtering av `FilFeil` som `tfm-sjekk sjekk`
  fikk i 0.9.3. Den kaller `les_modeller` uten den, så en ødelagt fil gir
  fortsatt traceback og exit 1 der.

Ingen kontroll endrer hva den ser etter. Exit-koden er uendret: en advarsel
stenger ikke porten.

## Capabilities

### Modified Capabilities

- `dekning`: kravet om at samme objektidentitet skal meldes utvides til å gjelde
  innenfor én fil, ikke bare på tvers av fagmodeller. Grunnen kravet finnes for
  — at to objekter kollapser til ett og resultatet ikke er til å stole på —
  gjelder like fullt, og konsekvensen er verre: det oppstår et funn som er
  usant.

## Impact

- `src/tfm_sjekk/kontekst.py` — `delt_identitet`, og docstringen som avgrenser
  den
- `src/tfm_sjekk/kontroller/d3_identitet.py` — meldingen må dekke begge
  tilfellene
- `src/tfm_sjekk/cli.py` — `oppsett`-kommandoen
- `tests/test_dekning.py`, `tests/test_cli.py`

Ingen nye avhengigheter. Ingen dataformater endres.
