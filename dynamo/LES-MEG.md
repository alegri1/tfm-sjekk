# Funn tilbake til Revit, via Dynamo

Fra §11-samtalen: *«Skriving tilbake til Revit, får schedule som man kan gå
gjennom og fikse feilene fortløpende.»* Funnet er ikke leveransen — rettingen
er det, og den skjer i Revit.

Dette er den letteste veien dit. Ingen plugin, ingen installasjon: et
Python-skript i en Dynamo-graf.

## Slik henger det sammen

```
tfm-sjekk sjekk ... --ut rapport
                          │
                          ▼
                   rapport/funn.csv
                          │
   ┌──────────────────────┴───────────────────────┐
   │  Dynamo                                       │
   │                                               │
   │  File Path ─────────────────────────> IN[0]   │
   │  GetParameterValueByName(TFM) ──────> IN[1]   │
   │                                               │
   │            tfm_til_revit.py                   │
   │                    │                          │
   │                    ├── OUT[0]  avvikstekster  │
   │                    └── OUT[1]  tallene        │
   │                          │                    │
   │  Element.SetParameterByName("TFM_Avvik") <────┤
   └───────────────────────────────────────────────┘
                          │
                          ▼
              Schedule filtrert på TFM_Avvik ≠ tom
```

## Oppsett i Revit, én gang

1. Lag en **prosjektparameter** eller delt parameter `TFM_Avvik`, type **Tekst**,
   på de kategoriene du sjekker (Electrical Fixtures, Air Terminals, …).
2. Lag en schedule med kolonnene du vil gå gjennom, pluss `TFM_Avvik`.
3. Filtrer schedulen på `TFM_Avvik` **is not empty**.

Da har du en arbeidsliste som tømmer seg selv etter hvert som du retter — kjør
grafen på nytt, og radene forsvinner.

## Grafen

1. **Python Script**-node, lim inn hele `tfm_til_revit.py`. Sett antall inputs
   til **2**.
2. `File Path` → `IN[0]` — pek på `rapport/funn.csv`
3. `All Elements of Category` → `Element.GetParameterValueByName` med
   TFM-parameteren → `IN[1]`
4. Elementene selv går rett til `Element.SetParameterByName` — de skal ikke
   innom Python-noden.
5. `OUT` er en liste med to ting. Bruk `List.GetItemAtIndex`:
   - indeks 0 → avvikstekstene → `Element.SetParameterByName("TFM_Avvik")`
   - indeks 1 → tallene → en `Watch`-node

## Les tallene før du stoler på resultatet

`OUT[1]` finnes fordi en kobling som treffer null elementer ser **nøyaktig ut
som** en modell uten avvik. Det er samme tvetydighet som «ingen funn» kontra
«ingenting sjekket», og den skal ikke gjentas her.

| Tall | Hva du ser etter |
|---|---|
| `funn_i_fila` | stemmer med rapporten? |
| `elementer_med_tfm` | leste Dynamo faktisk TFM-parameteren? Er den 0, er parameternavnet feil |
| `elementer_med_avvik` | selve resultatet |
| `funn_uten_nokkel` | funn som ikke kan kobles — se under |
| `tfm_verdier_uten_element` | TFM-verdier med funn som ingen element har. Er lista lang, er koblingen feil |

Er `elementer_med_avvik` 0 mens `funn_i_fila` er 17, har koblingen bommet — ikke
modellen din.

## Hva som ikke kan kobles, og hvorfor

Koblingen skjer på **TFM-verdien**, ikke på GUID. Begge sider har TFM-verdien
garantert, og det er den du skal rette uansett.

IFC-fila bærer riktignok en `GlobalId` per objekt, men den er ikke Revits
`UniqueId`. Revits IFC-eksportør utleder den ene av den andre på en måte som
avhenger av eksportinnstillinger, og en nøkkel som stille gir null treff er
verre enn ingen nøkkel i det hele tatt.

Følgen er at to slags funn ikke kan festes til et element:

- **K1, objektet mangler TFM.** Det har ingen verdi å koble på. Men det trenger
  heller ingen kobling: i Revit finner du dem ved å filtrere schedulen på tom
  TFM-parameter.
- **K7 om mastera.** «Dette systemet står i mastera og er ikke modellert» handler
  ikke om et objekt i det hele tatt.

Begge telles i `funn_uten_nokkel`, så du ser hvor mange det gjelder.

Har modellen en `IfcGUID`-parameter fra eksporten, kan du sende **den** som
`IN[1]` i stedet for TFM-verdien. Da matches det på `global_id`-kolonnen, og
også K1-funnene treffer. Prøv det — det er den bedre veien hvis den finnes.

## En Revit-modell å prøve mot

Du trenger en `.rvt` med TFM-verdier for å kjøre grafen. Den enkleste er å la
Revit lage den av en IFC vi allerede har:

```bash
uv run python eksempler/lag_demomodell.py
uv run tfm-sjekk sjekk eksempler/visning-2x3.ifc --ut rapport-2x3
```

Åpne så `eksempler/visning-2x3.ifc` i Revit — `File → Open → IFC` — og bruk
`rapport-2x3/funn.csv` som `IN[0]`.

**Bruk 2x3-fila, ikke `visning.ifc`.** De har samme innhold, men Revits
IFC-importør åpner IFC 2x3 langt mer pålitelig enn IFC4, og 2x3-fila er skrevet
med `CoordinationView_V2.0` — MVD-en importøren forventer. IFC4-fila bruker
`ReferenceView`, som er ment for lesing, og Revit vegrer seg.

Fordelen med denne veien: verdiene på begge sider kommer fra samme fil, så
treffer ikke koblingen, er det skriptet som er galt — ikke dataene.

**Finn parameternavnet først.** Hva Revit kaller TFM-egenskapen etter en
IFC-import avhenger av importinnstillingene. Kjør denne i en Python-node med ett
element som `IN[0]`:

```python
OUT = sorted(p.Name for p in IN[0].Parameters)
```

Se etter `TFM`, eventuelt noe som `TFM11_Forekomst.TFM`. Det navnet er det du
gir `Element.GetParameterValueByName`.

## Hva som er prøvd, og hva som ikke er det

**Prøvd**, i `tests/test_dynamo.py`, mot filer skrevet av verktøyets egen
CSV-skriver: lesing av fila, at BOM-en håndteres, hvilke verdier som duger som
nøkkel, at MMI-verdien i et K9-funn ikke forveksles med en TFM-ID, at et funn
uten egen nøkkel finner den hos en søskenrad, rekkefølgen ut, nedkortingen ved
mange funn, og at tallene skiller null treff fra ingen avvik.

**Ikke prøvd:** selve Dynamo-kjøringen. Her finnes verken Revit eller Dynamo.
Skallet nederst i skriptet — `IN`/`OUT` — er skrevet etter Dynamos konvensjon,
men det er du som er den første som kjører det.

Skriptet er skrevet for både IronPython 2.7 og CPython3, siden Dynamo bruker
begge avhengig av versjon og nodetype. Derfor ingen f-strenger og ingen
typeannotasjoner, og derfor er `dynamo/` unntatt fra `UP`-reglene i ruff.
