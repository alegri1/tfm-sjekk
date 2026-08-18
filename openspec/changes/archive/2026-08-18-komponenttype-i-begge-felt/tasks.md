## 1. Én kilde til komponenttypen

- [x] 1.1 La `Kontekst` kunne oppgi et objekts komponenttype etter forrangsregelen:
      `%`-delen først, så typefeltet, ellers ingen.
- [x] 1.2 La samme oppslag si fra når de to feltene er uenige, slik at både T1 og
      K7 kan forholde seg til det uten å regne det ut hver for seg.
- [x] 1.3 Bruk `normaliser` fra masterlesingen til sammenligningen, så «samme
      komponenttype» har én definisjon i verktøyet.
- [x] 1.4 Test forrangsregelen: begge til stede, bare `%`-del, bare typefelt,
      ingen av delene.
- [x] 1.5 Test at mellomrom og små bokstaver ikke gjør to like verdier ulike.

## 2. Kontrollen T1

- [x] 2.0 Fjern «TFM» fra `egenskapsnavn_type`. Navnet er forekomstens eget
      kandidatnavn, så et treff på tvers av egenskapssett gir hele TFM-ID-en
      som komponenttype. Bruddet på kravet om distinkte feltnavn var usynlig
      så lenge `tfm_type` var ubrukt.

- [x] 2.1 Legg til kontrollen som melder sprik mellom de to feltene, med grad feil.
      Hold den utenfor nummerserien K1–K9, som D1.
- [x] 2.2 La meldingen oppgi begge verdiene og hvilket felt hver av dem kom fra.
- [x] 2.3 Test at sprik gir nøyaktig ett funn, og at like verdier ikke gir noe.
- [x] 2.4 Test at kontrollen kan slås av og få endret grad fra `tfm-sjekk.toml`.

## 3. K7 bruker den nye kilden

- [x] 3.1 La K7 hente komponenttypen fra oppslaget i stedet for fra `tfm.komponenttype`.
- [x] 3.2 Test at en komponenttype som bare står i typefeltet sjekkes mot mastera,
      både når den er kjent og når den er ukjent.
- [x] 3.3 Test at K7 tier om objekter der de to feltene spriker, slik at T1 er
      eneste funn.
- [x] 3.4 Test at K7s motsatte retning — oppføringer i mastera som ikke er
      modellert — også teller typer som bare står i typefeltet.

## 4. Demoen

- [x] 4.1 Utvid demomodellene med et objekt der de to feltene spriker, og ett der
      `TFM11_Type` er eneste kilde til komponenttypen.
- [x] 4.2 Utvid `FIKTIV-tfm-master.csv` slik at de nye komponenttypene som skal
      være i orden, faktisk står der — samme drift som rammet mastera før.
- [x] 4.3 Kjør demoen og les rapporten: T1 skal vise ett sprik, og K7 skal melde om
      en komponenttype som bare fantes i typefeltet.

## 5. Regresjon og dokumentasjon

- [x] 5.1 Bekreft at BCF-fila fortsatt validerer og at determinismen holder.
- [x] 5.2 Beskriv i README at komponenttypen kan stå to steder, hvilken som har
      forrang, og hva som skjer når de spriker.
