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

Åpne så `eksempler/visning-2x3.ifc` i Revit og bruk `rapport-2x3/funn.csv`
som `IN[0]`.

**Bruk `File → Open → IFC…`**, ikke `File → Open → Project`. Prosjektdialogen tar
imot filnavnet og gjør så ingenting — uten feilmelding. IFC har sin egen
oppføring i Open-undermenyen.

**Bruk 2x3-fila, ikke `visning.ifc`.** De har samme innhold, men Revits
IFC-importør åpner IFC 2x3 langt mer pålitelig enn IFC4, og 2x3-fila er skrevet
med `CoordinationView_V2.0` — MVD-en importøren forventer. IFC4-fila bruker
`ReferenceView`, som er ment for lesing, og Revit vegrer seg.

Fordelen med denne veien: verdiene på begge sider kommer fra samme fil, så
treffer ikke koblingen, er det skriptet som er galt — ikke dataene.

**Parameternavnet får settnavnet foran.** Revit 2027 importerer
`TFM11_Forekomst`-settets `TFM`-egenskap som parameteren

    TFM11_Forekomst.TFM

Det er den strengen `Element.GetParameterValueByName` skal ha — ikke `TFM`.
Bekreftet ved import av `visning-2x3.ifc` i Revit 2027.

Er du i tvil, eller på en annen Revit-versjon, list navnene selv. Python-node
med ett element som `IN[0]`:

```python
OUT = sorted(p.Name for p in IN[0].Parameters)
```

## Runden etter en retting krever riktig eksportoppsett

`tfm-sjekk` leser en IFC-fil, ikke Revit-modellen. Retter du i Revit, må du
eksportere på nytt før verktøyet ser endringen.

**Og en eksport med standardoppsett inneholder ingen TFM.** Det er prøvd:
en modell med åtte merkede objekter, eksportert med Revits standardinnstillinger,
ga en IFC med bare `Pset_DistributionFlowElementCommon` og
`Pset_QuantityTakeOff`. Verktøyet meldte åtte K1-feil på åtte objekter, og
`tfm-sjekk oppsett` svarte «ingenting å bygge på» — helt korrekt, for verdiene
var ikke i fila.

Revits IFC-eksportør tar bare med sine egne standard-psett med mindre den får
beskjed om noe annet. `revit/TFM-egenskapssett.txt` i dette repoet er en ferdig
utfylt kartleggingsfil som legger TFM, TFM-type og MMI i egenskapssett med de
navnene verktøyet leter etter.

    File > Export > IFC > Edit setup > fanen «Parameter Mapping»
    kryss av «Export user defined property sets»
    filvalget dukker opp ETTER avkryssingen — pek på fila der

Fanen het «Property Sets» i eldre Revit. I 2027 er den delt i Category
Mapping, Property Mapping og Parameter Mapping, og det er den siste som
gjelder. Filvalget er skjult til boksen er krysset av.

Kolonnene i fila skilles med **tabulator**. Med mellomrom leses den uten
feilmelding og uten virkning.

**Prøvd 2026-08-21.** Med fila på plass ga eksporten:

    [TFM11_Forekomst]  TFM        8 objekter
    [TFM11_Type]       TFMType    2 objekter
    [MMI]              MMI        8 objekter

altså nøyaktig navnene standardoppsettet leter etter. `tfm-sjekk oppsett`
svarte «oppsettet dekker modellene som de er», og `sjekk` gikk fra åtte
K1-feil til null — de gjenværende funnene var de ekte: T1-spriket og
MMI-avviket, som begge overlevde runden gjennom Revit.

### Relasjonene overlever ikke denne runden

Ett funn kom til: K8 melder «fant 1 fordeling, men ingen kursgrupper». Talt
opp mot originalen:

    IfcElectricalCircuit        4  ->  0
    IfcGroup                    4  ->  0
    IfcRelAssignsToGroup        4  ->  0
    IfcDistributionPort        14  ->  0
    IfcRelConnectsPorts         7  ->  0
    IfcRelNests                14  ->  0

Objektene og TFM-verdiene overlevde. Strukturen mellom dem gjorde ikke.

**Tapet skjer ved import, ikke ved eksport.** Objektene kommer inn i Revit som
`Generic Models` — IFC-importen lager geometri, ikke elektriske systemer. En
Generic Model kan ikke ligge på en kurs i Revit, så det fantes ingen kurs å
skrive ut igjen. Det finnes heller ingen eksportinnstilling for det; søk i
tilleggets ressursstrenger gir ingen treff på system, circuit eller group.

Konsekvensen for verktøyet: **K8 kan bare arbeide på en IFC eksportert fra en
modell som har ekte MEP-systemer.** Går modellen veien om en IFC-import, er
K8 ute av spill uansett hvor godt merkingen ellers er.

Om en ekte Revit-modell med virkelige elektriske kurser eksporterer dem som
IfcElectricalCircuit, vet vi ikke. Det kan bare en ekte modell svare på, og
det er et spørsmål verdt å stille: *kommer kursgrupperingen med i eksporten
deres?*

Kontrollen sier uansett fra framfor å tie. Uten den linja ville en tom
K8-rapport sett ut som at kursene var i orden.

Dette er et engangsoppsett per prosjekt, og det er en BIM-koordinator-oppgave.
Det er også et spørsmål verdt å stille tidlig: *hvordan er IFC-eksporten deres
satt opp, og kommer TFM-parameteren med?*

## Hva som er prøvd, og hva som ikke er det

**Prøvd**, i `tests/test_dynamo.py`, mot filer skrevet av verktøyets egen
CSV-skriver: lesing av fila, at BOM-en håndteres, hvilke verdier som duger som
nøkkel, at MMI-verdien i et K9-funn ikke forveksles med en TFM-ID, at et funn
uten egen nøkkel finner den hos en søskenrad, rekkefølgen ut, nedkortingen ved
mange funn, og at tallene skiller null treff fra ingen avvik.

**Prøvd i Dynamo**, 2026-08-21, i Revit 2027 med Python-motoren `PythonNet3`
(som er CPython3 under nytt navn — nyere Dynamo har droppet IronPython 2.7).
Grafen kjørte mot `visning-2x3.ifc` importert i Revit og ga de ventede tallene:

    elementer            8
    elementer_med_tfm    8
    funn_i_fila          5
    elementer_med_avvik  4
    funn_uten_nokkel     0

**Fortsatt uprøvd:** Python 2-grenen i `les_funn`. Den kan ikke kjøres her, og
Dynamo-versjonen over bruker den ikke. Den står igjen for eldre Dynamo.

Skriptet er skrevet for både IronPython 2.7 og CPython3, siden Dynamo bruker
begge avhengig av versjon og nodetype. Derfor ingen f-strenger og ingen
typeannotasjoner, og derfor er `dynamo/` unntatt fra `UP`-reglene i ruff.
