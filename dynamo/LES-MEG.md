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

## To sløyfer, ikke én

Det som gjør dette tungt å lese er at engangsjobben og rundejobben står om
hverandre. De er ikke det samme:

| | Hva | Hvor ofte |
|---|---|---|
| **A** | parameter, eksportoppsett, kartleggingsfil, schedule, **grafene** | én gang per prosjekt |
| **B** | eksporter, `tfm-sjekk sjekk`, kjør grafen, rett | hver runde |

**Grafene finnes ferdig.** `dynamo/tfm-sjekk-tfm-fra-revit.dyn` og
`dynamo/tfm-sjekk-tfm-til-revit.dyn` er bygget og kjørt mot Snowdon Towers i
Revit 2027, med alle sju kategoriene koblet. Åpne dem i Dynamo — du skal ikke
bygge dem opp igjen.

To ting må rettes før første kjøring, og begge er valgt for å feile høylytt om
du glemmer dem:

| Graf | Node | Leveres med | Skal være |
|---|---|---|---|
| `fra-revit` | Code Block → `IN[2]` | `"SETT-PLASSERING";` | prosjektets plasseringskode |
| `til-revit` | File Path → `IN[0]` | `C:\prosjekt\rapport\funn.csv` | din egen `funn.csv` |

`merk` nekter å merke med plassholderen, og `les_fil` kaster på en sti som ikke
finnes. En ekte kode i grafen ville vært verre: da hadde en fremmed modell blitt
merket med et annet bygg uten at noe protesterte.

**Sløyfe B er én kommando** når `tfm-sjekk.toml` bærer ruten — se «Den faste
ruten» i README-en:

```toml
modeller = ["eksport/*.ifc"]
ut = "rapport"
```

## Oppsett i Revit, én gang

**Parameteren.** `Manage → Project Parameters → Add…`, navn `TFM_Avvik`, type
**Text**, **Instance**, på de kategoriene du sjekker — Electrical Fixtures,
Electrical Equipment, Lighting Fixtures, Lighting Devices, Data Devices,
Conduits, Conduit Fittings.

`Instance`, ikke `Type`: avviket gjelder ett objekt, ikke alle av samme slag.

**Schedulen.** `View → Schedules → Multi-Category`.

Ikke `Schedule/Quantities`. Den låser deg til én kategori, og funnene ligger
spredt over alle sju. En multikategori-schedule tar dem i én liste.

| Fane | Hva |
|---|---|
| `Fields` | `Family and Type`, `TFM`, `TFM_Avvik`, `Level` |
| `Filter` | `TFM_Avvik` → **`is not empty`** |
| `Sorting/Grouping` | `Level`, så `TFM`. La `Itemize every instance` stå på. |

Filteret er det som gjør lista til en arbeidsliste framfor en oversikt. Uten det
får du hele modellen.

Finner du ikke `TFM_Avvik` blant feltene, er den ikke bundet til kategoriene.

**Slik brukes den.** Klikk en rad og trykk `Highlight in Model` på båndet. Revit
zoomer til objektet i en åpen 3D- eller planvisning. Det er den knappen som gjør
schedulen til et verktøy og ikke en tabell.

**Raden forsvinner ikke når du retter objektet.** `TFM_Avvik` er en tekst Dynamo
skrev inn, og den vet ikke at du har gjort noe. Lista tømmer seg først når hele
runden er kjørt på nytt:

    eksporter IFC -> tfm-sjekk -> grafen -> radene forsvinner

Det er derfor dette er en runde og ikke en direkte kobling. Rett gjerne et titalls
objekter før du kjører om igjen.

## Grafen holder en kopi, ikke en peker

Python-noden lagrer skriptet inne i `.dyn`-fila. Den leser ikke fra repoet, og
den vet ikke at fila har endret seg. Oppdaterer du skriptet, må du åpne noden og
lime inn på nytt — ellers kjører grafen videre på den versjonen du limte inn
første gang.

Det er ikke teoretisk, og det har skjedd to ganger. En graf bygget 21. august
manglet feltet `nokkel_fra`, som kom inn dagen etter. Alt annet i sammendraget så
riktig ut, og tallene stemte, så ingenting tydet på at noe var gammelt. Og
`fra-revit`-grafen beskrev seg selv med en nodekobling repoet dokumenterte som
feil — ledningene var riktige, beskrivelsen var én generasjon gammel.

**Slik ser du det: sammendraget oppgir skriptets versjon.**

    Skript 0.8.1.
    2590 elementer merket.
    74 systemforekomster.

Er tallet lavere enn utgivelsen du hentet, kjører grafen på en gammel kopi. Lim
inn på nytt fra `dynamo/tfm_fra_revit.py`.

Står det `ukjent`, har du limt inn direkte fra `.py`-fila. Det er ikke galt —
men da vet ingen hvor gammel kopien er, og linja sier det.

For `tfm_til_revit.py` er versjonen første nøkkel i `OUT[1]`: `skript`.

Linja står i hver kjøring, også når alt er i orden. En melding som bare dukker
opp av og til, blir ikke lest den gangen den betyr noe.

**For grafene i repoet er det ikke lenger noe å se etter.** Ansvaret er delt:
`.py`-fila er fasit for skriptet, `.dyn`-fila for ledningene.

```
   dynamo/tfm_til_revit.py       fasit for skriptet
            │
            │  verktoy/oppdater-grafene.py   (limer inn)
            ▼
   dynamo/tfm-sjekk-tfm-til-revit.dyn
            │
            │  tests/test_dynamo.py          (sier fra)
            ▼
        bygget feiler når de er ulike
```

Endrer du et av skriptene, kjør:

```bash
uv run python verktoy/oppdater-grafene.py
uv run python verktoy/oppdater-grafene.py --demomappe <sti>   # tar demomappa òg
```

Skriveren setter samtidig pakkens versjon inn i `.dyn`-fila. Kilden beholder
`VERSJON = "ukjent"`, så de to kan ikke bli uenige: kopien får versjonen sin i
samme operasjon som skriptet.

**Kjeden er fire ledd, og testen når bare det andre:**

    dynamo/tfm_fra_revit.py          kilden
    dynamo/*.dyn                     kopi 1 — voktet av en test
    demomappa/*.dyn                  kopi 2 — tas av --demomappe
    noden i din Dynamo               kopi 3 — INGEN test når hit

Det er kopi 3 som produserer merkingen. Versjonslinja i sammendraget er det
eneste som avslører at den er gammel.

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
Element.ElementType → GetParameterValueByName("Family Name") ─> IN[0]
Element.GetParameterValueByName("Circuit Number") ───────────> IN[1]
Code Block  "115080";  ─────────────────────────────────────> IN[2]
Element.ElementType → Element.Name ─────────────────────────> IN[3]  (valgfri)

OUT[0] ──> Element.SetParameterByName("TFM")   ← samme elementer inn i «element»
OUT[1] ──> Watch
```

Parameteren må være **Tekst** og **Instance**, og den må hete det
`revit/TFM-egenskapssett.txt` peker på — ellers kommer verdiene aldri ut i
IFC-eksporten.

**Den legger ikke inn feil med vilje.** `verktoy/legg_til_tfm.py` gjør det, fordi
den bygger en fikstur av en fil. Denne skriver inn i en ekte modell, og det
skiller seg. Det trengs heller ikke: en ekte modell har sine egne hull.

### Modellen: hvor den kommer fra

Snowdon Towers er Autodesks eget eksempelprosjekt, levert med Revit siden 2024.
Et blandet bygg på en ekte tomt i Brownsville, Pennsylvania, med sju filer som
er lenket til hverandre.

Filene lastes ned herfra — én lenke per fagmodell, ikke ett arkiv:

<https://help.autodesk.com/view/RVT/2026/ENU/?guid=GUID-61EF2F22-3A1F-4317-B925-1E85F138BE88>

    Snowdon Towers Sample Electrical.rvt        RIE — den vi merker
    Snowdon Towers Sample Architectural.rvt     ARK
    Snowdon Towers Sample Structural.rvt        RIB
    Snowdon Towers Sample Site.rvt              tomt og terreng
    Snowdon Towers Sample HVAC.rvt              RIV, ventilasjon
    Snowdon Towers Sample Plumbing.rvt          RIV, sanitær
    Snowdon Towers Sample Facades.rvt           fasader

**`.rvt`-fila i demomappa er ikke Autodesks lenger.** Den er Electrical-fila
merket med TFM av grafen under, og lagret på nytt fra Revit 2027. Den er
1,8 MB mindre enn nedlastingen, og forskjellen er ikke merkingen alene — en
lagring fra en nyere Revit skriver fila om. Skal du starte fra bunnen, last ned
på nytt framfor å bruke den i demomappa.

**Navnene har mellomrom, ikke understrek.** Revit slår opp lenker på filnavn, og
en fil som heter `Snowdon_Towers_Sample_Architectural.rvt` blir stående med rød
X i `Manage Links` selv om den ligger rett ved siden av. Enten døp om, eller
pek på hver enkelt med `Reload From`.

### Kjørt mot Snowdon Towers

Hele veien er gått i Revit 2027 på Autodesks `Snowdon Towers Sample Electrical
Solar`: grafen merket modellen, modellen ble eksportert til IFC med
kartleggingsfila, og `tfm-sjekk` leste eksporten.

Sju kategorier — Electrical Fixtures, Electrical Equipment, Lighting Devices,
Lighting Fixtures, Data Devices, Conduits, Conduit Fittings — ga:

    2426 elementer merket
    64 systemforekomster
    1029 uten kursnummer — de får undernummer «00»
    1 familie står ikke i tabellen og fikk 4390

Gjennom `tfm-sjekk` ble det **177 funn, alle K8**: objekter som ikke ligger på
noen kurs. Null K1, null K2, null K6 — merkingen er ren, og hvert funn er et
ekte hull i Autodesks modell. Ingen av dem er lagt inn av noen.

Den ene ukjente familien er `Lobby Chandelier`. Den står ikke i `FAMILIER` med
vilje: oppslaget matcher fra begynnelsen av navnet, så ingen generisk nøkkel
treffer den, og å legge den inn ville vært å skrive ett prosjekts
navnekonvensjon inn i en delt tabell. Betyr kodene noe for deg, legg dine egne
familier inn der. Tabellen er den samme som i `verktoy/legg_til_tfm.py`, og
`tests/test_merking.py` passer på at de ikke driver fra hverandre.

**En kontroll som er verdt å gjøre selv.** Den samme logikken kjørt tørt mot
IFC-en — uten å gå veien om Revit — ga 1021 uten kursnummer og 169 funn.
Forskjellen på åtte er den samme begge steder, og kommer av at tørrkjøringen
filtrerte på IFC-klasser der Revit-runden filtrerte på sju kategorier. Åtte flere
objekter uten kurs ga åtte flere funn. Et tall som lar seg forklare er noe annet
enn et tall som ser rimelig ut.

### Bygg grafen, steg for steg

**Trenger du dette?** Ferdige grafer ligger i `dynamo/` — se «To sløyfer, ikke
én» øverst. Stegene her er for deg som vil forstå hva de gjør, som kjører en
eldre Dynamo enn 4.1, eller som skal bygge noe annet av de samme delene.

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

**6. Les familienavnet og kursnummeret.** De to kommer ikke like enkelt.

**Alt forgrenes fra én og samme elementliste.** Har du flere kategorier, er det
`List.Flatten` som er kilden; med én kategori er det `All Elements of Category`.
Lag ikke en ny hentenode per gren. De fire listene som går inn i Python-noden må
være i samme rekkefølge, ellers får element nr. 500 naboens kursnummer — og det
er en feil som ikke synes noe sted. Skriptet stopper på ulik lengde, men kan
ikke se en omstokking.

I resten av dette steget står «elementlista» for den ene kilden.

**Kursnummeret** er én node: `Element.GetParameterValueByName` med
`All Elements of Category` inn i `element`, og en `Code Block` med

    "Circuit Number";

inn i `parameterName`. Anførselstegnene og semikolonet må begge være der.
`Circuit Number;` uten anførselstegn er ikke teksten «Circuit Number» — Dynamo
leser det som et navn på noe, lager en inngangsport av det, og sender null
videre. Kjennetegnet er at Code Block-en får en ny port på venstre side.

**Familienavnet er to noder**, og det er verdt å vite hvilke:

    elementlista
        -> Element.ElementType
        -> Element.GetParameterValueByName("Family Name")   -> IN[0]

`Family Name` er en innebygd parameter på **typen**, og den virker på begge
slags familier Revit har. Det er hele poenget, for de to oppfører seg ulikt:

| | Lastet familie | Systemfamilie |
|---|---|---|
| Eksempel | `Duplex Receptacle` | `Conduit with Fittings` |
| `FamilyType.Family` | virker | **null** |
| `Family Name` | virker | virker |

Prøvd i Revit 2027 på Snowdon Towers: 2426 av 2426 elementer fikk et navn.

**Tre veier som ser riktige ut, og ikke er det:**

`Element.GetParameterValueByName("Family and Type")` returnerer et Revit-objekt,
ikke en streng. En `Watch` viser det som

    Family Type: 18" D x 15" H, Family: Pendant-Dome

Familienavnet står der, men det er Dynamos visningsform — ikke data. Skriptet
deler på første kolon og sitter igjen med «Family Type», som ingen familie
heter. Alle 588 elementene ble ukjente.

`Element.ElementType -> FamilyType.Family -> Element.Name` virker på lastede
familier, men gir null på systemfamilier, med advarselen
`Asked to convert non-convertible types`. Advarselen er riktig — et kabelrør
*er* ikke en familietype. 530 kabelrør falt til standardkoden.

`Element.ElementType -> Element.Name` gir **typenavnet**, som sier noe annet enn
familien: kabelrørene heter `Electrical Metallic Tubing (EMT)` etter materialet,
ikke etter hva de er. Også ukjent for tabellen.

**Reserven, om du vil ha den.** Skriptet tar en valgfri fjerde inngang:

    elementlista -> Element.ElementType -> Element.Name   -> IN[3]

Den brukes bare der `IN[0]` er tom, og sammendraget sier hvor mange det gjaldt.
Med `Family Name` på `IN[0]` fyrte den aldri på Snowdon — men den koster
ingenting, og en modell der noe mangler `Family Name` vil da si fra framfor å
falle stille til standardkoden.

**7. Se på det du fikk, før du går videre.** Heng en `Watch` på hver av de to og
trykk `Run`. Du skal se familienavn i den ene (`Duplex Receptacle: 20A` eller
liknende) og kursnumre i den andre (`1`, `6,8`, eller tomt).

Er familienavnene tomme, eller inneholder de kolon og komma, mangler et ledd i
kjeden fra steg 6 — se etter `Element.Name` til slutt.

Skriptet deler på kolon og bruker bare det som står før, så et navn på formen
`Familie: Type` er like bra som `Familie` alene. Men `Family Type: ..., Family:
...` er noe annet: der står familienavnet bakerst, og det leses ikke.

**8. Python-noden.** Søk `Python Script`. Den kommer med to inputs; klikk `+` på
noden én gang, så du har tre — eller to ganger om du vil ha reserven på `IN[3]`.
Dobbeltklikk, lim inn hele `tfm_fra_revit.py`, trykk `Save`. Koble:

    familienavn        -> IN[0]
    kursnumre          -> IN[1]
    Code Block  "115080";   -> IN[2]
    typenavn           -> IN[3]   (valgfri)

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
| `ADVARSEL: ingen av familienavnene ...` | `IN[0]` gir noe annet enn navn. Linja under advarselen viser den første verdien ordrett — inneholder den kolon og komma, er det et Revit-objekt og ikke et navn. Se steg 6. |
| Skriptet kaster om ulik lengde | `IN[0]` og `IN[1]` kommer fra ulike elementlister. |
| `SetParameterByName` feiler på noen få elementer | Den fikk `x[1]` — sammendraget — i stedet for `x[0]`. Utgangene står i feil rekkefølge. |
| Watch viser lister i lister | Flere kategorier uten `List.Flatten`. |
| `Internal error ... Dereferencing a non-pointer` | En node fikk null. Nesten alltid en `All Elements of Category` uten kategori — forgren fra den du har i stedet for å lage en ny. |
| `Ingen elementer inn` | Kategorivalget traff ingenting. En tom liste ser ut som en ferdig merket modell. |
| `Asked to convert non-convertible types` på `FamilyType.Family` | Systemfamilier — kabelrør, kabelbroer, kanaler — er ikke familietyper. Riktig advarsel, ikke en feil du har gjort. Bruk `Family Name` i stedet, se steg 6. |
| Verdiene kommer ikke ut i IFC-en | Kartleggingsfila mangler i eksportoppsettet, eller peker på et annet parameternavn. |

### Én tabell dekker alle fag

`FAMILIER` bærer både elektro og VVS. Det virker fordi navnene ikke kolliderer:
«Round Duct» og «Downlight» deler ingen begynnelse, og `familiekode` treffer på
begynnelsen av familienavnet. Grafen kan derfor kjøres mot hvilken som helst
fagmodell uten å byttes.

Navnene i VVS-delen er **lest ut av Snowdon Towers' egne HVAC- og
Plumbing-eksporter**, ikke gjettet. Det er ikke pedanteri: en gjettet rad
treffer ingenting, og da faller objektet til `STANDARD = ("4390", "QLX")` — en
ELEKTRO-kode. Et VVS-objekt merket 4390 er verre enn et umerket, fordi det ser
riktig ut.

Målingen fanget en forskjell ingen ville gjettet: arkitektmodellen skriver
`Mop Sink`, rørmodellen `MopSinkConnection`. Samme utstyr, to skrivemåter, og
uten begge hadde ett objekt falt gjennom.

**`STANDARD` er med vilje elektro, også nå.** En VVS-modell der noe får 4390 er
et signal om at tabellen mangler en familie. Alternativet — en reservekode per
fag — ville gjort den manglende raden usynlig: objektet hadde fått en plausibel
VVS-kode, og ingen hadde lett etter familien som manglet.

### For VVS: send systemnavnet inn på `IN[1]`, ikke kursnummeret

`Circuit Number` finnes ikke på ventilasjons- og sanitærobjekter. Send
**`System Name`** i stedet — `kursnummer()` trekker ut sifre av hva som helst
den får, så det krever ingen kodeendring, bare en annen ledning.

    Mechanical Supply Air 22   ->  undernummer «22»
    Domestic Cold Water 30     ->  undernummer «30»

Det gir undernummeret ekte innhold fra modellen framfor «00», og det er
nødvendig av en annen grunn også: **komponentens løpenummer er tre siffer.**

Uten inndeling havner alt i én bøtte. Snowdons rørmodell har 6369 objekter i
omfanget, og med «00» overalt fikk 79 % av dem firesifret løpenummer — altså
ugyldig grammatikk på noe som så ferdig merket ut. Elektromodellen slapp unna
fordi ekte kursnumre ga den 64 bøtter.

**Går en bøtte likevel over 999, ruller det over i systemets løpenummer:**

    ++115080=3100.001.01-JSR999
    ++115080=3100.002.01-JSR001

Det er der formatet er ment å gå. Men **hvilke 999 som havner i «system 1» er
vilkårlig** — det følger rekkefølgen inn, ikke noe i bygget. Les aldri `.002`
som et ekte anlegg nummer to.

Alternativet var å sette `komponent_lopenummer_siffer = 4`. Da hadde prosjektet
hatt en grammatikk ingen andre bruker, og grensen ville vært skjult framfor
håndtert.

K8 rører uansett ikke 3xx — `er_elektro` er «4» eller «5» — så et VVS-objekt
uten kursnummer gir ingen funn.

**Sammendraget sier fortsatt «uten kursnummer».** Med systemnavn på `IN[1]` blir
det tallet ~0 for VVS, og ordet er da upresist: objektene har systemnummer, ikke
kursnummer. Skriptet vet hvilket fag hvert objekt er, men ikke hvilket fag
*kjøringen* gjelder, så linja er skrevet for det vanlige tilfellet.

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

**Bruk 2x3-fila, ikke `demo-elektro.ifc`.** De har samme innhold, men Revits
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

### Lenkeeksport tar IKKE med lenkenes egne parametre

Prøvd 25. august 2026, og det kostet tre eksportrunder å finne.

`File > Export > IFC` med «Export linked files as separate IFCs» gir én IFC per
lenke, og geometrien kommer riktig ut. **Men TFM-parameteren i de lenkede
modellene blir ikke med.**

    Electrical.ifc    TFM11_Forekomst: 2426    <- vertsmodellen
    HVAC.ifc          INGEN TFM                <- lenke
    Plumbing.ifc      INGEN TFM                <- lenke

`TFM` er en **prosjektparameter**, og prosjektparametre hører til ett dokument.
Eksporten kjører i vertsmodellens kontekst, og der finnes ikke de lenkede
modellenes egne parametre.

Feilen er stille. Eksporten lykkes, filstørrelsene ser rimelige ut, og
`tfm-sjekk` melder K1 på hvert objekt — altså nøyaktig som om modellene var
umerket. Vi trodde først at merkingen ikke var lagret.

**Slik ser du det:** eksporter én lenket modell ALENE og sammenlign. Fikk den
TFM da, er det lenkeeksporten. Filstørrelsen sier det også — HVAC gikk fra
9,2 til 10,7 MB med merkingen med.

**Løsningen er å eksportere hver modell for seg.** Åpne `.rvt`-fila som
vertsmodell og eksporter den alene, med kartleggingsfila i oppsettet. Da leses
parameteren fra det dokumentet den bor i.

Modellene som ikke bærer TFM — arkitekt, konstruksjon, tomt — kan gjerne komme
fra lenkeeksporten. De har ingenting å miste.

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
