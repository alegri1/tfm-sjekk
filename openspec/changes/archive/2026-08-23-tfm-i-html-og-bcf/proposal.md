## Why

HTML-rapporten og BCF-en kaller et felt «TFM-verdi» og legger noe annet i det.

`Funn.verdi` er verdien funnet handler om, og K9 overstyrer den med MMI-verdien.
CSV og XLSX fikk et eget `tfm`-felt i `tfm-kolonne-i-funn` og skiller nå de to.
HTML og BCF ble bevisst holdt utenfor, med to begrunnelser som begge handlet om
*kobling*: leseren ser TFM-verdien allerede, og BCF peker på objekter med
GlobalId. Begge holder for kobling. Ingen av dem dekker etiketten.

Følgen er konkret. Et K9-funn i HTML-rapporten står slik:

    K9 | info | demo-elektro.ifc | IfcOutlet | 200 | MMI «200» avviker fra …

Kolonneoverskriften sier «TFM-verdi». Innholdet er en MMI-verdi. Og fordi
tabellen ikke har noen GlobalId-kolonne heller, sier raden ikke hvilket uttak det
gjelder — funnet er ikke til å handle på. BCF-kommentaren gjør det samme:
`TFM-verdi: 200`, og TFM-strengen finnes ingen steder i emnet.

Dette er de to formatene §5 løfter fram: BCF er «viktigst», HTML-rapporten er
«det folk deler i Teams». Verktøyet skal si fra når det ikke kan svare — her
svarer det feil, med selvsikker etikett.

## What Changes

- **HTML-rapporten:** kolonnen «TFM-verdi» blir «TFM» og inneholder objektets
  egen TFM-forekomstverdi, uansett hvilken kontroll som meldte. Tabellen blir
  ikke bredere.
- **BCF-kommentaren:** `TFM-verdi: <verdi>` blir `TFM: <objektets TFM>`.
- Verdien funnet handler om går ikke tapt: den står allerede i meldinga, som
  begge formater viser i sin helhet («MMI «200» avviker fra resten av systemet
  …»). Ingen av de to formatene mister informasjon.
- Tomt felt der objektet mangler TFM (K1) eller funnet ikke gjelder et objekt
  (K7s meldinger om mastera) — samme regel som i CSV og XLSX.
- **CSV, XLSX, kontrollene og `Funn.verdi` er uendret.** Ingen kontroll endrer
  hva den finner eller melder.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `funnformat`: Kravet «De maskinlesbare rapportene skal ha samme felter»
  erstattes. Det var avgrenset til formatene som behandles videre, og fritok
  uttrykkelig rapporten til lesing fra å bære objektets TFM-verdi — et fritak
  som hvilte på at leseren ser TFM-verdien likevel, og som derfor ikke holder
  for K9. Avgrensningen selv er blitt feil, så kravet byttes ut med ett som
  gjelder alle rapportformatene, med uendret krav til CSV og XLSX.

  I tillegg kommer et nytt krav: ingen rapport får merke et felt som TFM når
  feltet inneholder noe annet, uansett hvilket format det er.

## Impact

- **`rapport/html.py`:** kolonneoverskriften og cellen; `f.verdi` → `f.tfm`.
  Sorteringsindeksen (`sorter(4)`) er uendret — kolonnen bytter innhold, ikke
  plass.
- **`rapport/bcf.py`:** `_detaljer` bruker `f.tfm` og etiketten «TFM».
- **Uendret:** kontrollene, `modell.py`, `rapport/csv_rapport.py`,
  `rapport/xlsx.py`, `tfm_sjekk.ifc`, Dynamo-skriptet.
- **Prøving:** demomodellene har nøyaktig ett funn der `tfm` og `verdi` er ulike
  — K9-avviket i `demo-elektro.ifc`. Det funnet er hele prøven, og uten det ville
  en test av dette ikke kunne skille rett fra galt. Testene skal kontrollere
  begge formater på nettopp den raden, og at et K1-funn gir tomt felt framfor
  strengen «None».
