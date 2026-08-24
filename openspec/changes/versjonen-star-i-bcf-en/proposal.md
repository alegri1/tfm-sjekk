## Why

En BCF kan være eldre enn koden som lagde den, og ingenting sier fra.

Det skjedde i dag. Demomappa hadde tre BCF-filer, og én av dem —
`snowdon-rapport/funn.bcfzip` — var laget før kamerafeilen ble rettet. GUID-ene
stemte, så vieweren klaget ikke. Den flyttet bare kameraet 969 kilometer, og
modellen forsvant.

Fila så fullt gyldig ut ved siden av de to ferske. Det fantes ingen måte å se
forskjell på annet enn å regne ut kameraavstanden.

`fast-identitet-i-demomodellene` løste at *modellene* endrer identitet mellom
kjøringer. Dette er en annen drift: rapporten er fersk nok til å matche
modellen, men laget av en utgave som gjorde noe galt. Den har ingen mekanisme i
dag.

## What Changes

- `CreationAuthor` i hvert BCF-emne blir `tfm-sjekk <versjon>` i stedet for
  `tfm-sjekk`. Feltet er per emne og vises i emnelista i enhver viewer.
- Det samme gjelder `Author` på kommentaren, som allerede bruker samme verdi.
- **Uendret:** `bcf.version` står på `2.1`. `DetailedVersion` der er BCF-formatets
  versjon, ikke verktøyets, og å skrive noe annet ville vært feil bruk av feltet.
- **Uendret:** funnene, de tre andre rapportformatene, alt annet.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `funnformat`: Nytt krav om at et BCF-emne skal bære versjonen av verktøyet som
  lagde det. Feltet er per emne, som resten av det evnen beskriver. De fem
  eksisterende kravene står uendret.

## Impact

- **`rapport/bcf.py`:** `FORFATTER` utledes av pakkeversjonen framfor å være en
  fast streng.
- **Uendret:** CLI-en, kontrollene, HTML, CSV og XLSX.
- **Prøving:** emnet skal bære versjonen, og BCF-en skal fortsatt være
  reproduserbar for samme funn og samme `--opprettet` innenfor én versjon. At
  fila endrer seg mellom versjoner er hensikten.
