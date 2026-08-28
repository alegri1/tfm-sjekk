## 1. Tittelen kuttes ved en grense

- [x] 1.1 Utvid `_tittel` i `rapport/bcf.py` med ordgrense-trinnet mellom
      setningsgrensen og det harde kuttet. Ellipsen skal telle med i lengden.
- [x] 1.2 Strip åpne tegn — `(`, `«`, `"`, `-`, `–` — fra enden av det som ble
      igjen, etter kuttet.
- [x] 1.3 Skriv om docstringen så den beskriver alle fire trinnene og sier
      hvorfor det harde kuttet må bli liggende (tekst uten mellomrom).

## 2. Prøv titlene

- [x] 2.1 Test i `tests/test_bcf.py`: en melding uten setningsgrense innenfor
      100 tegn gir en tittel som ikke slutter midt i et ord.
- [x] 2.2 Test: en tittel som ville endt på `(` eller `«` gjør ikke det.
- [x] 2.3 Test: en tekst helt uten mellomrom kuttes fortsatt, og holder seg
      innenfor grensen.
- [x] 2.4 Test: setningsgrensen har fortsatt forrang, og gir ingen ellipse.
- [x] 2.5 Test: hver tittel er ≤ 100 tegn — for ALLE demofunnene, ikke bare for
      konstruerte strenger. Det var nettopp en test som bare sjekket lengden som
      lot det halverte ordet passere i 0.8.2.

## 3. Oppsummeringslinja

- [x] 3.1 Bygg gradsleddet i `cli.py` fra gradene som har funn, alvorligst
      først, med riktig entallsform per grad.
- [x] 3.2 Samle filnavnene i en liste der filene skrives, og bygg linja fra den
      lista framfor fra hardkodede navn.
- [x] 3.3 Bruk `ut / navn` framfor `f"{ut}/navn"`.

## 4. Prøv oppsummeringen

- [x] 4.1 Test i `tests/test_cli.py`: en kjøring med funn av alle tre grader
      nevner alle tre, og summen stemmer med antall rader i CSV-en.
- [x] 4.2 Test: en grad uten funn nevnes ikke.
- [x] 4.3 Test: «1 advarsel», ikke «1 advarsler».
- [x] 4.4 Test: alle fire filnavnene står i linja, og alle fire finnes på disk.
- [x] 4.5 Kjør den eksisterende cp1252-testen på nytt — linja har fått nye ord,
      og «→» står der fortsatt.

## 5. Se på det

- [x] 5.1 Kjør demoen og les konsollinja. Tallene skal stemme med toppen av
      HTML-rapporten: 13 feil, 1 advarsel, 3 info.
- [x] 5.2 Pakk ut `funn.bcfzip` og les alle 17 titlene. Ingen skal slutte midt i
      et ord eller på et åpent tegn.
- [x] 5.3 Oppdater README der konsollutdata er gjengitt. Linja var ikke
      gjengitt noe sted fra før; den er nå dokumentert under «Hva 'ingen funn'
      betyr», der «ingen funn» hører hjemme.
- [x] 5.4 Importer BCF-en i BIMcollab ZOOM og se på emnelista. Det er der
      titlene faktisk leses, og det eneste stedet forskjellen er poenget. Krever
      prosjekteieren — si fra framfor å hake av for noe jeg ikke har sett.
      SETT: emne 17 leser «… på tvers av 2 filer…» i emnelista, hele
      setningen står i Description, og alle 17 emnene kom med.
