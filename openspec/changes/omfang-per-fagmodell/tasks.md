## 1. Oppsettet

- [ ] 1.1 `FagmodellOppsett` med `ifc_klasser: list[str]`, og
      `fagmodell: dict[str, FagmodellOppsett]` på `Konfigurasjon`
- [ ] 1.2 `omfang_for(kildefil)` — mest spesifikke mønster vinner, ellers
      toppnivåets `ifc_klasser`
- [ ] 1.3 To like lange mønstre som treffer samme fil stopper kjøringen og
      navngir begge. Å velge det første ville vært en gjetning
- [ ] 1.4 `er_unntatt(kildefil)` — sant når fila treffer et mønster med tom liste
- [ ] 1.5 Test: mønstertreff, mest spesifikke vinner, uten treff brukes toppnivået
- [ ] 1.6 Test: to like spesifikke mønstre gir exit 2 med begge navngitt

## 2. Kontekst

- [ ] 2.1 `relevante_objekter()` slår opp omfanget per `kildefil`
- [ ] 2.2 `dekning()` teller mot samme omfang
- [ ] 2.3 `unntatte_filer()` — de som er unntatt, til D1 og til utskriften
- [ ] 2.4 Test: to filer med ulikt omfang i samme kjøring
- [ ] 2.5 Test: `med_tfm()` og `k.objekter` er uendret av unntak — det er dette
      som holder K6 i live på tvers av en unntatt fil

## 3. D1 og utskriften

- [ ] 3.1 D1 hopper over unntatte filer
- [ ] 3.2 D1 melder fortsatt tom dekning for filer som ikke er nevnt i oppsettet
- [ ] 3.3 Dekningslinja i `cli.py` viser unntaket framfor å utelate fila
- [ ] 3.4 Test: unntatt fil gir ingen D1
- [ ] 3.5 Test: uteglemt fil gir D1 som før
- [ ] 3.6 Test: unntaket står i utskriften

## 4. Kontrollene som ikke skal endres

- [ ] 4.1 Test: K1 gir ingen funn i en unntatt fil
- [ ] 4.2 Test: K6 finner duplikat mellom en unntatt og en kontrollert fil, med
      begge navngitt. Dette er kravet hele endringen finnes for
- [ ] 4.3 Test: K8 på en unntatt fil med TFM oppfører seg som før — omfanget
      styrer ikke `med_tfm()`, og det skal stå skrevet et sted som feiler

## 5. Oppsettforslaget og malen

- [ ] 5.1 De nye nøklene inn i `_gyldige_nokler` — sjekk om modelloppslaget
      dekker en `dict[str, BaseModel]`, ellers utvid det
- [ ] 5.2 Repoets `tfm-sjekk.toml` får seksjonen kommentert ut, med ARK-eksemplet
- [ ] 5.3 Vurder om `tfm-sjekk oppsett` skal foreslå unntak når en fil har null
      i omfanget. Ikke bygg det uten at det står i oppgavene — noter og spør

## 6. Prøvd der det brukes

- [ ] 6.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [ ] 6.2 Kjør mot de fire ekte eksportene i
      `C:\Users\aleks\Desktop\revit-eksport-files` med ARK unntatt.
      Venter: 675 K1 borte, RIE-ens 177 K8 urørt, ingen D1 på ARK
- [ ] 6.3 Plant ett duplikat mellom ARK og RIE og se at K6 melder det med begge
      filene navngitt. Uten denne prøven er kravet ubevist
- [ ] 6.4 Les rapporten. Er de 177 nå det første man ser?
- [ ] 6.5 **Til brukeren:** åpne BCF-en i vieweren og se at emnene fortsatt
      zoomer riktig når fire modeller er lastet
