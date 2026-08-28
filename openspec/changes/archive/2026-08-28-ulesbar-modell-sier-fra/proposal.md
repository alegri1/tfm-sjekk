## Why

En fil som ikke lar seg lese som IFC gir en rå Python-traceback og en exit-kode
som betyr noe annet:

```
tom.ifc      OSError: Unable to open file for reading      exit 1
sopp.ifc     Error: Unable to parse IFC SPF header         exit 120
```

**Exit 1 betyr «modellen har feil» (§5).** Det er porten i leveranseprosessen.
En CI-jobb kan ikke skille «fagmodellen har 40 K1-feil» fra «fila lot seg ikke
åpne» — begge stopper leveransen, men bare den ene er noe entreprenøren kan
rette. Exit 120 betyr ingenting; den kommer av at prosessen dør på vei ut.

Asymmetrien er det som gjør dette til en feil framfor en ruhet:

```
sti som ikke finnes   →  «Path ... does not exist.»       exit 2  ✔
oppsett som ikke leses →  melding med --config som hint   exit 2  ✔
fil som ikke er IFC    →  traceback fra ifcopenshell      exit 1 / 120
```

Skrivefeil i stien er håndtert, og et uleselig oppsett er håndtert. En avbrutt
Revit-eksport, en halv opplasting fra et filområde, en `.ifcZIP` som har fått
feil endelse — de sannsynlige hendelsene i et ekte prosjekt — er ikke.

En tredje variant er stillere. En **avkuttet** IFC leses uten innvending:

```
1 objekter
avkuttet.ifc: 1 av 1 objekter i omfanget
alle TFM-verdiene lot seg tolke
```

Hver linje er sann, og til sammen er de misvisende: dette er de første 400
bytene av en modell på 26 kB. Fila mangler `END-ISO-10303-21;` til slutt, så
den er billig å kjenne igjen — og en halv fil er ikke noe å konkludere fra.

Dette er det samme prinsippet som har drevet de seks siste endringene: **et
verktøy som ikke kan svare, skal si at det ikke kan svare** — og det skal ikke
si det med koden som betyr at modellen er underkjent.

## What Changes

- En modellfil som ikke lar seg åpne eller tolke stopper kjøringen med en
  melding som navngir **fila** og **hva som gikk galt**, og med **exit 2** — som
  en sti som peker feil. Ingen traceback, ingen rapport.
- Det samme gjelder i en federert kjøring: er én av seks filer uleselig, sier
  meldingen hvilken. Kjøringen stopper framfor å svare på fem sjettedeler av
  spørsmålet, fordi K6 og D3 ser på tvers av filer og et svar uten den sjette
  ville vært feil uten å se feil ut.
- En IFC som mangler avslutningen `END-ISO-10303-21;` regnes som **ufullstendig**
  og behandles likt: kjøringen stopper med en melding om at fila ser avkuttet ut.
- Ingen rapportfiler skrives i noen av tilfellene. En rapport fra en kjøring som
  ikke kom i mål er verre enn ingen rapport.

Ingen kontroll endrer oppførsel. Exit 0 og exit 1 betyr det samme som før.

## Capabilities

### New Capabilities

- `modellesing`: hva verktøyet garanterer om å lese en modellfil — at en fil det
  ikke kan lese blir sagt fra om framfor å krasje, at det skjer med koden som
  betyr «kunne ikke kjøre» framfor den som betyr «underkjent», og at en
  ufullstendig fil ikke blir lest som en hel.

### Modified Capabilities

Ingen. `oppsettfunn` dekker oppsettfila, `fastrute` dekker ruten fram til
filene; ingen av dem sier noe om hva som skjer når fila finnes og likevel ikke
kan leses.

## Impact

- `src/tfm_sjekk/ifc/loader.py` — `les_modell`
- `src/tfm_sjekk/ifc/federering.py` — feilen må krysse prosessgrensen med
  filnavnet i behold
- `src/tfm_sjekk/cli.py` — samme utgang som `OppsettFeil`
- `tests/test_ifc.py`, `tests/test_cli.py`
- README: §5-avsnittet om exit-koder nevner i dag bare 0 og 1

Ingen nye avhengigheter. Ingen dataformater endres.
