## 1. Datamodellen

- [x] 1.1 `ForeslattGrammatikk` i `oppsett/modell.py`: innstillingens navn, verdien
      som foreslås, antall verdier den løser, og antall som allerede parser
- [x] 1.2 `Oppsettforslag.grammatikk: list[ForeslattGrammatikk]`, og `har_noe()`
      utvidet slik at et forslag med bare grammatikk ikke er tomt

## 2. Utledningen

- [x] 2.1 `_grammatikkforslag(kontekst)` i `oppsett/utled.py`: for hver kandidat,
      bygg grammatikken med den slått av og prøv å parse hver verdi som feiler i dag
- [x] 2.2 Foreslå bare når **alle** går igjennom — en innstilling som løser noen av
      dem peker på merkefeil, ikke på fase
- [x] 2.3 Kandidatene er `krev_plassering` og `krev_komponenttype`, hver bare når
      den er slått på i `kontekst.config`
- [x] 2.4 Ingen sifferantall og ingen andre formkrav blant kandidatene
- [x] 2.5 Test per krav i spesifikasjonen, mot `Kontekst` bygget i minnet:
      tidligfase foreslås, blandede feil foreslår ingenting, allerede valgfri
      foreslås ikke, sifferantall foreslås aldri
- [x] 2.6 Test på at to kandidater kan slå til samtidig uten at den ene maskerer
      den andre

## 3. Skriveren

- [x] 3.1 `[grammatikk]`-tabellen i `oppsett/toml_ut.py`, plassert etter
      toppnivånøklene og før `[pset]`
- [x] 3.2 Kommentar over hver innstilling med begge tallene: hvor mange verdier den
      løser, og hvor mange som allerede parser
- [x] 3.3 Test som leser et **sammensatt** forslag — grammatikk, egenskapssett og
      klasse — tilbake gjennom `Konfigurasjon.les` og slår fast at alle tre er i
      kraft. Skrevet som en prøve på utfallet, ikke på rekkefølgen

## 4. Kommandoen

- [x] 4.1 `oppsett` skal ikke melde «oppsettet dekker modellene som de er» når det
      finnes et grammatikkforslag
- [x] 4.2 Test i `tests/test_cli.py`, egen prosess, mot `tidligfase.ifc`

## 5. Rundturen

- [x] 5.1 Test: forslag utledet av en tidligfasemodell, brukt som konfigurasjon på
      samme modell, får verdiene til å parse
- [x] 5.2 Test: andre kjøring med eget forslag gir ingenting å foreslå

## 6. Demo og prøving hos konsumenten

- [x] 6.1 Kjør `tfm-sjekk oppsett eksempler/tidligfase.ifc` og se at den nå
      foreslår `krev_plassering = false` med begge tallene
- [x] 6.2 Bruk forslaget som `--config` i en `sjekk`-kjøring: de fem K2-funnene
      skal forsvinne og K6-duplikatet komme fram
- [x] 6.3 Kjør i en cp1252-konsoll
- [x] 6.4 README: utvid avsnittet om tidligfase med at verktøyet nå finner
      innstillingen selv, framfor at brukeren må kjenne den
- [x] 6.5 Røyktesten i `.github/workflows/bygg.yml`: `oppsett` på tidligfase.ifc
      fra binæren, og forslaget brukt som `--config`
