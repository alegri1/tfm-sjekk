## 1. Utvalget blir stabilt

- [ ] 1.1 Steg 2 i `_finn` ser alle egenskapssett framfor å returnere på første
- [ ] 1.2 Velger settet med alfabetisk første navn. Skriv i koden at regelen ikke
      er klok, bare stabil og forklarlig i én setning
- [ ] 1.3 Steg 1 røres ikke — rekkefølgen der er brukerens egen liste
- [ ] 1.4 Test: to filer med ombyttet rekkefølge på settene gir samme verdi
- [ ] 1.5 Test: steg 1 velger fortsatt etter oppsettets rekkefølge

## 2. Kandidatene bæres videre

- [ ] 2.1 `_finn` returnerer også kandidatene som ikke ble valgt, med sett og verdi
- [ ] 2.2 `Verdikilde` eller et søsken bærer dem gjennom prosessgrensa som ren data
- [ ] 2.3 Bare kandidater som er ULIKE den valgte bæres — like er ikke et avvik
- [ ] 2.4 Test: to like verdier gir ingen forkastet kandidat
- [ ] 2.5 Test: to ulike gir én, med sett og verdi

## 3. T2

- [ ] 3.1 Ny kontroll `T2`, ved siden av T1. Skriv hvorfor den hører der og ikke
      blant D-ene: dette er en motsigelse i modellen, ikke i kjøringen
- [ ] 3.2 Grad feil, som T1
- [ ] 3.3 Meldingen oppgir begge verdiene og begge egenskapssettene
- [ ] 3.4 De øvrige kontrollene kjører på den valgte verdien som før
- [ ] 3.5 Test: to ulike verdier gir T2
- [ ] 3.6 Test: to like gir ikke T2
- [ ] 3.7 Test: én verdi gir ikke T2

## 4. Prøvd der det brukes

- [ ] 4.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [ ] 4.2 De to filene med ombyttet rekkefølge — prøven som avdekket det
- [ ] 4.3 Demoen normalt: ingenting nytt
- [ ] 4.4 Den federerte Snowdon-kjøringen: 24 456 objekter. Kommer det T2-funn,
      har modellen dobbeltmerking vi ikke visste om — og da er tallet i seg selv
      et funn verdt å se på
- [ ] 4.5 **Åpne HTML-rapporten** hvis noe fyrer
