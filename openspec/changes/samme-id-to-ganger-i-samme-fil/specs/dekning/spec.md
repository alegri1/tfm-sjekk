## MODIFIED Requirements

### Requirement: Samme objektidentitet i flere fagmodeller skal meldes

Går samme IFC-identitet igjen blant objekter i omfanget, SKAL verktøyet melde
det som et funn med grad advarsel. Det gjelder både når identiteten går igjen i
flere fagmodeller og når den går igjen flere ganger i samme fil.

Identiteten brukes til å feste et funn til en fil og til å bære parseresultatet.
Er den ikke entydig, peker funn på vilkårlige filer, og to objekter deler ett
parseresultat. Undersøkelsen er da gjort, men resultatet er ikke til å stole på —
og det er et annet tilfelle enn at noe ikke ble undersøkt.

Innenfor én fil er følgen verre enn på tvers. To objekter med hver sin TFM-verdi
får ett felles parseresultat, og verktøyet melder da et duplikat som ikke finnes
i modellen — et funn som er usant, ikke bare upresist.

Funnet SKAL navngi fagmodellene og hvor mange objekter det gjelder, og si at
fil-tilhørigheten i de øvrige funnene er upålitelig for dem.

De to tilfellene SKAL skilles i meldingen. De krever ulik handling: samme modell
sendt inn to ganger fjernes fra kjøringen, mens en fil som bryter IFC-kravet om
unikhet må eksporteres på nytt.

#### Scenario: Samme modell er sendt inn to ganger
- **WHEN** to fagmodeller inneholder objekter i omfanget med samme identitet
- **THEN** meldes det som et funn med grad advarsel
- **AND** funnet navngir fagmodellene og antallet

#### Scenario: Samme identitet to ganger i én fil
- **WHEN** én fagmodell inneholder to objekter i omfanget med samme identitet
- **THEN** meldes det som et funn med grad advarsel
- **AND** navngir funnet fila og antallet
- **AND** sier meldingen at fila bryter IFC-kravet om unik identitet

#### Scenario: De to tilfellene ser ulike ut
- **WHEN** en kjøring har både en identitet delt mellom to filer og en identitet
  som går igjen i én fil
- **THEN** er de to funnene ulike, og hvert av dem sier hva som skal gjøres

#### Scenario: Hver identitet finnes bare ett sted
- **WHEN** ingen identitet i omfanget går igjen
- **THEN** meldes det ikke

## ADDED Requirements

### Requirement: Et duplikat som skyldes delt identitet skal ikke meldes som en merkefeil

Deler to objekter i omfanget identitet, SKAL verktøyet ikke melde en
komponentforekomst som brukt flere ganger når det bare er parseresultatet de
deler.

To objekter med hver sin TFM-verdi er ikke et duplikat. Meldes de som ett, får
den som skal rette modellen beskjed om å finne to like TFM-er som ikke finnes —
og den ene av de to verdiene blir aldri kontrollert.

#### Scenario: To ulike TFM-verdier på samme identitet
- **WHEN** to objekter i samme fil har samme identitet og hver sin TFM-verdi
- **THEN** meldes det ikke at en komponentforekomst er brukt på to objekter
- **AND** meldes den delte identiteten i stedet

### Requirement: Alle kommandoer som leser modeller skal si fra på samme måte

Kan ikke en modellfil leses, SKAL enhver kommando som leser modeller svare på
den samme måten: en melding, og koden som betyr at kjøringen ikke kunne
gjennomføres.

Kravet ble innført for kontrollkjøringen. En kommando som leser de samme filene
og svarer annerledes på den samme fila, er en kommando som lyver om verktøyet.

#### Scenario: Oppsettforslag på en ødelagt fil
- **WHEN** kommandoen som foreslår et oppsett får en fil som ikke lar seg lese
- **THEN** gir den en melding og den samme exit-koden som kontrollkjøringen
- **AND** vises ingen traceback
