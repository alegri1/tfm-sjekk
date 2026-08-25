## 1. Oppsettet

- [x] 1.1 `FagmodellOppsett` med `ifc_klasser: list[str]`, og
      `fagmodell: dict[str, FagmodellOppsett]` på `Konfigurasjon`
- [x] 1.2 `omfang_for(kildefil)` — mest spesifikke mønster vinner, ellers
      toppnivåets `ifc_klasser`
- [x] 1.3 To like lange mønstre som treffer samme fil stopper kjøringen og
      navngir begge. Å velge det første ville vært en gjetning
- [x] 1.4 `er_unntatt(kildefil)` — sant når fila treffer et mønster med tom liste
- [x] 1.5 Test: mønstertreff, mest spesifikke vinner, uten treff brukes toppnivået
- [x] 1.6 Test: to like spesifikke mønstre gir exit 2 med begge navngitt

## 2. Kontekst

- [x] 2.1 `relevante_objekter()` slår opp omfanget per `kildefil`
- [x] 2.2 `dekning()` teller mot samme omfang
- [x] 2.3 `unntatte_filer()` — de som er unntatt, til D1 og til utskriften
- [x] 2.4 Test: to filer med ulikt omfang i samme kjøring
- [x] 2.5 Test: `med_tfm()` og `k.objekter` er uendret av unntak — det er dette
      som holder K6 i live på tvers av en unntatt fil

## 3. D1 og utskriften

- [x] 3.1 D1 hopper over unntatte filer
- [x] 3.2 D1 melder fortsatt tom dekning for filer som ikke er nevnt i oppsettet
- [x] 3.3 Dekningslinja i `cli.py` viser unntaket framfor å utelate fila
- [x] 3.4 Test: unntatt fil gir ingen D1
- [x] 3.5 Test: uteglemt fil gir D1 som før
- [x] 3.6 Test: unntaket står i utskriften

## 4. Kontrollene som ikke skal endres

- [x] 4.1 Test: K1 gir ingen funn i en unntatt fil
- [x] 4.2 Test: K6 finner duplikat mellom en unntatt og en kontrollert fil, med
      begge navngitt. Dette er kravet hele endringen finnes for
- [x] 4.3 Test: K8 på en unntatt fil med TFM oppfører seg som før — omfanget
      styrer ikke `med_tfm()`, og det skal stå skrevet et sted som feiler

## 5. Oppsettforslaget og malen

- [x] 5.1 De nye nøklene inn i `_gyldige_nokler` — sjekk om modelloppslaget
      dekker en `dict[str, BaseModel]`, ellers utvid det
- [x] 5.2 Repoets `tfm-sjekk.toml` får seksjonen kommentert ut, med ARK-eksemplet
- [x] 5.3 Vurdert, og IKKE bygget. `tfm-sjekk oppsett` ser at en fil har null i
      omfanget, men ikke hvorfor — den kan ikke skille «arkitektmodell som skal
      unntas» fra «elektromodell der `ifc_klasser` er for smal». De to krever
      motsatt handling, og et forslag som gjetter feil ville slått av
      kontrollene på riktig fil. D1-meldingen stiller allerede spørsmålet;
      svaret er prosjektets. Tas opp med brukeren.

## 6. Prøvd der det brukes

- [x] 6.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 6.2 Kjør mot de fire ekte eksportene i
      `C:\Users\aleks\Desktop\revit-eksport-files` med ARK unntatt.
      Venter: 675 K1 borte, RIE-ens 177 K8 urørt, ingen D1 på ARK
- [x] 6.3 Plant ett duplikat mellom ARK og RIE og se at K6 melder det med begge
      filene navngitt. Uten denne prøven er kravet ubevist
- [x] 6.4 Les rapporten. Er de 177 nå det første man ser?
- [x] 6.5 BCF-en åpnet i vieweren med alle fire modellene lastet, 2026-08-25.
      Emnene zoomer riktig. Bekreftet av brukeren
