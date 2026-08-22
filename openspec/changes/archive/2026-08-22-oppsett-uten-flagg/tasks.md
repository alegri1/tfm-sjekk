## 1. Konfigurasjonen bærer stier

- [x] 1.1 Felter for TFM-master, systemtabell og komponenttabell i `Konfigurasjon`
- [x] 1.2 `Konfigurasjon.kilde: Path | None`, satt av `les()` — objektet som bærer
      stiene skal bære opphavet sitt
- [x] 1.3 Oppslag som løser en relativ sti mot `kilde.parent`, og lar en absolutt
      sti stå
- [x] 1.4 Tester: relativ sti løst riktig fra en helt annen arbeidskatalog,
      absolutt sti urørt, ingen `kilde` når standardverdiene brukes

## 2. Å finne fila

- [x] 2.1 `finn_oppsett(modeller, arbeidskatalog)`: modellens mappe først, så
      arbeidskatalogen, første treff vinner
- [x] 2.2 Tester per krav: hos modellen, i arbeidskatalogen, begge steder
      (modellen vinner), ingen steder

## 3. Kommandoene

- [x] 3.1 `sjekk` bruker funnet oppsett når `--config` mangler
- [x] 3.2 `oppsett` gjør det samme — den leser allerede `--config`
- [x] 3.3 Meldingslinja først i utskriften: hvilken fil, eller at ingen ble funnet
- [x] 3.4 Et flagg vinner over konfigurasjonen, for hver av de tre stiene
- [x] 3.5 Tester i `tests/test_cli.py`, egen prosess: full kjøring uten et eneste
      flagg, og at linja sier hvilken fil som ble lest

## 4. En sti som peker feil

- [x] 4.1 En sti fra konfigurasjonen som ikke finnes stopper kjøringen
- [x] 4.2 Meldingen navngir både stien slik den sto i fila og stien den ble løst
      til — det er forskjellen mellom dem som forvirrer
- [x] 4.3 Test: skrivefeil i stien gir en feil, ikke «hoppet over»
- [x] 4.4 Test: ingen sti oppgitt gir fortsatt «hoppet over», som før

## 5. Demo og prøving hos konsumenten

- [x] 5.1 `eksempler/tfm-sjekk-full.toml` med stier til FIKTIV-tabellene, som
      viser formen
- [x] 5.2 Kjør demoen uten et eneste flagg og se at alle elleve kontrollene kjører
- [x] 5.3 Kjør fra en annen mappe enn modellen ligger i — det er tilfellet der
      «ved siden av modellen» og «arbeidskatalogen» skiller lag
- [x] 5.4 Prøv dra-og-slipp av en IFC-fil oppå binæren, med oppsettet hos modellen
- [x] 5.5 README: vis den korte kommandoen først, og de fem flaggene som det du
      gjør når du ikke har et oppsett ennå
- [x] 5.6 `tfm-sjekk.toml` i repoet får de tre feltene som kommenterte eksempler
