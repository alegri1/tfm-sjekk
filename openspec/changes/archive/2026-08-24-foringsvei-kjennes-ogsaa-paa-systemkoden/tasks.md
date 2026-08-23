## 1. Fest prøven før endringen

- [x] 1.1 Skriv en test der et objekt uten føringsvei-klasse — en
      `IfcBuildingElementProxy` — er merket `=4360.001.00`, og `4360` er
      oppgitt i oppsettet. Den skal ikke gi K8-funn. Den skal feile nå.
- [x] 1.2 Skriv en test der det samme objektet kjøres **uten** at noe er
      oppgitt. Den skal gi funn, både før og etter endringen — det er den som
      låser at standardoppførselen ikke rører seg.
- [x] 1.3 Kjør begge og bekreft at 1.1 feiler og 1.2 passerer. Passerer 1.1
      allerede, prøver den noe annet enn den tror.

## 2. Nøkkelen

- [x] 2.1 Legg `foring_systemkoder: list[str] = []` i `ElektroOppsett` i
      `config.py`, med en docstring som sier hvorfor lista er tom (§8).
- [x] 2.2 Test at standardverdien er tom. Et krav om at noe skal være tomt
      forsvinner ellers første gang noen «fyller ut» lista i god tro.

## 3. Gjenkjenningen

- [x] 3.1 Endre `Kontekst.er_foringsvei` til å ta `(objekt, tfm)` og gi sant
      når IFC-klassen **eller** systemkoden treffer.
- [x] 3.2 Oppdater kallet i `k8_elektro._a_kursnummer_utfylt`.
- [x] 3.3 Kjør hele testsuiten. `er_foringsvei` har bare én bruker, så en
      signaturendring skal ikke røre noe annet — bekreft at det stemmer.

## 4. Dekk grensene

- [x] 4.1 Test at klassen alene fortsatt holder, uten at noen systemkode er
      oppgitt.
- [x] 4.2 Test at systemkoden alene holder, på et objekt uten føringsvei-klasse.
- [x] 4.3 Test at en annen systemkode enn den oppgitte fortsatt meldes.
- [x] 4.4 Test at unntaket ikke sprer seg: et objekt unntatt på systemkoden skal
      fortsatt telle i koblingsgrafen, slik at K8b ser det.

## 5. Oppsettet

- [x] 5.1 Dokumenter `foring_systemkoder` i `tfm-sjekk.toml` med et utfylt
      eksempel i kommentaren. Kommentaren er der brukeren leter — en tom liste
      uten forklaring er en nøkkel ingen finner.
- [x] 5.2 Se over om README-en beskriver føringsvei-unntaket, og nevn i så fall
      begge kjennetegnene.

## 6. Prøv mot ekte data

- [x] 6.1 Kjør mot Snowdon-eksporten uten konfigurasjon. Skal fortsatt gi 177
      funn — endringen skal ikke røre noe før noen ber om det.
- [x] 6.2 Kjør med `foring_systemkoder = ["4360"]`. Skal gi 161: de seksten
      koblingsboksene forsvinner, og ingenting annet.
- [x] 6.3 Bekreft at de seksten som forsvant faktisk er koblingsboksene, ikke
      seksten tilfeldige objekter. Et tall som stemmer er ikke det samme som et
      tall som er riktig.
- [x] 6.4 Kjør demoen og bekreft at funntallet er uendret — 17.

## 7. Avslutt

- [x] 7.1 Kjør hele testsuiten, `ruff check` og `ruff format --check`.
