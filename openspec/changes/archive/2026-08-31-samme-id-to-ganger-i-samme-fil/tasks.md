## 1. Identiteten telles, ikke bare filene

- [x] 1.1 La `delt_identitet` i `kontekst.py` bære både filene og antallet
      objekter per identitet, slik at de to tilfellene lar seg skille.
- [x] 1.2 Ta med identiteter som går igjen innenfor én fil.
- [x] 1.3 Skriv om docstringen. Den sier i dag at samme identitet i samme fil
      «er en annen sak» — det stemte da den ble skrevet, og gjør det ikke nå.

## 2. D3 melder begge tilfellene

- [x] 2.1 To meldinger, fordi de krever to handlinger: fjern den ene fila, eller
      eksporter fila på nytt.
- [x] 2.2 Meldingen om én fil sier at fila bryter IFC-kravet om unik identitet.
- [x] 2.3 Grupperingen per filkombinasjon står — tusen delte objekter er ett
      problem, ikke tusen funn.

## 3. K6 melder ikke et duplikat som ikke finnes

- [x] 3.1 La K6 hoppe over identitetene D3 har meldt.
- [x] 3.2 Sjekk at et ekte duplikat mellom to objekter som HAR hver sin
      identitet fortsatt meldes. Det er den kontrollen dette ikke skal koste.

## 4. `oppsett` svarer som `sjekk`

- [x] 4.1 Legg `_som_brukerfeil("modeller")` rundt `les_modeller` i
      `oppsett`-kommandoen i `cli.py`.
- [x] 4.2 Let etter flere kall til `les_modeller` og `les_modell` i pakken. Det
      var å rette stedet feilen viste seg framfor alle stedene funksjonen kalles
      som gjorde at denne ble glemt i 0.9.3.

## 5. Prøv det

- [x] 5.1 Test: to objekter i samme fil med samme GlobalId og hver sin TFM gir
      ett D3-funn med grad advarsel, og fila navngis.
- [x] 5.2 Test: det oppdiktede K6-funnet er borte. Assert på at «…JVZ002» IKKE
      meldes som brukt på to objekter — det var nettopp den setningen som var
      usann.
- [x] 5.3 Test: et ekte K6-duplikat i samme fil, med to ulike GlobalId-er,
      meldes fortsatt.
- [x] 5.4 Test: identitet delt mellom to filer gir fortsatt sitt eget funn, og
      de to meldingene er ulike.
- [x] 5.5 Test: `tfm-sjekk oppsett` på en ødelagt fil gir exit 2, en melding og
      ingen traceback.
- [x] 5.6 Test: en modell uten duplikater gir ingen D3-funn — så testen over
      ikke går grønt fordi D3 alltid fyrer.

## 6. Se på det

- [x] 6.1 Kjør demoen og se at 17 funn og exit 1 er uendret.
- [x] 6.2 Lag en rapport fra fila med duplikat identitet og les den. Advarselen
      skal si hva man gjør, og K6-feilen skal være borte.
- [x] 6.3 Kjør i cp1252-konsoll.

## 7. Forbeholdet

- [x] 7.1 MERK i koden at duplikat GlobalId er konstruert her ved å redigere en
      fikstur. Snowdon har ingen. At det forekommer i ekte eksporter er lest,
      ikke sett i denne mappa — og det skal ikke stå som mer enn det er.
