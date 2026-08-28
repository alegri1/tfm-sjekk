## 1. Utvalget blir stabilt

- [x] 1.1 Steg 2 i `_finn` ser alle egenskapssett framfor å returnere på første
- [x] 1.2 Velger settet med alfabetisk første navn. Skriv i koden at regelen ikke
      er klok, bare stabil og forklarlig i én setning
- [x] 1.3 Steg 1 beholder sin UTVALGSREGEL — rekkefølgen der er brukerens egen
      liste. Men den bærer nå uenige kandidater den også: design-en sa «steg 1
      røres ikke», og det gjaldt utvalget. Kravet om å melde uenighet skiller
      ikke på hvor verdien kom fra, og den mest realistiske saken —
      `TFM11_Forekomst` mot `Pset_Revit_Data` etter en Revit-runde — går
      nettopp via steg 1
- [x] 1.4 Test: to filer med ombyttet rekkefølge på settene gir samme verdi
- [x] 1.5 Test: steg 1 velger fortsatt etter oppsettets rekkefølge

## 2. Kandidatene bæres videre

- [x] 2.1 `_finn` returnerer også kandidatene som ikke ble valgt, med sett og verdi
- [x] 2.2 `Verdikilde` eller et søsken bærer dem gjennom prosessgrensa som ren data
- [x] 2.3 Bare kandidater som er ULIKE den valgte bæres — like er ikke et avvik
- [x] 2.4 Test: to like verdier gir ingen forkastet kandidat
- [x] 2.5 Test: to ulike gir én, med sett og verdi

## 3. T2

- [x] 3.1 Ny kontroll `T2`, ved siden av T1. Skriv hvorfor den hører der og ikke
      blant D-ene: dette er en motsigelse i modellen, ikke i kjøringen
- [x] 3.2 Grad feil, som T1
- [x] 3.3 Meldingen oppgir begge verdiene og begge egenskapssettene
- [x] 3.4 De øvrige kontrollene kjører på den valgte verdien som før
- [x] 3.5 Test: to ulike verdier gir T2
- [x] 3.6 Test: to like gir ikke T2
- [x] 3.7 Test: én verdi gir ikke T2

## 4. Prøvd der det brukes

- [x] 4.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 4.2 De to filene med ombyttet rekkefølge — prøven som avdekket det
- [x] 4.3 Demoen normalt: ingenting nytt
- [x] 4.4 Den federerte Snowdon-kjøringen: 24 456 objekter. Kommer det T2-funn,
      har modellen dobbeltmerking vi ikke visste om — og da er tallet i seg selv
      et funn verdt å se på
- [ ] 4.5 IKKE GJORT, bevisst. Ingenting fyrte i de faste kjøringene, så det finnes ingen rapport med T2 å åpne — det ville krevd en modell laget for formålet. Prosjekteieren valgte å hoppe over
