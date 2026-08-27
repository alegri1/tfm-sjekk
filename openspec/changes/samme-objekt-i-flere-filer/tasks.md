## 1. Kollisjonen finnes

- [ ] 1.1 `Kontekst` gir identiteter som går igjen i flere fagmodeller, med filene
- [ ] 1.2 Bare objekter i omfanget teller — delte rutenett er normale og stille
- [ ] 1.3 Test: samme identitet i to filer, i omfanget, blir funnet
- [ ] 1.4 Test: samme identitet utenfor omfanget blir ikke funnet
- [ ] 1.5 Test: én identitet flere ganger i SAMME fil er ikke dette. IFC krever
      unikhet der, men hvis en fil bryter det, er det en annen sak

## 2. D3

- [ ] 2.1 Ny kontroll `D3`, ved siden av D1 og D2. Skriv hvorfor den ikke er en
      utvidelse av dem
- [ ] 2.2 Grad advarsel. Skriv hvorfor: exit-koden er 1 uansett fra K6, og D3
      forklarer den framfor å legge til en feil
- [ ] 2.3 Meldingen navngir fagmodellene og antall objekter
- [ ] 2.4 Meldingen sier hva som ER pålitelig — funnene selv — og hva som ikke er
      det: hvilken fil de tilhører
- [ ] 2.5 Meldingen nevner den vanligste årsaken: samme modell sendt inn to ganger
- [ ] 2.6 Test: funnet fyrer, med grad advarsel
- [ ] 2.7 Test: ingen kollisjon gir ingen funn
- [ ] 2.8 Test: begge objektene står igjen — ingen sammenslåing eller forkasting

## 3. Dokumentasjonen

- [ ] 3.1 README: hva advarselen betyr og hva man gjør
- [ ] 3.2 Skriv i `kontekst.py` hvorfor `_etter_id` beholder GlobalId som nøkkel,
      så neste leser ikke tror det er en forglemmelse

## 4. Prøvd der det brukes

- [ ] 4.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [ ] 4.2 To kopier av demo-rie.ifc under ulike navn: advarselen skal forklare de
      tretten funnene
- [ ] 4.3 Den federerte Snowdon-kjøringen: INGEN D3-funn, fordi de to delte
      objektene er `IfcGrid` utenfor omfanget
- [ ] 4.4 Demoen normalt: ingenting nytt
- [ ] 4.5 **Åpne HTML-rapporten** og se at advarselen leses som en forklaring,
      ikke som enda et funn i mengden
