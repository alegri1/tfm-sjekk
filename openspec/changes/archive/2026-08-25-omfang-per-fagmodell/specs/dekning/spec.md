## MODIFIED Requirements

### Requirement: Tomt omfang i en fagmodell gir et funn

Når ingen av objektene i en fagmodell er i omfanget, SKAL verktøyet melde det som
et funn med grad advarsel — **med mindre fagmodellen er unntatt med vilje** i
oppsettet.

Vurderingen SKAL gjøres per fagmodell. En federering der én fil er uten tekniske
fag er nettopp tilfellet som ellers går stille forbi, og det er den fila funnet
skal peke på.

Unntaket er nødvendig fordi funnet ellers mister sin verdi. Et prosjekt som med
vilje federerer inn ARK og RIB for kontrollene på tvers, ville fått en advarsel
per fil hver eneste kjøring — og en advarsel som alltid står der leses ikke.
Funnet skal fortsatt fyre når dekningen mangler ved en forglemmelse; det er
forskjellen mellom de to som nå kan uttrykkes.

#### Scenario: Ingen objekter i omfanget
- **WHEN** en fagmodell er lest, men ingen av objektene er i noen av de konfigurerte
  IFC-klassene
- **THEN** rapporten inneholder et funn med grad advarsel om at ingenting ble
  kontrollert i den fagmodellen

#### Scenario: Én tom fagmodell blant flere
- **WHEN** en kjøring omfatter tre fagmodeller, og bare én av dem har null objekter
  i omfanget
- **THEN** funnet gjelder den ene fagmodellen
- **AND** de to andre gir ikke funn om dekning

#### Scenario: Modell uten objekter i det hele tatt
- **WHEN** en fil ikke inneholder noen objekter verktøyet leser
- **THEN** rapporten sier fra om det på samme måte

#### Scenario: Fagmodellen er unntatt med vilje
- **WHEN** oppsettet gir en fagmodell et tomt sett IFC-klasser
- **THEN** rapporten melder ikke manglende dekning for den fagmodellen
