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
5. `OUT` er en liste med to ting. Pakk den opp med én `Code Block` på to
   linjer — `x[0];` og `x[1];` — og koble Python-noden inn i `x`:
   - øverste utgang → avvikstekstene → `Element.SetParameterByName("TFM_Avvik")`
   - nederste utgang → tallene → en `Watch`-node

   `List.GetItemAtIndex` gjør det samme, men er fire noder i stedet for én, og
   de to indeksene havner hver sin plass på lerretet. Se steg 9 lenger nede.

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

## To felter som ligner, og som ikke er det samme

`funn.csv` har to felter med TFM-verdier, og forskjellen mellom dem er hele
grunnen til at koblingen virker:

| Felt | Betyr |
|---|---|
| `tfm` | **Objektets egen TFM-verdi.** Alltid den samme for et gitt objekt, uansett hva funnet handler om. Dette er nøkkelen. |
| `verdi` | **Verdien funnet handler om.** For de fleste kontroller det samme som over — men K9 melder om MMI og legger MMI-verdien her. |

For et K9-funn står det `++115080=4310.001.14-QLF105` i `tfm` og `200` i `verdi`.
Kobler du på `verdi`, fester K9-funn seg aldri til noe element.

`OUT[1]` har et felt `nokkel_fra` som sier hvilken vei skriptet gikk:

    "tfm-kolonnen"            rapporten har feltet — dette er det normale
    "utledet av søskenrader"  eldre rapport uten feltet, svakere resultat

Den utledede veien virker for et objekt som har minst ett funn der `verdi` *er*
TFM-ID-en. Har objektet bare et K9-funn, finnes ingen søskenrad å låne nøkkelen
fra, og funnet faller ut i stillhet. Ser du `utledet av søskenrader`, kjør
`tfm-sjekk` på nytt så rapporten får feltet.

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

## Merkingen den andre veien: `tfm_fra_revit.py`

Grafen over skriver funn *tilbake*. Denne skriver merkingen *inn*, og trengs når
modellen ikke har TFM fra før. En umerket modell gir K1 på hvert eneste objekt,
og en rapport der alt er feil sier ingenting om noe.

Halve TFM-ID-en ligger allerede i modellen. Familien sier hva objektet er, og
`Circuit Number` sier hvilken kurs det henger på. Det som mangler er formatet.

```
Element.GetParameterValueByName("Family") ─────────> IN[0]
Element.GetParameterValueByName("Circuit Number") ─> IN[1]
Code Block  "115080";  ───────────────────────────> IN[2]

OUT[0] ──> Element.SetParameterByName("TFM")   ← samme elementer inn i «element»
OUT[1] ──> Watch
```

Parameteren må være **Tekst** og **Instance**, og den må hete det
`revit/TFM-egenskapssett.txt` peker på — ellers kommer verdiene aldri ut i
IFC-eksporten.

**Den legger ikke inn feil med vilje.** `verktoy/legg_til_tfm.py` gjør det, fordi
den bygger en fikstur av en fil. Denne skriver inn i en ekte modell, og det
skiller seg. Det trengs heller ikke: en ekte modell har sine egne hull.

### Prøvd mot Snowdon Towers

Logikken er kjørt tørt mot Autodesks `Snowdon Towers Sample Electrical Solar`,
2426 elementer:

    2426 elementer merket, alle TFM-ID-er unike
    69 systemforekomster
    1021 uten kursnummer — de får undernummer «00»
    140 familier står ikke i tabellen og fikk 4390

Kjørt gjennom `tfm-sjekk` gir det **169 funn, alle K8**: objekter som ikke ligger
på noen kurs. Null K1, null K2, null K6 — merkingen er ren, og hvert funn er et
ekte hull i Autodesks modell.

De 140 ukjente familiene er ikke en feil, men en fattigdom: `FAMILIER`-tabellen
i skriptet kjenner fjorten familienavn. Betyr kodene noe for deg, legg dine egne
inn der. Tabellen er den samme som i `verktoy/legg_til_tfm.py`, og
`tests/test_merking.py` passer på at de ikke driver fra hverandre.

### Bygg grafen, steg for steg

Skrevet for deg som ikke bruker Dynamo daglig. Ti steg, og du bygger lesesiden
ferdig før du kobler til noe som skriver.

**1. Lag parameteren i Revit — før du åpner Dynamo.** Grafen skriver til en
parameter som må finnes fra før. Gjør den ikke det, feiler siste steg med
`No parameter found by that name`, og meldingen sier ingenting om hvorfor.

    Manage -> Project Parameters -> Add...
        Name:                TFM
        Type of Parameter:   Text
        (*) Instance                     <- ikke Type
        Categories:          kryss av de samme du henter fra i steg 5

`Instance` er ikke en detalj. Er den `Type`, deler alle armaturer av samme type
én TFM-verdi, og løpenummeret blir meningsløst.

Navnet må være det samme som `revit/TFM-egenskapssett.txt` peker på i siste
kolonne. Ellers blir verdiene liggende i modellen og kommer aldri ut i
IFC-eksporten.

**2. Åpne Dynamo.** I Revit: fanen `Manage` → `Dynamo`. Velg `New`.

**3. Sett motoren.** Nederst til høyre i Dynamo-vinduet står Python-motoren.
`PythonNet3` er riktig. Er den låst, er den allerede riktig.

**4. Sett kjøremodus til Manual.** Nederst til venstre står `Automatic`. Bytt
til `Manual`. Dette er det viktigste steget: i Automatic kjører grafen i det
øyeblikket du kobler siste ledning, og en skrivenode skriver da til alle
elementene før du har sett på noe.

**5. Hent elementene.** To noder:

- Søk `Categories` — en nedtrekksliste. Velg `Lighting Fixtures` til å begynne
  med. Én kategori er nok til å få grafen til å virke; flere kommer til slutt.
- Søk `All Elements of Category`. Den ligger under `Revit → Selection`, ikke
  under `Categories` — nedtrekkslista er bare en verdi, ikke et bibliotek.

Koble `Categories` → `category`.

**6. Les de to parameterne.** To `Element.GetParameterValueByName`-noder, begge
med `All Elements of Category` inn i `element`. Navnet gis av en `Code Block`
(dobbeltklikk på lerretet):

    "Family and Type";     -> parameterName på den første
    "Circuit Number";      -> parameterName på den andre

Anførselstegnene og semikolonet må begge være der. `Family and Type;` uten
anførselstegn er ikke teksten «Family and Type» — Dynamo leser det som et navn
på noe, lager en inngangsport av det, og sender null videre. Kjennetegnet er at
Code Block-en får en ny port på venstre side.

**7. Se på det du fikk, før du går videre.** Heng en `Watch` på hver av de to og
trykk `Run`. Du skal se familienavn i den ene (`Duplex Receptacle: 20A` eller
liknende) og kursnumre i den andre (`1`, `6,8`, eller tomt).

Er familienavnene tomme eller ser ut som `Revit.Elements.Family`, virker ikke
`"Family and Type"` i din versjon. Prøv i denne rekkefølgen:

    a)  Code Block:  "Family";
    b)  Element.ElementType  ->  FamilyType.Family  ->  Element.Name

Skriptet deler på kolon og bruker bare det som står før, så `Familie: Type`
er like bra som `Familie` alene.

**8. Python-noden.** Søk `Python Script`. Den kommer med to inputs; klikk `+` på
noden én gang, så du har tre. Dobbeltklikk, lim inn hele `tfm_fra_revit.py`,
trykk `Save`. Koble:

    familienavn        -> IN[0]
    kursnumre          -> IN[1]
    Code Block  "115080";   -> IN[2]

**9. Pakk opp de to utgangene.** Python-noden har bare én utgangsport, og
skriptet gir deg to ting gjennom den:

    OUT[0]   TFM-ID-ene, én per element
    OUT[1]   sammendraget, én linje per tall

Lag én `Code Block` med nøyaktig disse to linjene:

    x[0];
    x[1];

Den får da én inngang (`x`, fordi navnet er udefinert) og to utganger, én per
linje. Koble Python-noden inn i `x`. Øverste utgang er TFM-ID-ene, nederste er
sammendraget — heng en `Watch` på den.

Semikolonene må være der, ett per linje.

*Alternativt* to `List.GetItemAtIndex`-noder, med `index` fra hver sin Code
Block (`0;` og `1;`) og Python-noden inn i begge `list`-inngangene. Det virker
like godt, men er fire noder i stedet for én — og de to indeksene havner hver
sin plass på lerretet, der det er lett å sette begge til samme tall. Da får
skrivenoden sammendraget i stedet for TFM-ID-ene, og advarselen du får peker
på noe helt annet.

**Trykk `Run` nå, og les Watch-en.** Står det `2426 elementer merket` og et
lavt tall for ukjente familier, er lesesiden ferdig. Står det `ADVARSEL: ingen
av familienavnene står i tabellen`, er `IN[0]` feilkoblet — gå tilbake til
steg 7.

**10. Først nå kobler du skrivingen.** `Element.SetParameterByName`:

    element         <- SAMME All Elements of Category som i steg 6
    parameterName   <- Code Block  "TFM";      <- med anførselstegn
    value           <- Code Block-ens øverste utgang  (x[0])

Elementene må komme fra den samme noden som parameterne ble lest fra. Henter du
dem fra en annen node, kan rekkefølgen være en annen, og hvert element får
naboens TFM-ID. Det er en feil ingen ser i grafen — dra ledningen fra utgangen
du allerede bruker.

Trykk `Run`. Sjekk et par elementer i Revit før du stoler på resten.

**Flere kategorier.** Legg til én `Categories`-node per kategori, samle dem i en
`List.Create`, og koble den inn i `All Elements of Category`. Du får da en liste
med lister — legg en `List.Flatten` etter, ellers ser skriptet én rad per
kategori i stedet for én per element.

Aktuelle kategorier: `Electrical Fixtures`, `Electrical Equipment`,
`Lighting Fixtures`, `Lighting Devices`, `Data Devices`, `Conduits`,
`Conduit Fittings`.

### Fellene, samlet

Én prøve skiller de fleste av dem fra hverandre: bytt `parameterName` til
`"Comments";` og kjør. `Comments` finnes på praktisk talt alt i Revit. Går det
gjennom, er det parameteren som mangler eller er feil bundet. Feiler det
fortsatt, er det koblingen inn i `element` som er problemet.


| Symptom | Årsak |
|---|---|
| `No parameter found by that name` | Parameteren finnes ikke (steg 1), er ikke bundet til kategorien, eller `parameterName` mangler anførselstegn — `TFM;` lager en inngangsport og sender null, `"TFM";` sender navnet. |
| Grafen skriver før du er klar | Kjøremodus står på `Automatic`. |
| `ADVARSEL: ingen av familienavnene ...` | `IN[0]` gir noe annet enn navn. Se steg 7. |
| Skriptet kaster om ulik lengde | `IN[0]` og `IN[1]` kommer fra ulike elementlister. |
| `SetParameterByName` feiler på noen få elementer | Den fikk `x[1]` — sammendraget — i stedet for `x[0]`. Utgangene står i feil rekkefølge. |
| Watch viser lister i lister | Flere kategorier uten `List.Flatten`. |
| `Ingen elementer inn` | Kategorivalget traff ingenting. En tom liste ser ut som en ferdig merket modell. |
| Verdiene kommer ikke ut i IFC-en | Kartleggingsfila mangler i eksportoppsettet, eller peker på et annet parameternavn. |

### Kursnummeret leses fra Revit, ikke fra IFC-en

Kursen er det eneste leddet i ID-en som ikke kan utledes av objektet selv. I IFC
leses den av navnet på `IfcSystem` — men det navnet er nettopp Revits eget
`Circuit Number`, skrevet ut ved eksport.

Det er også den ene retningen som virker. Kurser overlever eksporten *ut* av
Revit — Snowdon eksporterte 448 `IfcSystem` og 1405 objekter tilordnet en kurs —
men ikke importen *inn* igjen. Se «Hva som ikke kan kobles, og hvorfor».

Et objekt kan ligge på flere kurser; Revit skriver da «6,8». TFM har plass til
én, og den første brukes. Det er en forenkling verdt å vite om.

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
