## 1. Fest prøven før endringen

- [x] 1.1 Skriv en test per tilfelle i tabellen i proposal.md: feilstavet
      nøkkel i en seksjon, feilstavet seksjon, gyldig nøkkel i feil seksjon.
      Alle skal stoppe kjøringen. Alle skal feile nå.
- [x] 1.2 Skriv en test på at en riktig skrevet fil fortsatt leses, og at
      `[kontroller.K4]` fortsatt godtas. De skal passere både før og etter — det
      er de som låser at endringen ikke tar med seg noe den ikke skal.
- [x] 1.3 Kjør begge gruppene og bekreft at 1.1 feiler og 1.2 passerer.

## 2. Modellene avviser ukjente nøkler

- [x] 2.1 Sett `model_config = ConfigDict(extra="forbid")` på alle sju
      modellene i `config.py`.
- [x] 2.2 Kjør hele testsuiten. Feiler noe annet enn testene fra 1.1, er det et
      sted verktøyet selv sender en nøkkel modellen ikke kjenner — stopp og se
      på det framfor å lempe på kravet.

## 3. Meldingen

- [x] 3.1 Fang `ValidationError` i `Konfigurasjon.les` og oversett til en norsk
      melding som navngir nøkkelen og seksjonen den sto i.
- [x] 3.2 Foreslå nærmeste gyldige nøkkel med `difflib.get_close_matches` mot
      modellens `model_fields`. Lista skal hentes fra modellen, ikke skrives av
      — en håndskrevet liste driver fra modellen første gang noen legger til en
      nøkkel.
- [x] 3.3 Test at forslaget kommer når det finnes en som ligner, og at
      meldingen står støtt uten forslag når det ikke gjør det.
- [x] 3.4 Test at meldingen navngir seksjonen, ikke bare nøkkelen. «Ukjent
      nøkkel «type»» er ubrukelig når `type` finnes i to seksjoner.

## 4. Exit-koden

- [x] 4.1 La CLI-en gi exit 2, som ved en sti som peker feil. Samme slags feil
      fortjener samme kode.
- [x] 4.2 Test exit-koden gjennom CLI-en, ikke bare unntaket fra `les`.

## 5. Filene verktøyet selv skriver og leser

- [x] 5.1 Test at repoets egen `tfm-sjekk.toml` leses uten innsigelse. Den er
      både dokumentasjon og oppsett, og den brukes i CI-røyktesten og i
      demomappa.
- [x] 5.2 Bekreft at fila `oppsett`-kommandoen skriver fortsatt leses. Det
      finnes allerede en test som kjører forslaget gjennom `--config`; sjekk at
      den fortsatt passerer, og at den nå faktisk ville fanget
      `ifc_klasser`-feilen.

## 6. Prøv der det brukes

- [x] 6.1 Kjør demoen. Uendret — 17 funn.
- [x] 6.2 Kjør `verktoy/kjor-ci-steg.sh`, som gjenskaper røyktesten lokalt.
      Den bruker `tfm-sjekk.toml` og et generert `forslag.toml`, altså begge
      filene fra gruppe 5.
- [x] 6.3 Prøv en feilstavet nøkkel fra kommandolinja og les meldingen som en
      BIM-koordinator ville lest den. Sier den hva som er galt, hvor, og hva det
      skulle stått?

## 7. Avslutt

- [x] 7.1 Nevn i README-en at en ukjent nøkkel stopper kjøringen, der
      konfigurasjonen beskrives.
- [x] 7.2 Kjør hele testsuiten, `ruff check` og `ruff format --check`.
