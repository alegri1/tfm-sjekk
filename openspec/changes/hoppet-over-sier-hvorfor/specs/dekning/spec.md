## ADDED Requirements

### Requirement: En hoppet kontroll skal si hvorfor den ikke kjørte

Oppgir verktøyet at en kontroll ble hoppet over, SKAL det oppgi årsaken. Årsaken
SKAL skille mellom at kontrollen er slått av i oppsettet, at data den krever
mangler, og at den ikke er implementert ennå.

Årsaken SKAL følge med både til konsollen og til rapporten.

De tre er motsatte handlinger for den som leser: la det være, skaff dataene,
vent på en senere utgave. Ordet «hoppet over» alene sier ikke hvilken, og en
kontroll som aldri kjørte er verre enn en fagmodell uten objekter i omfanget —
den så ikke engang etter.

#### Scenario: Kontrollen mangler data
- **WHEN** en kontroll krever en kodetabell eller en TFM-master som ikke er
  oppgitt
- **THEN** oppgis det at kontrollen ble hoppet over fordi dataene mangler

#### Scenario: Kontrollen er slått av
- **WHEN** en kontroll er slått av i oppsettet
- **THEN** oppgis det at den ble slått av, ikke at data mangler

#### Scenario: Årsaken står også i rapporten
- **WHEN** en kjøring hopper over en kontroll
- **THEN** oppgir rapporten den samme årsaken som konsollen

### Requirement: Årsaken skal si hva som skal til

Mangler en kontroll data, SKAL meldingen navngi både kommandolinjeflagget og
nøkkelen i oppsettet som kan skaffe dem.

Meldingene i dette verktøyet leses av en BIM-koordinator, ikke av en utvikler.
Forskjellen mellom «mangler systemtabell» og «oppgi --systemtabell, eller
«systemtabell» i oppsettet» er forskjellen mellom å lete i dokumentasjonen og å
rette én linje — samme grunn som at en ukjent nøkkel foreslår den nærmeste
gyldige.

#### Scenario: Meldingen navngir flagget og nøkkelen
- **WHEN** en kontroll hoppes over fordi en kodetabell mangler
- **THEN** nevner meldingen flagget som oppgir tabellen
- **AND** den nevner nøkkelen som gjør det samme i oppsettet
