## Why

Demomodellene får ny identitet hver gang de lages. En BCF som ble skrevet før
forrige kjøring peker da på objekter som ikke finnes, og vieweren svarer:

    None of the viewpoint components are found in your project.
    Do you want to proceed?

Målt: null av 13 GUID-er matchet etter én regenerering.

Halve saken er allerede løst i verktøyet. `rapport/bcf.py` sier det selv:

> *GUID-ene* er ikke tilfeldige, men utledet fra innholdet i funnet med `uuid5`.
> Samme funn gir samme emne-GUID i går og i morgen.

Den andre halvparten er ikke det. `tests/fixtures/syntetisk.py` kaller
`guid.new()` 25 steder, og hver kjøring trekker nye `GlobalId`-er.

Det gjør demomappa skjør på en måte ingen ser. Du sender den fra deg,
mottakeren kjører `lag_demomodell.py` i god tro for å få `.ifc`-filene — de
ligger ikke i repoet (§8 og `.gitignore`) — og BCF-en slutter å peke på noe.
Ingen feilmelding, bare et emne som ikke finner objektet sitt.

Det er samme mønster som ferdigheten i repoet lister fire ganger: et
referansedatasett som driver fra det det beskriver. Her driver det fra seg selv.

## What Changes

- `GlobalId` i fikstur-modellene utledes av innholdet med `uuid5`, ikke trekkes
  med `guid.new()`. Samme generator og samme data gir samme identitet i dag og
  om et år.
- Det gjelder alle entiteter i fila, ikke bare produktene: prosjekt, romlig
  struktur, egenskapssett og relasjoner. En halvt deterministisk fil er en
  felle, fordi den ser stabil ut.
- **Uendret:** hvilke objekter modellene har, hvilke verdier de bærer, og hvor
  mange funn de gir. Bare identiteten blir forutsigbar.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

Ingen. Endringen ligger i testfiksturen, ikke i verktøyet: ingen kontroll,
ingen rapport og ingen kommando oppfører seg annerledes. `openspec/specs/`
beskriver hva verktøyet gjør, og det er uendret. Derfor `skip_specs: true`.

## Impact

- **`tests/fixtures/syntetisk.py`:** 25 kall til `guid.new()` byttes ut med en
  deterministisk generator, og `ifcopenshell.template.create` får en fast
  `project_globalid`.
- **Uendret:** `src/`, alle kontroller, alle rapportformater, CLI-en.
- **Prøving:** to kjøringer av `lag_demomodell.py` skal gi byte-identiske
  filer. Det er den eneste prøven som fanger dette — funntallet er det samme
  begge veier, og alt annet ser likt ut. En BCF laget før en regenerering skal
  fortsatt peke på de samme objektene etterpå.
