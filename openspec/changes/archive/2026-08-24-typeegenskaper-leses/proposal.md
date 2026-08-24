## Why

Ligger TFM-verdien på typeobjektet, ser verktøyet ingenting — og K1 melder at
hvert eneste objekt mangler TFM.

Mangelen står dokumentert i `loader.py` og er prøvd i begge skjemaer
(`test_ifc.py::test_typeegenskaper_leses_ikke`). Koblingen ligger i `IsTypedBy` i
IFC4 og som en `IfcRelDefinesByType` i `IsDefinedBy` i 2x3; ingen av delene
følges.

Notatet stiller selv spørsmålet om det er verdt å lukke: «avhenger av om norske
eksporter faktisk merker på typen». Evidensen vi har er tynn i begge retninger.
Snowdon-eksporten har 127 typeobjekter og 27 med egenskapssett, men bare
Autodesks egne — `Pset_ElectricalDeviceCommon` og liknende. Vår egen
Revit-eksport har åtte typeobjekter og null egenskapssett, fordi
`revit/TFM-egenskapssett.txt` merker med `I` for instance.

Men den fila kan like gjerne si `T`. Formatet støtter det, og for **komponenttypen**
er typeobjektet det naturlige stedet: alle forekomstene av en Revit-familietype
*er* samme komponenttype, og å gjenta verdien på hver av dem er duplisering.

Det avgjørende er ikke sannsynligheten, men hva som skjer når det inntreffer:
verktøyet ser ingenting og melder at alt mangler merking. Det er den verste
slags feil — den ser ut som en modell uten TFM, ikke som et verktøy som ikke
leste etter.

## What Changes

- Verdiuttrekket følger `IsTypedBy` (IFC4) og `IfcRelDefinesByType` (2x3), og
  leser egenskapssettene på typeobjektet.
- Alle tre feltene leses: TFM-forekomst, TFM-type og MMI.
- **Forekomstens egen verdi vinner** når begge finnes. Det er standard
  IFC-semantikk: en forekomst overstyrer typen sin.
- Er en TFM-forekomst bare merket på typen, leses den derfra — og deles typen
  av flere objekter, får de samme komponentforekomst og K6 melder dem. Det er
  teknisk riktig: verdien *er* duplisert. Verktøyet skal lese det som står, ikke
  bestemme hva som var ment.
- `Verdikilde` sier hvor verdien kom fra, som før. Feltet finnes allerede og
  bærer egenskapssett og feltnavn.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `verdiuttrekk`: To nye krav. Ett om at typeobjektets egenskapssett skal leses,
  i begge skjemaene. Ett om at forekomstens egen verdi vinner over typens. De
  åtte eksisterende kravene står uendret — forrangen mellom konfigurert felt,
  gjenkjent feltnavn og gjetning gjelder like fullt, den gjelder nå bare på to
  steder.

## Impact

- **`ifc/loader.py`:** `_psets` følger også typekoblingen. Rekkefølgen avgjør
  forrangen, så typens sett legges inn først og forekomstens over.
- **Uendret:** kontrollene, rapportformatene, konfigurasjonen. Ingen ny nøkkel:
  de samme `pset`-navnene og feltnavnene gjelder begge steder.
- **Prøving:** `test_typeegenskaper_leses_ikke` skal snus. Den finnes for begge
  skjemaer, og det er nettopp fordi koblingen heter forskjellige ting der.
  Mot Snowdon skal funntallet stå stille — den har ingen TFM på typen, og
  endringen skal ikke røre en modell som ikke bruker den.
