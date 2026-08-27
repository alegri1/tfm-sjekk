## ADDED Requirements

### Requirement: Samme objektidentitet i flere fagmodeller skal meldes

Har objekter i omfanget samme IFC-identitet i mer enn én fagmodell, SKAL
verktøyet melde det som et funn med grad advarsel.

Identiteten brukes til å feste et funn til en fil og til å bære parseresultatet.
Er den ikke entydig, peker funn på vilkårlige filer, og to objekter deler ett
parseresultat. Undersøkelsen er da gjort, men resultatet er ikke til å stole på —
og det er et annet tilfelle enn at noe ikke ble undersøkt.

Funnet SKAL navngi fagmodellene og hvor mange objekter det gjelder, og si at
fil-tilhørigheten i de øvrige funnene er upålitelig for dem.

#### Scenario: Samme modell er sendt inn to ganger
- **WHEN** to fagmodeller inneholder objekter i omfanget med samme identitet
- **THEN** meldes det som et funn med grad advarsel
- **AND** funnet navngir fagmodellene og antallet

#### Scenario: Hver identitet finnes bare ett sted
- **WHEN** ingen identitet i omfanget går igjen på tvers av fagmodeller
- **THEN** meldes det ikke

### Requirement: Delte objekter utenfor omfanget skal ikke meldes

Går en identitet igjen bare på objekter som ikke er i omfanget, SKAL det ikke
meldes.

Lenkede eksporter fra Revit legger delte objekter — rutenett, romlig struktur —
inn i hver fil. Det er normalt og uten følger: objektene kontrolleres ikke, og
ingen funn festes til dem. En advarsel her ville stått i hver eneste federerte
kjøring og sluttet å bli lest.

#### Scenario: Et delt rutenett i flere fagmodeller
- **WHEN** flere fagmodeller inneholder samme objekt utenfor omfanget
- **THEN** meldes det ikke

### Requirement: Verktøyet skal ikke velge mellom like identiteter

Verktøyet SKAL IKKE slå sammen, forkaste eller på annen måte velge mellom
objekter som deler identitet.

Hvilket av to like objekter som er det rette, kan bare den som sendte inn filene
svare på. Å velge ett ville gjort en tvetydighet til et svar, og resultatet ville
sett like rent ut som en riktig kjøring.

#### Scenario: Begge objektene blir stående
- **WHEN** to fagmodeller deler et objekt i omfanget
- **THEN** telles begge i dekningen for hver sin fagmodell
