## Why

`Funn.verdi` er dokumentert som «den aktuelle TFM-verdien, om relevant», men det
er ikke det den er. Den er *verdien funnet handler om*, og kontrollene kan
overstyre den: K9 legger MMI-verdien der, fordi det er MMI-en funnet gjelder.

Det er riktig for meldingen og galt som nøkkel. Kolonnen bærer to ting samtidig,
og den som leser fila kan ikke se hvilken av dem hun har fått.

Det ble oppdaget i praksis. Dynamo-skriptet som kobler funn tilbake til
Revit-elementer matcher på TFM-verdien, og et K9-funn med `verdi = "200"` festet
seg aldri til noe element. Løsningen der ble å lære elementets TFM fra søskenrader
med samme `global_id` — men et element som *bare* har et K9-funn har ingen
søskenrad, og faller da ut i stillhet.

En egen kolonne med elementets egen TFM-verdi gjør koblingen sikker i stedet for
utledet, og gjør `verdi` ærlig om hva den er.

## What Changes

- Ny kolonne `tfm` i `funn.csv` og en tilsvarende kolonne i `funn.xlsx`. Den
  inneholder **objektets egen TFM-forekomstverdi**, uansett hva funnet handler om.
- Tom for funn som ikke gjelder et objekt — K7s meldinger om mastera hører ikke
  til noe element.
- `verdi` beholder betydningen sin og endres ikke. Beskrivelsen rettes til å si
  hva den faktisk er, framfor å love noe den ikke holder.
- HTML-rapporten er uendret. Den leses, den behandles ikke, og TFM-verdien står
  allerede der for de aller fleste funn.
- Dynamo-skriptet bruker den nye kolonnen når den finnes, faller tilbake på
  søskenrad-utledningen når den ikke gjør, og **oppgir i statistikken hvilken vei
  som ble brukt**.

## Capabilities

### New Capabilities
- `funnformat`: Hva de maskinlesbare rapportene garanterer om hvert funn — hvilke
  felter som alltid gjelder samme ting, hvilke som avhenger av kontrollen, og hva
  som er tomt når et funn ikke gjelder et objekt. Formatet er en kontrakt: det
  leses av skript, av Dynamo og av Excel, og et felt som betyr to ting kan ikke
  brukes til noen av dem.

### Modified Capabilities

Ingen. Ingen kontroll endrer hva den finner eller melder.

## Impact

- **`modell.py`:** nytt felt `Funn.tfm`, satt av `for_objekt` fra objektets
  `tfm_forekomst`. Beskrivelsen på `verdi` rettes.
- **`rapport/csv_rapport.py`:** `tfm` inn i `KOLONNER`, før `verdi`.
- **`rapport/xlsx.py`:** tilsvarende kolonne med norsk etikett.
- **`dynamo/tfm_til_revit.py`:** leser `tfm` når den finnes, og rapporterer
  hvilken nøkkelkilde som ble brukt.
- **Uendret:** kontrollene, `tfm_sjekk.ifc`, HTML- og BCF-rapportene.
- **Prøving:** `tests/test_dynamo.py` går allerede gjennom prosjektets egen
  CSV-skriver, så en endring i kolonnene fanges der. Rundturen skal prøves på
  demomodellene: et element med bare et K9-funn skal nå kobles.
