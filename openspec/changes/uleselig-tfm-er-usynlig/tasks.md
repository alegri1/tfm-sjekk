## 1. Tallet blir synlig

- [ ] 1.1 `Kontekst` gir antall objekter i omfanget med uleselig TFM, per fagmodell
- [ ] 1.2 Tallet utledes av `parsefeil`, som allerede finnes — ikke ved å parse på nytt
- [ ] 1.3 Test: tallet er null når alt parser, og riktig når noe ikke gjør det
- [ ] 1.4 Test: objekter UTENFOR omfanget teller ikke med

## 2. Konvensjonsfunnet

- [ ] 2.1 Ny kontroll, eller utvidelse av D1 — avgjør ut fra hvor «per fagmodell»
      allerede bor. Skriv valget i koden
- [ ] 2.2 Fyrer bare når fagmodellen HAR objekter med TFM-verdi i omfanget og
      ingen av dem parset
- [ ] 2.3 Grad advarsel, som D1. Exit-koden skal ikke endres av den
- [ ] 2.4 Meldingen navngir innstillingen som avgjør grammatikken
- [ ] 2.5 Test: alle faller ut → funn
- [ ] 2.6 Test: én parser → ikke funn
- [ ] 2.7 Test: ingen har TFM → ikke funn, K1 gjør jobben
- [ ] 2.8 Test: per fagmodell — RIE riktig, RIV feil konvensjon gir ett funn

## 3. K2 sier hva det koster

- [ ] 3.1 Meldingen får én setning om at objektet ikke er kontrollert av de øvrige
- [ ] 3.2 Ingen oppramsing av kontrollnumre — de endrer seg, og de tar plassen
- [ ] 3.3 Test: setningen står i meldingen

## 4. Rapporten

- [ ] 4.1 Dekningstabellen får kolonnen, men bare når noe falt ut
- [ ] 4.2 Konsollen oppgir det samme
- [ ] 4.3 Lot alt seg tolke, skal det sies — fravær av tall må ikke tolkes
- [ ] 4.4 Test i `tests/test_html.py`
- [ ] 4.5 Ingen ny farge uten at den finnes i begge paletter

## 5. Prøvd der det brukes

- [ ] 5.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [ ] 5.2 Kjør demomodellene med `plassering_siffer = 5`. ALT skal falle ut, og
      rapporten skal si det — ikke bare vise atten K2-funn
- [ ] 5.3 Kjør demoen normalt og se at ingenting nytt dukker opp
- [ ] 5.4 Kjør den federerte Snowdon-kjøringen — 24 456 objekter — og se at
      tallet stemmer med det K2 melder
- [ ] 5.5 **Åpne HTML-rapporten**, i lys og mørk modus. Tabellen får en kolonne til
- [ ] 5.6 Se på en K2-melding i XLSX og i BCF. Setningen er lengre nå
