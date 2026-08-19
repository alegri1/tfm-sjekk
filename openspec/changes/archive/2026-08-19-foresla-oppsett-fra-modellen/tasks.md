## 1. Datamodell for forslaget

- [x] 1.1 Ny modul `src/tfm_sjekk/oppsett/__init__.py` med pydantic-modellene:
      `Foreslatt` (verdi, antall objekter, `Kilde`) og `Oppsettforslag`
      (foreslåtte egenskapssett og feltnavn per verditype, foreslåtte klasser,
      antall leste objekter, antall objekter med TFM-verdi)
- [x] 1.2 `Oppsettforslag.har_noe()` og skillet mellom «ingenting å foreslå» og
      «ingenting å bygge på», slik at kommandoen kan si hvilket tilfelle den står i

## 2. Utledning fra Kontekst

- [x] 2.1 `utled(kontekst) -> Oppsettforslag` i `src/tfm_sjekk/oppsett/utled.py`:
      aggreger `Verdikilde` over alle objekter, nøklet på verditype, egenskapssett
      og felt, med antall
- [x] 2.2 Klassifiser etter `Kilde`: `GJENKJENT_FELT` gir foreslått egenskapssett,
      `GJETTET` gir foreslått feltnavn, `KONFIGURERT` og `FORKASTET` gir ingenting
- [x] 2.3 Mål delta mot `kontekst.config`, ikke mot `Konfigurasjon()`, slik at
      `--config` virker og et forslag brukt om igjen blir tomt
- [x] 2.4 Sorter foreslåtte verdier synkende på antall objekter, med de
      konfigurerte foran og uendret innbyrdes rekkefølge
- [x] 2.5 Foreslå `ifc_klasser`: objekter med `tfm_forekomst` satt som ingen
      konfigurert klasse treffer via `er_av_type`, foreslått med sin konkrete
      `ifc_klasse` og med antall
- [x] 2.6 Tester for 2.1–2.5 mot `Kontekst` bygget i minnet, uten IFC-filer,
      i `tests/test_oppsett.py` — ett scenario per krav i spesifikasjonen,
      inkludert at en forkastet verdi ikke gir forslag og at umerkede klasser
      holdes utenfor

## 3. TOML-skriver

- [x] 3.1 `til_toml(forslag) -> str` i `src/tfm_sjekk/oppsett/toml_ut.py`:
      tabeller med lister av strenger, med sitering og escaping av `\` og `"`
- [x] 3.2 Skriv beviset som kommentar over hver oppføring: antall objekter og
      hvordan verdien ble funnet
- [x] 3.3 Topptekst med antall fagmodeller og objekter forslaget bygger på, og at
      det skal leses gjennom før bruk
- [x] 3.4 Tester: at utdata er gyldig TOML som `Konfigurasjon.les` godtar, at
      kommentarene inneholder antallet, og at et tomt forslag ikke gir tomme
      tabeller

## 4. Kommandoen

- [x] 4.1 `tfm-sjekk oppsett <filer>` i `cli.py`: bygg `Kontekst` med
      `--config`, uten master og kodetabeller, og skriv forslaget til standard ut
- [x] 4.2 `--ut <fil>` skriver til fil; en fil som finnes overskrives ikke uten
      `--overskriv`, og meldingen sier hva som må til
- [x] 4.3 Meld tomt forslag i to varianter: oppsettet dekker modellene, eller
      ingen TFM-verdier funnet — den siste med antall leste objekter
- [x] 4.4 Legg `oppsett` til blant kommandoordene `_med_standardkommando()`
      kjenner, med test på at en fil ved navn `oppsett.ifc` fortsatt går til `sjekk`
- [x] 4.5 Tester i `tests/test_cli.py`, kjørt i egen prosess: standard ut, `--ut`,
      nektet overskriving, og `oppsett` listet i hjelpeteksten

## 5. Rundtur — den egentlige prøven

- [x] 5.1 Test som kjører `utled` på en modell der verdiene ligger utenfor
      oppsettet, mater forslaget tilbake som konfigurasjon, og slår fast at
      kildene nå er `KONFIGURERT`
- [x] 5.2 Test på at andre kjøring med eget forslag som konfigurasjon gir et
      forslag uten innhold
- [x] 5.3 Fikstur i `tests/fixtures/syntetisk.py` for en modell som legger
      TFM-verdier i et ukonfigurert egenskapssett, i et ukonfigurert felt, og på
      en klasse utenfor omfanget — de tre tilfellene forslaget finnes for

## 6. Demo, dokumentasjon og prøving hos konsumenten

- [x] 6.1 Utvid `eksempler/lag_demomodell.py` med en fagmodell som har verdiene på
      avveie, slik at `oppsett` har noe å foreslå i demoen
- [x] 6.2 Kjør `tfm-sjekk oppsett` på demomodellene, les fila, og bruk den som
      `--config` i en påfølgende `sjekk` — fila verktøyet skriver skal være en fil
      verktøyet leser
- [x] 6.3 Kjør kommandoen i en cp1252-konsoll: forslaget inneholder ««»» og norske
      tegn i kommentarene
- [x] 6.4 README: nytt avsnitt om førstegangsbruk under «Bruk», og `oppsett` i
      kontrolloversiktens nabolag der kommandoene beskrives
- [x] 6.5 Røyktesten i `.github/workflows/bygg.yml` kjører `oppsett` fra binæren og
      slår fast at utdata er lesbar TOML
