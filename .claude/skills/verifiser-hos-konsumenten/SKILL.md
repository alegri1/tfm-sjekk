---
name: verifiser-hos-konsumenten
description: Bruk denne før du sier at noe er ferdig i tfm-sjekk, og alltid når du har endret utdata som noen andre leser - konsollutskrift, HTML-rapporten, CSV/XLSX, BCF-fila, binæren, README eller demomodellene. Grønne typer og grønne tester er ikke bevis på at det virker der det brukes.
---

# Verifiser hos konsumenten

## Hvorfor denne finnes

Sju feil i dette prosjektet har sluppet gjennom med alt grønt. Ikke én av dem
kunne typer, tester eller skjemavalidering fange, fordi ingen av delene ser det
konsumenten ser:

| Feilen | Alt var grønt fordi | Hvem fant den |
|---|---|---|
| `.gitignore` skjulte hele `src/tfm_sjekk/rapport/` | mønsteret var uankret, og pakken lå på disk | en klone |
| `docs/rapport.PNG` mot `docs/rapport.png` | Windows slår bokstavstørrelse sammen | GitHub |
| `→` i oppsummeringa krasjet ren modell | terminalen her er UTF-8 | en cp1252-konsoll |
| Mørk modus hadde 1,11:1 kontrast | CSS-en var syntaktisk feilfri | et øye |
| BCF-emner manglet kamera, så snapshot | begge er valgfrie i XSD-en | BIMcollab ZOOM |
| `demo-*.ifc` sveipet med en kopi av elektromodellen | K6 gjorde nøyaktig som den skulle | å lese rapporten |
| Ubeskyttet `$(...)` i et CI-steg | terminalen her kjører ikke med `set -e` | bygg på alle tre plattformer |

Mønsteret er ett: **det ble erklært ferdig uten at noen så på det der det
brukes.** Verktøykjeden her hjemme sier god dag.

## Sjekklista

Endret du noe i venstre kolonne, gjør du høyre kolonne før du sier ferdig.

**Konsollutskrift** (`cli.py`, meldingstekster, `rich`-oppsett)
- Skrev du et tegn utenfor ASCII - `→`, `«»`, `æøå`, tankestrek? Kjør i cp1252.
  `tests/test_cli.py::test_exit_koden_overlever_en_cp1252_konsoll` er malen:
  egen prosess med `koding="cp1252"`, ikke et kall i denne terminalen.
- Leser CI eller en test utskriften? Farger fra `rich` ligger i strengen.
  Bruk `uten_ansi()`.

**HTML-rapporten** (`rapport/html.py`)
- Åpne den, og skru på mørk modus. Nye farger må inn som CSS-variabler i begge
  paletter - en farge som bare finnes i den lyse blir usynlig i den mørke.
- Legg testen i `tests/test_html.py`.

**CSV og XLSX** (`rapport/csv_rapport.py`, `rapport/xlsx.py`)
- Åpne fila i Excel, helst nettversjonen. Den er strengere enn skrivebordet.
- Se etter: kolonner som ikke deler seg, og `Ã¸` der det skal stå `ø`. BOM og
  skilletegn drar mot hverandre - `sep=;` på linje 1 ødelegger BOM-en.

**BCF** (`rapport/bcf.py`)
- Skjemavalidering er ikke nok. Kamera og snapshot er **valgfrie** i XSD-en, så
  en fil kan validere og likevel gi «This issue has no viewpoint to zoom to».
- Importer `funn.bcfzip` i BIMcollab ZOOM mot `eksempler/demo-*.ifc`, og
  dobbeltklikk et emne. Modellnivå-emner uten objekt skal være merket.
- Legg testen i `tests/test_bcf.py`.

**Binæren** (`tfm-sjekk.spec`, alt som pakkes)
- Kjør den **utenfor prosjektmappa**. Kjører du den her, kan den plukke opp
  kildekoden ved siden av seg og se ut til å virke med en tom bundel.
- Gi den tre filer, så prosesspoolen faktisk starter. Uten `freeze_support()`
  ender det i `BrokenProcessPool`, og bare i den frosne binæren.
- Røyktesten i `.github/workflows/bygg.yml` gjør begge deler.

**Steg i en GitHub-workflow**
- `shell: bash` kjører som `bash --noprofile --norc -eo pipefail`. Under `set -e`
  river en tilordning fra en kommando som feiler hele steget, uten en eneste
  melding om hvorfor — og `tfm-sjekk sjekk` gir exit 1 hver gang den finner en
  feil. Skriv `$(... || true)` når det er utdata og ikke exit-koden du er ute
  etter.
- Prøv **steget**, ikke kommandoene hver for seg. En kommando som virker fint i
  terminalen din kan velte steget:

      verktoy/kjor-ci-steg.sh .github/workflows/bygg.yml binaer Røyktest

  Skriptet henter `run:`-blokka ut av YAML-en og kjører den med GitHubs egne
  flagg. Det gjenskapte feilen over på første forsøk, mens de samme kommandoene
  kjørte feilfritt i en vanlig terminal.

**README og alt som havner på GitHub**
- Lokale lenker og bilder: sjekk bokstavstørrelsen mot filnavnet på disk.
  Windows ser ikke forskjellen, GitHub gjør det.
- Nye ignoreringsmønstre: ankre kataloger med `/` foran, og klon repoet et
  annet sted for å se hva som faktisk ble med.

**Demomodeller og fikstur-data**
- Kjør demoen og **les rapporten**. Ikke bare tell at den ikke krasjet.
- Stemmer tallet med det dokumentasjonen lover? Fire ganger har et
  referansedatasett drevet fra det det beskriver: mastera, kodetabellen,
  røyktesten i CI, og `demo-*.ifc`-globben. Det skjer stille, og bare den som
  ser på utdataene oppdager det.

## Regelen

Si **ferdig** bare om det du har sett virke. Ellers si hva du prøvde og hva som
gjenstår - «testene er grønne, men jeg har ikke åpnet BCF-en i en viewer» er et
brukbart svar. «Ferdig» om noe du ikke har sett, er det ikke.

Er konsumenten noe bare brukeren har - BIMcollab ZOOM, Excel, en ekte
fagmodell - så si det, og be dem se. De sju feilene over ble alle funnet slik.
