## Why

Dobbeltklikker du et funn fra Snowdon-kjøringen i en BCF-viewer, forsvinner
modellen ut av bildet.

Kameraet i viewpointet skrives med objektets posisjon slik den står i IFC-fila.
BCF 2.1 krever meter. Snowdon-eksporten er i **fot**
(`IfcConversionBasedUnit «FOOT» = 0.3048 METRE`), og da havner kameraet her:

    skrevet i BCF (leses som meter):  1 370 159, 258 324, 786
    objektets faktiske posisjon:        417 624,  78 737, 240
    avstand:                                                969 km

Vieweren gjør nøyaktig som den blir bedt om. Modellen «krasjer» ikke — den er
utenfor synsfeltet. Alle 177 emnene i den kjøringen er rammet.

Antakelsen står skrevet i koden, og det er den som brakk:

    # Kameraets plassering i forhold til objektet, i modellens enhet (normalt
    # meter).
    KAMERAAVSTAND = 8.0

«Normalt meter» holdt for hver eneste fikstur vi har: `visning.ifc` er
`IfcSIUnit METRE`, og `demo-elektro.ifc` har ingen enhetsangivelse i det hele
tatt. Det var først en ekte Revit-eksport av et amerikansk prosjekt som viste at
antakelsen var en antakelse.

BCF er det formatet §5 kaller viktigst — «forskjellen mellom «interessant
skript» og «noe vi tar i bruk»». Et emne som sender vieweren 969 km ut i det
blå er verre enn et emne uten kamera: det ser ut som verktøyet fant noe, og
etterlater brukeren med å lure på om modellen er ødelagt.

## What Changes

- Objektets posisjon regnes om til **meter** når modellen leses, ut fra
  lengdeenheten i fila. Feltet `posisjon` er meter overalt etter det.
- `KAMERAAVSTAND` og `KAMERAHOYDE` betyr meter uten forbehold. I dag er de i
  modellens enhet, så i en fot-modell står kameraet 8 fot unna og ikke 8 meter.
- En fil uten lengdeenhet leses som meter. IFC krever en enhetsangivelse på
  `IfcProject`, så en fil uten er ufullstendig — og meter er den eneste
  antakelsen som ikke gjør noe verre.
- **Uendret:** kontrollene, funnene, HTML, CSV og XLSX. Bare kameraet i
  BCF-viewpointet flytter seg.

## Capabilities

### New Capabilities

- `synsvinkel`: Hva et BCF-emne garanterer om synsvinkelen det gjenoppretter.
  Et utvalg alene er ikke nok — en viewer trenger et kamera, og kameraet må stå
  i den enheten formatet krever. Ordet er kodens eget: «en viewer gjenoppretter
  en synsvinkel».

### Modified Capabilities

Ingen. `funnformat` sier hvilke felter hvert format bærer, ikke hvor kameraet
peker.

## Impact

- **`ifc/loader.py`:** `_posisjon` regner om til meter. Enheten leses av
  `IfcUnitAssignment` på prosjektet, én gang per fil.
- **`rapport/bcf.py`:** kommentaren over `KAMERAAVSTAND` slutter å ta forbehold.
  Ingen regning her — posisjonen er allerede meter.
- **Uendret:** `modell.py` (feltet er det samme, betydningen er presisert),
  kontrollene, de tre andre rapportformatene.
- **Prøving:** ingen fikstur har en annen enhet enn meter, og det er derfor
  feilen overlevde. Testene trenger en modell i fot, og prøven er at kameraet
  havner der objektet er — ikke bare at det finnes et kamera.
  `snowdon-eksport.ifc` er fasit: kameraet skal ligge innenfor noen titalls
  meter fra objektet, ikke 969 kilometer.
