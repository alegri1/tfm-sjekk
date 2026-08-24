## 1. Snu prøven som dokumenterer mangelen

- [x] 1.1 `test_ifc.py::test_typeegenskaper_leses_ikke` beskriver dagens
      oppførsel og finnes for begge skjemaer. Skriv den om til å kreve at
      verdien leses. Den skal feile nå.
- [x] 1.2 Behold begge skjemaene. Koblingen heter forskjellige ting i IFC4 og
      2x3, og en test som bare dekker det ene ville sagt god dag.
- [x] 1.3 Kjør og bekreft at den feiler i begge.

## 2. Fiksturen må kunne merke på typen

- [x] 2.1 Gi `lag_modell` mulighet til å legge egenskapssettet på et
      typeobjekt framfor på forekomsten. Uten det finnes ingen modell i repoet
      der mangelen kan prøves.
- [x] 2.2 Dekk begge skjemaene: `IsTypedBy` finnes ikke i 2x3, der går
      koblingen gjennom `IsDefinedBy`.
- [x] 2.3 Test at fiksturen faktisk lager det den lover — at typeobjektet har
      settet, og at forekomsten ikke har det.

## 3. Uttrekket følger typen

- [x] 3.1 La `_psets` lese typeobjektets `HasPropertySets` før objektets egne,
      slik at forekomsten overstyrer av seg selv.
- [x] 3.2 Følg koblingen i begge skjemaer.
- [x] 3.3 Oppdater docstringen: MANGEL-avsnittet erstattes av en beskrivelse av
      hva som nå leses og i hvilken rekkefølge.

## 4. Forrangen

- [x] 4.1 Test at forekomstens verdi vinner når begge har den.
- [x] 4.2 Test at typens brukes når forekomsten ikke har noe.
- [x] 4.3 Test at et objekt uten type virker som før.
- [x] 4.4 Test at en type uten egenskapssett virker som før.
- [x] 4.5 Test at `Verdikilde` fortsatt oppgir egenskapssett og feltnavn.

## 5. Prøv mot ekte data

- [x] 5.1 Kjør mot Snowdon-eksporten. Funntallet skal stå stille — den har
      ingen TFM på typen, og endringen skal ikke røre en modell som ikke bruker
      den.
- [x] 5.2 Kjør demoen. Uendret — 17 funn.
- [x] 5.3 Lag en modell merket på typen og kjør verktøyet på den. Før ga en slik
      modell K1 på hvert objekt; nå skal den leses.

## 6. Avslutt

- [x] 6.1 Nevn i README-en at merking på typen leses, der verdiuttrekket
      beskrives.
- [x] 6.2 Kjør hele testsuiten, `ruff check` og `ruff format --check`.
