## Context

Se proposal.md — Why. Det som former løsningen er hva mappa faktisk består av:

```
  22 filer
   │
   ├── 15  byte-identiske kopier av repofiler        -> kopieres
   │       FIKTIV-*.csv, demo-*.ifc, avveie, blindsone,
   │       tidligfase(.ifc/.toml), foringsvei(.ifc/.toml), *.dyn
   │
   ├──  4  binærfiler, 110 MB, kan ikke bygges       -> røres ikke
   │       Snowdon.rvt, snowdon-tfm.ifc,
   │       snowdon-eksport.ifc, eksport.ifc
   │
   └──  3  tfm-sjekk.exe  -> hentes fra utgivelsen
           kjor.cmd       -> skrives
           LES-MEG.txt    -> skrives, med målte tall
```

`eksempler/lag_demomodell.py` genererer allerede modellene og kalles som den er.

## Goals / Non-Goals

**Goals:**
- Demomappa slutter å være noe man eier og blir noe man kjører.
- Et tall i dokumentasjonen kan ikke være noe annet enn det kommandoen ga.
- Byggingen sier fra om alt den ikke fikk til.

**Non-Goals:**
- Ikke i CI. Byggingen trenger en utgivelse som finnes og en mappe som ikke er i
  git, og resultatet må uansett åpnes av et menneske før det kan kalles ferdig.
- Ingen synkronisering den andre veien. Retter du noe i mappa, er det tapt ved
  neste bygging — og det er meningen: kilden er repoet.
- Snowdon-kjeden gjenskapes ikke. Den krever Revit, Dynamo og en person.

## Decisions

### Malen ligger i repoet, ikke i skriptet

`verktoy/demomappe-LES-MEG.mal.txt`, ikke en streng inne i Python-fila.

Teksten er 400 linjer prosa som redigeres langt oftere enn koden rundt. I en
diff skal en endret setning se ut som en endret setning, ikke som en endret
strengliteral med rømte linjeskift. Det er også den fila som skal kunne leses av
noen som ikke leser Python.

*Alternativ vurdert:* Jinja2, som prosjektet allerede har til HTML-rapporten. For
mye: malen trenger bare navngitt utfylling, ingen løkker og ingen betingelser.
`str.format` med navngitte felt gjør det, og en ukjent plassholder blir en
`KeyError` — som er akkurat den feilen vi vil ha.

### Plassholderne er navngitte, og en som ikke ble fylt ut stopper byggingen

`{demo_funn}`, ikke `{0}`. Og etter utfylling: let etter `{` som står igjen.

`str.format` kaster på en plassholder uten verdi, men ikke på en verdi uten
plassholder — legger noen til et tall i malen uten å måle det, ville teksten blitt
skrevet med `{nytt_tall}` stående midt i. Det ser ut som en skrivefeil og ikke som
en manglende måling, og mottakeren har ingen måte å vite hvilken.

### Tallene måles ved å kjøre kommandoene dokumentet viser

Ikke ved å importere `tfm_sjekk` og telle funn. Byggingen starter **binæren i
mappa**, med de argumentene som står i teksten, og leser `funn.csv`.

Det er forskjellen mellom å prøve koden og å prøve leveransen. En binær kan være
en annen generasjon enn kilden, og det er nettopp den forskjellen mappa finnes for
å vise. Samme grunn til at røyktesten i CI kjører exe-en utenfor prosjektmappa.

Følgen er at byggingen tar noen minutter — Snowdon alene er 2439 objekter. Det er
riktig pris: den kjøres når en utgivelse er ny, ikke i en løkke.

### Binæren hentes fra en utgivelse, ikke bygges lokalt

`gh release download`, med versjonen som argument.

Mappa skal inneholde nøyaktig den binæren en bruker ville lastet ned. En lokal
PyInstaller-bygging gir en fil som ligner og som ingen andre har sett; røyktesten
i CI har ikke kjørt på den.

### Revit-filene er en forutsetning, ikke en utdata

Byggingen stopper om en av de fire mangler, framfor å bygge rundt dem.

De er det eneste i mappa som ikke kan lages på nytt. En bygging som ryddet først
og kopierte etterpå ville slettet dem — og en mappe uten Snowdon-kjeden er ikke
demomappa, den er demomodellene.

Derfor: ingen `rmtree`. Byggingen skriver over det den eier og lar resten være.
Filer den ikke kjenner blir liggende, og den sier fra om dem — en fil ingen har
plassert der med vilje er verdt et blikk, men ikke verdt å slette uten å spørre.

### Tabellene blir liggende i `kjor.cmd`, ikke i `tfm-sjekk.toml`

Byggingen viderefører valget fra v0.7.0. Mappa er ikke ett prosjekt; den er
flere uavhengige demoer, og `snowdon-tfm.ifc` skal med vilje kjøre uten tabeller —
med dem gir den over 5000 funn i stedet for 179.

Skrives dette ned bare i mappa, forsvinner det ved neste rydding. Derfor står det
her og i malen.

## Risks / Trade-offs

**En bygget mappe er ikke en prøvd mappe** → Byggingen kan ikke åpne Notisblokk,
dobbeltklikke `kjor.cmd` eller importere BCF-en i en viewer. Den siste oppgaven
er og blir et menneske. Står i proposal.md under «Prøves hos konsumenten».

**Malen kan drive fra det den beskriver, akkurat som teksten gjorde** → Bare
delvis: tallene kan den ikke lyve om lenger. Prosaen rundt kan den fortsatt.
Motmiddelet er at malen ligger i repoet og synes i en diff.

**`gh` må finnes på maskinen** → Den gjør det, og den brukes allerede. Mangler
den, stopper byggingen med det som mangler framfor å bygge en mappe uten binær.

**Byggingen tar minutter** → Den kjøres per utgivelse. Alternativet — å måle mot
kildekoden i stedet for binæren — er raskere og prøver feil ting.
