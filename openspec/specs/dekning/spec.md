## Purpose

Beskriver hva verktøyet sier om hvor mye av en modell det faktisk undersøkte.
Uten dette er fravær av funn tvetydig: det kan bety at alt er i orden, eller at
ingen kontroll hadde noe å se på. De to skal ikke se like ut i en rapport som
brukes som port i en leveranseprosess.

## Requirements

### Requirement: Rapporten sier hvor mye som ble sjekket

Verktøyet SKAL oppgi hvor mange objekter som var i omfanget, av hvor mange objekter
som ble lest, per fagmodell. Tallet SKAL oppgis også når det ikke er funnet noe å
melde.

Et dekningstall som bare vises når noe er galt er verdiløst: det er nettopp den rene
rapporten en leser trenger å kunne stole på.

#### Scenario: Dekningen oppgis ved en ren kjøring
- **WHEN** en fagmodell er kontrollert uten funn
- **THEN** rapporten oppgir antall objekter i omfanget og antall objekter lest for
  den fagmodellen

#### Scenario: Dekningen oppgis per fagmodell ved federering
- **WHEN** flere fagmodeller kontrolleres i samme kjøring
- **THEN** dekningen oppgis for hver av dem, ikke bare samlet

### Requirement: Tomt omfang i en fagmodell gir et funn

Når ingen av objektene i en fagmodell er i omfanget, SKAL verktøyet melde det som
et funn med grad advarsel.

Vurderingen SKAL gjøres per fagmodell. En federering der én fil er uten tekniske
fag er nettopp tilfellet som ellers går stille forbi, og det er den fila funnet
skal peke på.

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

### Requirement: Tomt omfang endrer ikke exit-koden

Et funn om tomt omfang SKAL ha grad advarsel og SKAL ikke gjøre exit-koden ulik
null alene.

Verktøyet står allerede som port i CI hos den som bruker det, og et legitimt kjør
på en modell uten tekniske fag skal ikke begynne å feile. Advarsler teller ikke mot
exit-koden (§5), og det er derfor graden er den riktige.

#### Scenario: Ren modell med tomt omfang
- **WHEN** en kjøring gir null feil, men et funn om tomt omfang
- **THEN** exit-koden er 0

#### Scenario: Tomt omfang sammen med ekte feil
- **WHEN** en kjøring har både et funn om tomt omfang i én fagmodell og minst én
  feil i en annen
- **THEN** exit-koden er 1, slik feilen alene ville gitt

### Requirement: Funnet peker på årsaken

Funnet om tomt omfang SKAL nevne hvilken innstilling som avgjør omfanget, og hvilke
IFC-klasser fagmodellen faktisk inneholder.

Den som leser rapporten skal kunne rette konfigurasjonen ut fra meldingen alene.
Uten klassene fila inneholder er beskjeden «ingenting ble sjekket» uten anvisning.

#### Scenario: Meldingen navngir innstillingen og klassene
- **WHEN** en fagmodell med bare `IfcWall` og `IfcSlab` gir tomt omfang
- **THEN** meldingen nevner innstillingen som styrer omfanget
- **AND** den nevner klassene som faktisk finnes i fagmodellen

### Requirement: Antall leste objekter skiller seg fra antall i omfanget

Der verktøyet i dag oppgir «objekter kontrollert», SKAL det skilles mellom antall
objekter som ble lest fra fila og antall som var i omfanget for kontrollene.

Dagens tall er antall leste objekter, presentert som om det var antall
kontrollerte. Nettopp den forskjellen er det denne evnen finnes for.

#### Scenario: Tallene er ulike og begge oppgis
- **WHEN** en fagmodell har 412 leste objekter og 0 i omfanget
- **THEN** rapporten oppgir begge tallene
- **AND** den framstiller ikke 412 som antall kontrollerte objekter
