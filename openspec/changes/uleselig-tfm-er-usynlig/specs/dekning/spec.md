## ADDED Requirements

### Requirement: Objekter med uleselig TFM skal telles

Verktøyet SKAL oppgi hvor mange objekter i omfanget som har en TFM-verdi som
ikke lot seg tolke. Tallet SKAL oppgis per fagmodell, ved siden av dekningen.

Et objekt med uleselig TFM er lest, det er i omfanget, og det er likevel ikke
kontrollert av de kontrollene som krever en tolket ID. Uten tallet ser en slik
fagmodell like undersøkt ut som en der alt ble kontrollert.

Dette er samme tvetydighet som evnen ellers finnes for å fjerne, én etasje inn:
dekningen svarer på om objektet var i omfanget, ikke på om det var lesbart nok
til å bli kontrollert.

#### Scenario: Noen objekter har uleselig TFM
- **WHEN** en fagmodell har objekter i omfanget der TFM-verdien ikke lar seg
  tolke
- **THEN** oppgir rapporten hvor mange det gjelder for den fagmodellen

#### Scenario: Alt lot seg tolke
- **WHEN** alle objektene i omfanget har en TFM som lot seg tolke
- **THEN** oppgis det, slik at fravær av tallet ikke må tolkes

### Requirement: Meldingen om syntaksfeil skal si hva den koster

Meldingen om at en TFM-verdi ikke følger grammatikken SKAL si at objektet
dermed ikke er kontrollert av de øvrige kontrollene.

Meldingen sier i dag hva som er galt med strengen. Den sier ikke at objektet
samtidig er uunderøkt for ukjent systemkode, duplisert forekomst, master-avvik
og kursnummer. Den som leser rapporten skal kunne se at et syntaksfunn skjuler
mer enn det viser.

#### Scenario: Meldingen nevner konsekvensen
- **WHEN** et objekt får et funn om at TFM-verdien ikke følger grammatikken
- **THEN** sier meldingen også at objektet ikke er kontrollert av de øvrige
  kontrollene

### Requirement: En fagmodell der alt faller ut skal meldes særskilt

Er det ingen objekter i omfanget som har en tolkbar TFM, mens fagmodellen har
objekter med TFM-verdi, SKAL verktøyet melde det som et eget funn med grad
advarsel.

Enkeltfeil rettes objekt for objekt. Faller alt ut, er det ikke enkeltfeil —
det er en merkekonvensjon som ikke stemmer med grammatikken i oppsettet, og
handlingen er å se på oppsettet framfor på modellen. De to skal ikke se like ut.

Funnet SKAL nevne innstillingen som avgjør grammatikken, på samme måte som
funnet om tomt omfang navngir innstillingen som avgjør omfanget.

#### Scenario: Ingen TFM-verdi lot seg tolke
- **WHEN** en fagmodell har objekter med TFM-verdi i omfanget, og ingen av dem
  lot seg tolke
- **THEN** meldes det som et funn med grad advarsel
- **AND** meldingen nevner innstillingen som avgjør grammatikken

#### Scenario: Noen lot seg tolke
- **WHEN** minst ett objekt i fagmodellen har en tolkbar TFM
- **THEN** meldes det ikke som en konvensjonsfeil
- **AND** de enkelte syntaksfunnene meldes som før

#### Scenario: Ingen objekter har TFM i det hele tatt
- **WHEN** ingen objekter i fagmodellen har en TFM-verdi
- **THEN** meldes det ikke som en konvensjonsfeil
- **AND** fraværet meldes som før, av kontrollen for manglende TFM
