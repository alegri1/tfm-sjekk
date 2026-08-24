## 1. Fest prøven før endringen

- [x] 1.1 Skriv en test per tilfelle i tabellen i proposal.md: `ifc_klasser` i
      `[pset]` skal si «toppnivå», `krev_plassering` i `[elektro]` skal si
      `[grammatikk]`, `gyldige_verdier` i `[master]` skal si `[mmi]`. Alle skal
      feile nå.
- [x] 1.2 Skriv en test på at en nøkkel som ikke finnes noe sted oppfører seg
      som før. Den skal passere både før og etter — det er den som låser at
      endringen ikke tar med seg noe den ikke skal.
- [x] 1.3 Kjør begge gruppene og bekreft at 1.1 feiler og 1.2 passerer.

## 2. Kartet over hvor nøklene hører hjemme

- [x] 2.1 Bygg kartet «feltnavn → hvor det hører hjemme» av modellenes
      `model_fields`, ikke av en håndskrevet liste. En liste driver fra modellen
      første gang noen legger til en nøkkel.
- [x] 2.2 Test at kartet finner et toppnivåfelt og et seksjonsfelt.
- [x] 2.3 Test at kartet ikke kan bli utdatert: hvert felt i hver modell skal
      finnes i kartet. Legges en nøkkel til uten at oppslaget følger med,
      feiler denne.

## 3. Meldingen

- [x] 3.1 La `_ukjente_nokler` slå opp nøkkelnavnet i kartet før den faller
      tilbake på `difflib`.
- [x] 3.2 Formuler linja som «Den hører hjemme på toppnivå.» og «Den hører
      hjemme i [grammatikk].» — beskrivende, ikke lovende. Verktøyet flytter
      ingenting.
- [x] 3.3 Test at forslaget om lignende nøkkel ikke kommer i tillegg når
      nøkkelen finnes et annet sted.

## 4. Flere steder samtidig

- [x] 4.1 Nevn alle stedene hvis nøkkelen finnes i mer enn én seksjon. Å peke
      på det første i en vilkårlig rekkefølge er en gjetning forkledd som et
      svar.
- [x] 4.2 Test det med et konstruert kart, siden tilfellet ikke finnes i
      modellene i dag.

## 5. Prøv der det brukes

- [x] 5.1 Kjør en feilstavet plassering fra kommandolinja og les meldingen som
      en BIM-koordinator ville lest den.
- [x] 5.2 Bekreft at exit-koden fortsatt er 2 og at ingen rapport skrives.
- [x] 5.3 Kjør demoen. Uendret — 17 funn.

## 6. Avslutt

- [x] 6.1 Oppdater eksempelet i README-en der den nye meldingen gjør den
      tydeligere.
- [x] 6.2 Kjør hele testsuiten, `ruff check` og `ruff format --check`.
