## 1. Datamodellen

- [x] 1.1 Nytt felt `Funn.tfm: str | None` i `modell.py`, med en beskrivelse som
      sier at det alltid er objektets egen TFM-forekomstverdi
- [x] 1.2 `for_objekt` setter det fra `objekt.tfm_forekomst`, **uten** en parameter
      kontrollene kan sende inn — det er overstyrbarheten som gjorde `verdi`
      ubrukelig som nøkkel
- [x] 1.3 Rett beskrivelsen på `verdi` slik at den sier hva feltet faktisk er:
      verdien funnet handler om, som kan være noe annet enn TFM-verdien

## 2. Rapportene

- [x] 2.1 `tfm` inn i `KOLONNER` i `csv_rapport.py`, plassert før `verdi`
- [x] 2.2 Tilsvarende kolonne i `xlsx.py` med etiketten `TFM`, ved siden av
      `TFM-verdi`
- [x] 2.3 HTML og BCF røres ikke — slå fast at ingen av dem har en kolonneliste
      som må følges med

## 3. Tester for formatet

- [x] 3.1 K2-funn: `tfm` og `verdi` er like
- [x] 3.2 K9-funn med MMI-verdi: `tfm` er TFM-verdien, `verdi` er MMI-verdien, og
      de to er ulike
- [x] 3.3 K1-funn på objekt uten TFM: `tfm` er tom
- [x] 3.4 K7-funn om mastera: både `tfm` og `global_id` er tomme
- [x] 3.5 De samme funnene skrevet til CSV og XLSX: begge har feltet
- [x] 3.6 Kontrollene kan ikke sette `tfm` — verifiser at signaturen til
      `for_objekt` ikke tar det imot

## 4. Dynamo-koblingen

- [x] 4.1 `tfm_per_element` leser `tfm`-kolonnen når den finnes
- [x] 4.2 Faller tilbake på søskenrad-utledningen når kolonnen mangler
- [x] 4.3 `statistikk` får et felt som sier hvilken vei som ble brukt
- [x] 4.4 Test: et element med **bare** et K9-funn kobles nå — det er tilfellet
      som falt ut i stillhet før
- [x] 4.5 Test: rader uten `tfm`-kolonne gir fortsatt riktig kobling, og
      statistikken sier at nøkkelen ble utledet

## 5. Demo og prøving hos konsumenten

- [x] 5.1 Kjør demoen og se at `funn.csv` har kolonnen, og at K9-raden har ulik
      `tfm` og `verdi`
- [x] 5.2 Åpne `funn.xlsx` i Excel og se at kolonnen er der og lar seg filtrere
- [x] 5.3 `dynamo/LES-MEG.md`: beskriv de to feltene og hva som skiller dem, og
      at statistikken sier hvilken nøkkelkilde som ble brukt
- [x] 5.4 Kjør Dynamo-grafen på nytt mot demomodellen og se at `nokkel_fra` sier
      at kolonnen ble brukt
