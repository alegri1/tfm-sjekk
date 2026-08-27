## 1. Tallet blir synlig

- [x] 1.1 `Kontekst` gir antall objekter i omfanget med uleselig TFM, per fagmodell
- [x] 1.2 Tallet utledes av `parsefeil`, som allerede finnes — ikke ved å parse på nytt
- [x] 1.3 Test: tallet er null når alt parser, og riktig når noe ikke gjør det
- [x] 1.4 Test: objekter UTENFOR omfanget teller ikke med

## 2. Konvensjonsfunnet

- [x] 2.1 Ny kontroll, eller utvidelse av D1 — avgjør ut fra hvor «per fagmodell»
      allerede bor. Skriv valget i koden
- [x] 2.2 Fyrer bare når fagmodellen HAR objekter med TFM-verdi i omfanget og
      ingen av dem parset
- [x] 2.3 Grad advarsel, som D1. Exit-koden skal ikke endres av den
- [x] 2.4 Meldingen navngir innstillingen som avgjør grammatikken
- [x] 2.5 Test: alle faller ut → funn
- [x] 2.6 Test: én parser → ikke funn
- [x] 2.7 Test: ingen har TFM → ikke funn, K1 gjør jobben
- [x] 2.8 Test: per fagmodell — RIE riktig, RIV feil konvensjon gir ett funn

## 3. K2 sier hva det koster

- [x] 3.1 Meldingen får én setning om at objektet ikke er kontrollert av de øvrige
- [x] 3.2 Ingen oppramsing av kontrollnumre — de endrer seg, og de tar plassen
- [x] 3.3 Test: setningen står i meldingen

## 4. Rapporten

- [x] 4.1 Dekningstabellen får kolonnen, men bare når noe falt ut
- [x] 4.2 Konsollen oppgir det samme
- [x] 4.3 Lot alt seg tolke, skal det sies — fravær av tall må ikke tolkes
- [x] 4.4 Test i `tests/test_html.py`
- [x] 4.5 Ingen ny farge uten at den finnes i begge paletter

## 5. Prøvd der det brukes

- [x] 5.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 5.2 Kjør demomodellene med `plassering_siffer = 5`. ALT skal falle ut, og
      rapporten skal si det — ikke bare vise atten K2-funn
- [x] 5.3 Kjørt normalt: 17 funn, samme fordeling som før. D2 fyrer ikke — 1 av 6
      uleselige, ikke alle. **Merk:** `kjor.cmd` kjører demomappas binær fra
      utgivelsen, ikke arbeidstreet. Prøven må gjøres med `python -m tfm_sjekk.cli`
- [x] 5.4 Kjør den federerte Snowdon-kjøringen — 24 456 objekter — og se at
      tallet stemmer med det K2 melder
- [x] 5.5 Åpnet av brukeren 2026-08-27. Fire kolonner leser fint, tomme celler
      der ingenting falt ut
- [x] 5.6 **Fant en regresjon.** Den nye setningen dyttet K2-tittelen over 100
      tegn, og BCF kuttet den midt i et ord: «… Objektet er derfor ikk». Tittelen
      er det man ser i emnelista i en viewer. `_tittel` kutter nå ved
      SETNINGSSLUTT; K2 er tilbake til 51 tegn og komplett. De fire som fortsatt
      får ellipse er enkeltsetninger uten brudd innen grensen — uendret oppførsel
