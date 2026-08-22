## Why

Kjørt på en ekte Revit-eksport — Autodesks Snowdon Towers, 2439 objekter, med
TFM-merking utledet av modellens egne kursnumre — ga verktøyet dette:

```
K1     2
K2     3
K6     6      elleve funn, alle lagt inn med vilje
K8  1018      ingen la inn
```

De 1018 er `IfcFlowSegment` og `IfcFlowFitting` — kabelrør og bend — pluss noe
utstyr. K8a krever kursnummer av alt som ligger i et NS 3451 kapittel 4- eller
5-system, og føringsveier ligger ikke *på* en kurs. De **bærer** kurser.

En RIE som kjørte dette på sin egen modell ville fått 1018 meldinger om kabelrør
og 11 om ekte feil. Hen ville lukket rapporten før hun fant dem.

Unntaket finnes allerede i prinsippet. K8a hopper over fordelinger, med
begrunnelsen «tavla er roten kursene går ut fra, ikke noe som selv ligger på en
kurs». Det argumentet gjelder ordrett for føringsveier — regelen er bare for
smal.

Ingen av de åtte demomodellene kunne avslørt dette. De har tre til åtte objekter
hver, og ingen føringsveier.

## What Changes

- Nytt oppsett `elektro.foring_klasser` med IFC-klassene som fører kurser
  framfor å ligge på dem: `IfcFlowSegment`, `IfcFlowFitting`,
  `IfcCableCarrierSegment`, `IfcCableCarrierFitting`, `IfcCableSegment`,
  `IfcCableFitting`.
- **K8a hopper over disse**, på samme måte som den allerede hopper over
  fordelinger, og av samme grunn.
- Ingen annen del av K8 endres. K8b og K8c leser koblingsgrafen og
  kursgrupperingen, og føringsveier hører hjemme i begge.
- De 168 objektene som står igjen — lamper og stikk uten kursnummer — meldes som
  før, ett funn per objekt. Det er en ekte merkefeil, og hvert objekt skal kunne
  finnes i en viewer gjennom sin egen BCF-sak.

Etter dette gir samme modell **179 funn i stedet for 1029**, og de handler om
merking framfor om hva slags objekt noe er.

## Capabilities

### Modified Capabilities

Ingen skrevet ned ennå. K8 har aldri hatt en spesifikasjon i `openspec/specs/` —
kontrollen er beskrevet i §4 og i sin egen docstring, men ingen delta er skrevet
om den før nå.

### New Capabilities
- `kursnummer`: Når undernummeret i en TFM-ID skal leses som et kurs-/sløyfe­nummer,
  og hvilke objekter kravet ikke gjelder for. To slags objekter er unntatt av
  samme grunn — fordelingen er roten kursene går ut fra, og føringsveien er det
  som bærer dem. Ingen av dem ligger på en kurs.

## Impact

- **`config.py`:** `ElektroOppsett.foring_klasser`.
- **`kontekst.py`:** `er_foringsvei(objekt)`, ved siden av `er_fordeling`.
- **`kontroller/k8_elektro.py`:** ett hopp til i K8a.
- **Uendret:** K8b, K8c, alle andre kontroller, uttrekket, rapportene.
- **Prøving:** en fikstur med rør og bend, og en kjøring mot Snowdon-modellen der
  tallet skal falle fra 1029 til 179. Det siste kan bare gjøres lokalt —
  modellen er Autodesks og ligger ikke i repoet.
