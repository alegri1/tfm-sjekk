## Context

Se proposal.md — Why.

`_psets(produkt)` går over `produkt.IsDefinedBy` og plukker
`IfcRelDefinesByProperties` med et `IfcPropertySet`. Den returnerer en ordbok
fra settnavn til felt/verdi, og `_finn` velger blant dem etter forrangen i
`verdiuttrekk`.

Typekoblingen ligger et annet sted, og heter ikke det samme i de to skjemaene:

    IFC4     produkt.IsTypedBy      -> IfcRelDefinesByType -> RelatingType
    IFC 2x3  produkt.IsDefinedBy    -> IfcRelDefinesByType -> RelatingType

Typeobjektet bærer settene sine på `HasPropertySets`, ikke gjennom en relasjon.

## Goals / Non-Goals

**Goals:**

- En modell merket på typen skal leses.
- En modell som ikke bruker typemerking skal gi nøyaktig samme resultat som før.

**Non-Goals:**

- Å innføre en ny konfigurasjonsnøkkel. De samme `pset`-navnene og feltnavnene
  gjelder begge steder — et prosjekt som kaller settet `TFM11_Type` kaller det
  det samme uansett hvor det henger.
- Å avgjøre om en TFM-forekomst på en delt type er en modelleringsfeil. Verdien
  er duplisert, K6 melder duplikater, og det er riktig svar. Å tie om det ville
  vært å bestemme hva som var ment.
- Å lese fra `IfcRelDefinesByTemplate` eller andre definisjonsrelasjoner.
  `IfcRelDefinesByType` er den som bærer Revits familietyper.

## Decisions

### Rekkefølge framfor sammenligning

`_psets` bygger allerede en ordbok. Legges typens sett inn først og forekomstens
etterpå, overstyrer forekomsten av seg selv — samme mekanisme som `dict.update`.

Alternativet var å hente begge og sammenligne per felt. Det ville krevd at
`_finn` visste om to kilder, og forrangen i `verdiuttrekk` — konfigurert,
gjenkjent, gjettet — måtte da vevd sammen med forekomst-mot-type. To
uavhengige rangeringer i samme funksjon er en av de tingene som ser enkel ut i
en commit og er umulig å endre et halvår senere.

Prisen er at et sett med samme navn på begge steder smelter sammen felt for
felt, ikke som en enhet. I praksis er det ønsket: har typen `TFM11_Type.TFMType`
og forekomsten `TFM11_Type.MMI`, skal begge leses.

### Én funksjon, ikke to

`_psets` får ansvaret framfor at `les_modell` slår sammen to kall. Da kan ingen
konsument av `_psets` få halve bildet, og rekkefølgen ligger ett sted.

### Ingen ny `Kilde`

`Verdikilde` bærer `kilde`, `pset` og `felt`. Å legge til at settet hang på
typen ville vært opplysende, men `Kilde` er i dag en rangering av *hvor sikkert*
verktøyet vet — konfigurert, gjenkjent, gjettet, forkastet. Hvor settet hang er
et annet spørsmål enn hvor sikker verdien er, og å blande dem ville gjort
rangeringen tvetydig.

Kommer behovet, er det et eget felt på `Verdikilde` og en egen sak.

## Risks / Trade-offs

**En delt type med TFM-forekomst gir mange K6-funn** → 512 objekter deler den
største typen i Snowdon. Er en forekomstverdi merket der, melder K6 alle 512.
Det er teknisk riktig — verdien er duplisert — men det peker på objektene
framfor på typen. Vurdert og valgt: verktøyet skal lese det som står. En egen
melding for tilfellet er en egen sak, og den kan skrives når noen har sett det
skje.

**Modeller som tidligere så tomme ut, får plutselig funn** → Det er hensikten,
og det kan overraske: en modell som ga «K1 på alt» kan nå gi hundrevis av ekte
funn. Rapporten blir lengre og riktigere på én gang.

**Typeobjekter finnes i tusentall** → Snowdon har 127 typer for 2439 objekter,
altså langt færre typer enn objekter. Oppslaget går fra objektet til typen, ikke
motsatt, så kostnaden er én relasjon per objekt. Uttrekket leser allerede
`IsDefinedBy` for hvert objekt.
