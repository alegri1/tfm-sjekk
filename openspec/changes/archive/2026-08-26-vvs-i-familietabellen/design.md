## Context

Se proposal.md — Why. Det som styrer framgangsmåten er at `familiekode` treffer
på **begynnelsen av familienavnet**:

```python
familie = (navn or "").split(":")[0].strip()
for nøkkel, koder in FAMILIER:
    if familie.startswith(nøkkel):
        return koder
return STANDARD
```

En tabell bygget på gjettede navn treffer ingenting, og alt faller til
`STANDARD = ("4390", "QLX")` — en elektro-restkode. Modellen ville sett merket
ut og vært systematisk gal, som er nøyaktig feilen endringen skal fjerne.

Sanitærfamiliene i arkitektmodellen er hentet ut og er ekte:

    Sink Vanity-Round (31), Sink Kitchen-Island (22), Toilet-Domestic-3D (21),
    Sink-Wall-Barrier Free-3D (15), Toilet-Commercial-Wall-3D (15),
    Shower Stall - Rectangular (11), Shower Stall with Seat (10),
    Plumb_Floor Sink (3), Sink-3 Basin, Sink-Produce, Hand Sink, Mop Sink_Rect

Men det er **arkitektens** utstyr. RIV-modellene bærer rør, ventiler, aggregater
og ventiler som ikke finnes i ARK, og HVAC-navnene finnes ingen steder på denne
maskinen.

## Goals / Non-Goals

**Goals:**
- Én tabell dekker alle fag, slik at grafen ikke må byttes per modell.
- Hver rad er utledet av et familienavn noen har sett i en ekte modell.
- Kodene er like fiktive som de elektro, og det står.

**Non-Goals:**
- Ingen ny kontroll, ingen endring i `tfm-sjekk`. Tabellen er data i et skript
  verktøyet aldri leser.
- Ingen automatisk gjenkjenning av fag. Familienavnet er nøkkelen, som før.
- Ingen VVS-spesifikk `STANDARD`. Se under.

## Decisions

### Familienavnene måles, de gjettes ikke

Tabellen skrives **etter** at HVAC og Plumbing er eksportert til IFC, og
navnene er lest ut av filene.

Dette er den samme regelen som gjorde at demomappa sluttet å drive: et navn
skrevet av et menneske er sant i det øyeblikket det skrives og aldri etterpå.
Forskjellen her er større, ikke mindre — en bomsjanse per familie, og hver bom
gir et objekt merket med feil fag.

*Alternativ vurdert:* skrive tabellen på Revits standard familienavn og la
`elementer_med_tfm` i sammendraget avsløre bommene. Skriptet er bygget for det
— ukjente familier får `STANDARD` framfor å hoppes over, nettopp så en rapport
viser hva som er ukjent. Men `STANDARD` er `("4390", "QLX")`, altså elektro, og
i en VVS-modell er en elektro-restkode verre enn ingen kode.

### Én tabell, ikke én per fag

VVS-navnene kolliderer ikke med de elektro — «Air Terminal» og «Downlight» deler
ingen begynnelse. En samlet tabell betyr at grafen kan kjøres mot hvilken som
helst modell uten å byttes, og at én test fortsatt holder de to filene
synkronisert.

`tests/test_merking.py` passer allerede på at ingen nøkkel skygger for en annen.
Den regelen blir viktigere med flere rader, og den fanger opp de nye av seg selv.

### `STANDARD` blir stående som elektro

En VVS-modell der noe faller til `4390` er et **signal om at tabellen er
ufullstendig**, ikke noe å skjule. Koden ser feil ut i rapporten, og det er
riktig: den er feil.

*Alternativ vurdert:* la grafen ta en reservekode som inndata, satt per kjøring
ved siden av plasseringen. Det ville gjort en manglende rad usynlig — objektet
hadde fått en plausibel VVS-kode og ingen ville lett etter familien som manglet.
En kode som ser gal ut er mer opplysende enn en som ser rimelig ut.

### Undernummeret blir «00» for VVS

`Circuit Number` finnes ikke på ventilasjons- og sanitærobjekter, så `IN[1]` gir
null, og `kursnummer()` svarer `UTEN_KURS = "00"`.

Det er riktig og ikke en mangel. §4 tolker undernummeret som kurs-/sløyfenummer
bare for NS 3451 kapittel 4 og 5; for 3xx er det et undernummer uten den
betydningen. `er_elektro` er «4» eller «5», så K8 rører ikke VVS uansett — det
er allerede prøvd med `demo-riv.ifc`.

## Risks / Trade-offs

**Tabellen kan være ufullstendig etter første kjøring** → `elementer_med_tfm` og
advarselen om familienavn i `OUT[1]` viser det, og en `4390`-kode i rapporten
peker rett på familien som mangler. Runden gjentas til tabellen dekker.

**Familienavnene er Autodesks, ikke norske** → Står allerede over tabellen: «En
norsk modell har andre — det er FAMILIER du endrer da, ikke koden under.» De
nye radene arver forbeholdet, og de er like eksempelaktige som de elektro.

**§8** → Kodene er funnet på, som de elektro. Det står med store bokstaver over
tabellen, og VVS-radene legges under samme overskrift så forbeholdet ikke kan
leses som om det bare gjaldt elektro.
