## 1. Oppsettet peker på modellene

- [x] 1.1 `Konfigurasjon` får `modeller: list[str] = []` og `ut: Path | None`, begge
      med `description` som sier hva de er til for
- [x] 1.2 `Konfigurasjon.stier(felt)` — samme regel som `sti()`, men for en liste, og
      med mønstertreff. Sorterer resultatet; se design.md om byte-identisk BCF
- [x] 1.3 De to nye navnene inn i `_gyldige_nokler`, så en skrivefeil får forslag og
      en nøkkel i feil seksjon får vite hvor den hører hjemme
- [x] 1.4 Test: relativ sti løses mot oppsettfila, ikke mot arbeidskatalogen
- [x] 1.5 Test: mønster gir sortert rekkefølge uavhengig av filsystemets

## 2. `sjekk` uten filargumenter

- [x] 2.1 `modeller` blir valgfritt argument. Oppsettet leses først når lista er tom
      — `finn_oppsett([])` faller tilbake til arbeidskatalogen
- [x] 2.2 Modeller fra oppsettet der ingen finnes: stopp med en feil som oppgir både
      mønsteret slik det sto og stien det ble løst til. Ingen rapport skrives
- [x] 2.3 Ingen modeller noe sted: stopp med en melding om at ingen modell er oppgitt
- [x] 2.4 `--ut` hentes fra oppsettet når flagget ikke er gitt
- [x] 2.5 Test: kjøring uten argumenter i en mappe med oppsett gir rapport
- [x] 2.6 Test: filargumenter vinner over oppsettets `modeller`
- [x] 2.7 Test: `--ut` vinner over oppsettets `ut`
- [x] 2.8 Test: mønster uten treff gir exit 2 og ingen rapportmappe
- [x] 2.9 Test: dra-og-slipp beholder rapporten hos modellen selv når oppsettet har
      `ut` — `_med_rapportmappe` setter flagget, og flagget vinner

## 3. Grafene inn i repoet

- [x] 3.1 Kopier de to `.dyn`-filene fra demomappa til `dynamo/`
- [x] 3.2 Bytt den hardkodede CSV-stien mot `C:\prosjekt\rapport\funn.csv`, og
      `"115080";` mot en plassholder som ikke er en ekte Snowdon-kode
- [x] 3.3 `verktoy/oppdater-grafene.py` — limer `dynamo/*.py` inn i riktig
      `PythonScriptNode` i hver `.dyn`, og sier hvilke som ble endret
- [x] 3.4 Kjør den. `fra-revit`-grafens kopi er én generasjon gammel og skal bli fersk
- [x] 3.5 Test i `tests/test_dynamo.py`: skriptkopien i hver `.dyn` er lik kildefila,
      med en feilmelding som nevner `verktoy/oppdater-grafene.py`
- [x] 3.6 Test: ingen absolutt brukersti i `.dyn`-filene

## 4. Dokumentasjonen skiller de to sløyfene

- [x] 4.1 `dynamo/LES-MEG.md`: åpne med de to sløyfene — engangs per prosjekt, og
      runden som gjentas — og si at grafene finnes ferdig
- [x] 4.2 «Bygg grafen, steg for steg» blir stående, men merkes som veien for den som
      vil bygge selv eller kjører eldre Dynamo
- [x] 4.3 Avsnittet om at Python-noden holder en kopi peker på
      `verktoy/oppdater-grafene.py` og på testen som vokter det
- [x] 4.4 `README.md`: den korte ruten — `tfm-sjekk.toml` med `modeller` og `ut`, og
      `tfm-sjekk sjekk` uten argumenter
- [x] 4.5 Fjern setningen i README om oppsett «ved siden av modellene» hvis den nå
      er upresis — ruten kan peke andre steder

## 5. Prøvd der det brukes

- [x] 5.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 5.3 Ruten prøvd frosset: PyInstaller-binær bygget lokalt, kjørt via `kjor.cmd`
      i en kopi av demomappa. 17 funn, rad for rad like en kjøring med
      filargumenter. Dra-og-slipp og mønster-uten-treff (exit 2) prøvd samme sted
- [x] 5.7 BOM i oppsettet krasjet med en tilbakesporing — funnet under 5.3, gjelder
      v0.6.2 like mye. Rettet, og ugyldig TOML gir nå en melding med filnavn

**5.2, 5.4, 5.5 og 5.6 venter på taggen.** `tfm-sjekk.exe` i demomappa er v0.6.2,
og den avviser `modeller` og `ut` med exit 2 — et oppsett med ruten ville brukket
*alle* demokommandoene, ikke bare den nye. Mappa holdes selvkonsistent på 0.6.2 og
oppdateres i én omgang når binæren byttes; `LES-MEG.txt` skal ha ny versjon i
toppen da uansett.

- [ ] 5.2 Demomappa: `tfm-sjekk.toml` får `modeller` og `ut`, og en `kjor.cmd` som
      bare kaller `tfm-sjekk.exe sjekk` og ender med `pause`
- [ ] 5.4 Kopier de to `.dyn`-filene til demomappa fra `dynamo/`, så demoen og repoet
      er samme generasjon
- [ ] 5.5 `LES-MEG.txt` i demomappa nevner `kjor.cmd` og grafene. **Retter samtidig
      en drift som allerede står der:** avsnittet ber deg finne stien
      `C:\dev\tfm-validator\rapport-2x3\funn.csv` i grafen, og den stien finnes
      ikke i fila. Nevner også `tidligfase.toml`, som ikke ligger i mappa
- [ ] 5.6 **Til brukeren:** åpne begge `.dyn` i Dynamo i Revit og se at ledningene
      sitter. En gyldig JSON-fil beviser det ikke
