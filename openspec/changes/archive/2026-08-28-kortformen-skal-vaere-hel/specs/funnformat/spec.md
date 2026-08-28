## ADDED Requirements

### Requirement: En forkortet tittel skal slutte et sted den kan slutte

Må et emnes tittel kortes ned for å holde seg innenfor formatets grense, SKAL
den avsluttes ved en grense i teksten — en setning eller et ord — og ikke midt
inne i et ord.

Tittelen SKAL ikke avsluttes på et tegn som åpner noe: en parentes, et
anførselstegn eller en bindestrek som venter på det som kommer etter. Åpner
tittelen en parentes uten å lukke den, SKAL parentesen ikke stå igjen.

En sammenhengende streng uten mellomrom SKAL ikke regnes som et ord. Et objekts
TFM-ID er 26 tegn uten mellomrom, og en melding som ramser opp flere av dem har
ingen ordgrense å kutte ved.

Tittelen er det eneste en viewer viser i emnelista. Hele meldingen står i
beskrivelsen, så ingenting går tapt — men den som blar gjennom hundre emner
leser bare titlene, og «merket med system…» ser ut som en ødelagt fil framfor en
forkortet setning. En avslutning som lukker seg selv sier tydelig at det finnes
mer å lese; en som stopper midt i et ord sier at noe er galt.

#### Scenario: Meldingen har en setningsgrense innenfor grensen
- **WHEN** meldingen er for lang og første setning slutter innenfor grensen
- **THEN** er tittelen den første setningen, hel

#### Scenario: Første setning er selv for lang
- **WHEN** meldingen er for lang og det ikke finnes noen setningsgrense innenfor
  grensen
- **THEN** avsluttes tittelen ved siste hele ord som får plass
- **AND** det siste ordet i tittelen er ikke halvert

#### Scenario: Kuttet lander like etter en åpen parentes
- **WHEN** teksten fram til grensen slutter på en parentes eller et
  anførselstegn som ikke er lukket
- **THEN** tas det tegnet ikke med i tittelen

#### Scenario: Kuttet lander inne i en parentes
- **WHEN** tittelen åpner en parentes og grensen nås før den lukkes
- **THEN** er hele den åpne parentesen utelatt fra tittelen
- **AND** avsluttes tittelen ved siste hele ord foran den

#### Scenario: Teksten er én lang identifikator
- **WHEN** teksten fram til grensen ikke inneholder noen ordgrense verdt navnet
- **THEN** kuttes den likevel, og tittelen holder seg innenfor grensen
- **AND** er tittelen ikke redusert til de første tegnene alene

#### Scenario: Tittelen holder seg innenfor grensen
- **WHEN** en melding av hvilken som helst lengde blir til en tittel
- **THEN** er tittelen aldri lengre enn det formatet tillater

#### Scenario: Det er synlig at tittelen er forkortet
- **WHEN** en tittel er kortet ned fordi meldingen var for lang
- **THEN** viser tittelen selv at den fortsetter et annet sted
