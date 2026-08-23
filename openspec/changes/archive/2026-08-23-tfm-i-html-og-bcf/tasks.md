## 1. Fest prøven før rettingen

- [x] 1.1 Skriv en test som bygger et `Funn` der `tfm` og `verdi` er ulike (som et
      K9-funn: TFM-verdien på objektet, MMI-verdien i `verdi`), skriver
      HTML-rapporten, og krever at raden inneholder TFM-verdien og **ikke**
      MMI-verdien. Den skal feile nå.
- [x] 1.2 Skriv tilsvarende test for BCF: samme `Funn`, og kommentaren i
      `markup.bcf` skal inneholde TFM-verdien og ikke MMI-verdien. Den skal
      feile nå.
- [x] 1.3 Kjør de to og bekreft at de faktisk feiler, med den forventede grunnen.
      En test som passerer før rettingen prøver noe annet enn den tror.

## 2. HTML-rapporten

- [x] 2.1 Bytt kolonneoverskriften «TFM-verdi» til «TFM» i malen i
      `rapport/html.py`.
- [x] 2.2 Bytt cellens kilde fra `f.verdi` til `f.tfm`, med samme tomhåndtering
      som før, slik at et K1-funn gir en tom celle og ikke «None».
- [x] 2.3 Bekreft at sorteringsindeksen fortsatt peker på samme kolonne.
      Kolonnen bytter innhold, ikke plass.

## 3. BCF-emnene

- [x] 3.1 La `_detaljer` i `rapport/bcf.py` bruke `f.tfm` med etiketten «TFM»,
      og la ledd et falle bort når `f.tfm` er tom — samme mønster som i dag.
- [x] 3.2 Bekreft at `Description` er uendret. Verdien funnet handler om skal
      fortsatt stå der, formulert av kontrollen.

## 4. Dekk de tomme tilfellene

- [x] 4.1 Test at et K1-funn (objektet mangler TFM) gir tomt felt i begge
      formater, ikke en plassholdertekst.
- [x] 4.2 Test at et funn uten objekt (K7s melding om en oppføring i mastera som
      ikke er modellert) gir tomt felt i begge formater.

## 5. Prøv mot demoen

- [x] 5.1 Kjør demoen og bekreft at K9-raden i `rapport.html` viser
      `++115080=4310.001.14-QLF105` under overskriften «TFM», ikke `200`.
- [x] 5.2 Bekreft at K9-emnet i `funn.bcfzip` oppgir samme TFM-verdi i
      kommentaren, og at `Description` fortsatt nevner MMI-verdien.
- [x] 5.3 Bekreft at funntallet er uendret — 17. Denne endringen skal ikke røre
      hva som finnes, bare hva rapporten kaller det.
- [x] 5.4 Bekreft at `funn.csv` og `funn.xlsx` er uendret.

## 6. Avslutt

- [x] 6.1 Kjør hele testsuiten, `ruff check` og `ruff format --check`.
- [x] 6.2 Se over om noe i README-en eller huskelappen beskriver
      HTML-kolonnene, og rett det i så fall. En anvisning som beskriver den
      gamle overskriften er den samme slags feil som denne endringen retter.
