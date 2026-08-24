## 1. Fest prøven før endringen

- [x] 1.1 Skriv en test som kjører en fikstur to ganger til ulike stier og
      krever byte-identiske filer. Den skal feile nå.
- [x] 1.2 Skriv en test som dekker en modell med geometri også — der kommer
      GUID-ene også fra `ifcopenshell.template.create`, som er et eget sted å
      glemme.
- [x] 1.3 Kjør begge og bekreft at de feiler.

## 2. Generatoren

- [x] 2.1 Lag en deterministisk GUID-generator i `syntetisk.py`: fast navnerom,
      `uuid5` over «filnavn:løpenummer», komprimert til IFC-formatet.
- [x] 2.2 Skriv i kommentaren at navnerommet aldri må endres, med samme
      begrunnelse som i `rapport/bcf.py`.
- [x] 2.3 Test at to generatorer med samme frø gir samme rekke, og at to med
      ulikt frø ikke gjør det.

## 3. Ta den i bruk

- [x] 3.1 Bytt ut alle 25 kall til `guid.new()`.
- [x] 3.2 Send generatoren til `_romlig_struktur`, som lager den romlige kjeden.
- [x] 3.3 Gi `ifcopenshell.template.create` en fast `project_globalid`.
- [x] 3.4 Bekreft at ingen `guid.new()` står igjen i fila.

## 4. Prøv at det virker

- [x] 4.1 Kjør `lag_demomodell.py` to ganger og sammenlign alle åtte filene
      byte for byte.
- [x] 4.2 Lag en BCF, kjør generatoren på nytt, og bekreft at BCF-en fortsatt
      peker på objekter som finnes. Det er dette hele endringen handler om.
- [x] 4.3 Kjør demoen. Funntallet skal være uendret — 17.
- [x] 4.4 Kjør hele testsuiten. Fiksturen brukes av mange tester, og en endring
      i identiteten kan velte en test som ikke burde bry seg.

## 5. Avslutt

- [x] 5.1 Regenerer BCF-en i demomappa, så den stemmer med de nye modellene.
- [x] 5.2 Kjør `ruff check` og `ruff format --check`.
