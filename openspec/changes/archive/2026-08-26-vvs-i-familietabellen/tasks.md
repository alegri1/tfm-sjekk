## 1. Familienavnene måles

- [x] 1.1 **Til brukeren:** last ned `Snowdon Towers Sample HVAC.rvt` (23 MB) og
      `Snowdon Towers Sample Plumbing.rvt` (42 MB) til `Desktop\snowdon\`, slik at
      lenkene i Electrical-modellen løser seg
- [x] 1.2 **Til brukeren:** eksporter begge til IFC — umerket, standardoppsett
      holder. Det er familienavnene vi er ute etter, ikke egenskaper
- [x] 1.3 Les familienavn og antall ut av de to IFC-ene, gruppert per IFC-klasse
- [x] 1.4 Sammenlign med sanitærfamiliene i arkitektmodellen. Er de samme
      familier brukt begge steder, skal de ha samme kode

## 2. Tabellen

- [x] 2.1 Nye rader i `FAMILIER` i `dynamo/tfm_fra_revit.py`, gruppert etter fag
      med samme kommentarstil som de elektro
- [x] 2.2 Samme rader i `verktoy/legg_til_tfm.py`
- [x] 2.3 Kodene er funnet på (§8), og VVS-radene ligger under samme overskrift
      som sier det — forbeholdet skal ikke kunne leses som elektro-bare
- [x] 2.4 Kjør `verktoy/oppdater-grafene.py`, ellers bærer `.dyn`-filene en
      eldre kopi av skriptet

## 3. Tester

- [x] 3.1 `test_familietabellen_er_den_samme_som_i_injektoren` skal fortsatt være
      grønn — den fanger de nye radene av seg selv
- [x] 3.2 Ingen ny nøkkel skygger for en eksisterende. Testen finnes; sjekk at
      den dekker de nye
- [x] 3.3 Ny test: hver VVS-familie i tabellen gir en 3xx-systemkode, og ingen
      elektro-familie gjør det
- [x] 3.4 Test: en familie som ikke står i tabellen får fortsatt `STANDARD`, og
      `STANDARD` er uendret

## 4. Dokumentasjonen

- [x] 4.1 `dynamo/LES-MEG.md`: én tabell dekker alle fag, og hvorfor det virker —
      familienavnene kolliderer ikke på tvers av fag
- [x] 4.2 Si at undernummeret blir «00» for VVS, at det er riktig, og at K8 ikke
      rører 3xx

## 4b. Løpenummeret ruller over (lagt til underveis)

- [x] 4b.1 `tfm_id` tar systemets løpenummer i stedet for å hardkode `.001`
- [x] 4b.2 `merk` regner `divmod(teller - 1, 999)` og ruller over
- [x] 4b.3 Samme regel i `verktoy/legg_til_tfm.py`, som hardkodet `.001` likt
- [x] 4b.4 Test: 999 → `.001`, 1000 → `.002.00-JVZ001`
- [x] 4b.5 Test: alle ID-er parser etter overrulling, og ingen duplikater
- [x] 4b.6 Test: elektro er uendret — `.001` overalt
- [x] 4b.7 Prøvd mot de ekte modellene: 8959 ID-er, alle unike, null ugyldige
- [x] 4b.8 `dynamo/LES-MEG.md`: `System Name` på `IN[1]`, og at overrullingen er
      vilkårlig

## 5. Prøvd der det brukes

- [x] 5.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 5.2 **Til brukeren:** kjør grafen mot HVAC og Plumbing i Revit. Les
      `OUT[1]`: `elementer_med_tfm` skal være lik `elementer`. Er den lavere,
      mangler tabellen familier
- [x] 5.3 **Til brukeren:** lagre modellene. Det er steget som ble glemt sist, og
      merkingen levde bare i Revit-økta
- [x] 5.4 **Til brukeren:** eksporter alle seks med kartleggingsfila
- [x] 5.5 Kjørt federert: 24 456 objekter, 47 s. Null `4390` i begge RIV-modellene.
      Rørmodellen fikk 6038 med 3100 og 331 med 3600 — de siste er avtrekkskanaler,
      og at de kodes som ventilasjon er riktig
- [x] 5.6 Lest. 839 funn: RIE-ens 177 K8 og 662 K6 om delte luftsystemer mellom
      HVAC og Plumbing. De 662 drukner de 177, men de er ekte — se proposal.md.
      Prosjekteieren valgte å la dem stå
