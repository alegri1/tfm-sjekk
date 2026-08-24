## 1. Fest prøven før rettingen

- [x] 1.1 Lag en fikstur som skriver en modell i **fot** — samme objekter som en
      metermodell, men med `IfcConversionBasedUnit «FOOT»`. Uten den finnes det
      ingen fil i repoet der antakelsen er usann, og det er nettopp derfor
      feilen overlevde.
- [x] 1.2 Skriv en test: samme objekt i meter og i fot skal gi kamera på samme
      sted i BCF-en. Den skal feile nå.
- [x] 1.3 Skriv en test på at kameraet står innenfor noen titalls meter fra
      objektet i fot-modellen. Den skal feile nå, og med et tall som viser hvor
      galt det er.
- [x] 1.4 Kjør begge og bekreft at de feiler av de forventede grunnene.

## 2. Enheten leses

- [x] 2.1 Skriv en funksjon i `ifc/loader.py` som finner meterfaktoren av
      `IfcUnitAssignment` → `LENGTHUNIT`. Dekk `IfcSIUnit` med og uten `Prefix`,
      og `IfcConversionBasedUnit` med `ConversionFactor`.
- [x] 2.2 Test faktoren for meter (1.0), millimeter (0.001) og fot (0.3048).
- [x] 2.3 Test at en fil uten `IfcUnitAssignment` gir 1.0, og at en enhet
      verktøyet ikke forstår også gir 1.0 framfor å stoppe kjøringen.
- [x] 2.4 Slå faktoren opp **én gang per fil**, ikke per objekt. Snowdon har
      2439 objekter og ett svar.

## 3. Posisjonen blir meter

- [x] 3.1 La `_posisjon` gange koordinatene med faktoren.
- [x] 3.2 Oppdater docstringen: feltet er meter, og det er en garanti
      konsumentene kan regne med.
- [x] 3.3 Presiser beskrivelsen av `posisjon` i `modell.py` — begge stedene
      feltet er definert.

## 4. Kameraet slutter å ta forbehold

- [x] 4.1 Rett kommentaren over `KAMERAAVSTAND` i `rapport/bcf.py`: meter, uten
      «normalt». Verdiene er uendret.
- [x] 4.2 Bekreft at `bcf.py` ikke trenger å vite noe om enheter. Gjør den det,
      har omregningen havnet på feil sted.

## 5. Emner uten kamera

- [x] 5.1 Test at et funn uten kjent posisjon fortsatt gir et emne uten kamera,
      ikke et emne med kamera i origo. Et emne som sier «ingenting å zoome til»
      er ærlig; et som peker feil er ikke det.
- [x] 5.2 Test at et funn som gjelder modellen som helhet fortsatt gir emne uten
      kamera.

## 6. Prøv mot fila som avslørte det

- [x] 6.1 Kjør mot `snowdon-eksport.ifc` og les kamerakoordinatene ut av
      viewpointet. De skal være rundt 417 624, 78 737 — ikke 1 370 159.
- [x] 6.2 Regn ut avstanden fra kameraet til objektet i det samme emnet. Den
      skal være et titalls meter, ikke 969 kilometer.
- [x] 6.3 Kjør demoen. Funntallet skal være uendret — 17 — og BCF-en for
      metermodellene skal være byte-identisk med før. Endringen skal ikke røre
      noe som allerede var riktig.

## 7. Prøv der det faktisk brukes

- [x] 7.1 Legg den nye BCF-en fra Snowdon i demomappa, slik at den kan åpnes i
      en viewer. Det er den eneste prøven som teller for dette formatet — §5
      kaller BCF viktigst nettopp fordi det er der funnene tas i bruk.
- [x] 7.2 Skriv i sammendraget hva som skal sjekkes ved åpning: dobbeltklikk et
      emne, og modellen skal stå i bildet med objektet valgt.

## 8. Avslutt

- [x] 8.1 Nevn i README-en at kameraet står i meter uansett modellens enhet,
      der BCF beskrives.
- [x] 8.2 Kjør hele testsuiten, `ruff check` og `ruff format --check`.
