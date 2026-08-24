## ADDED Requirements

### Requirement: Et BCF-emne skal bære versjonen av verktøyet som lagde det

Hvert emne SKAL oppgi hvilken utgave av verktøyet som skrev det.

En rapport kan være eldre enn koden som lagde den, og det ser man ikke på den.
En BCF laget før en rettelse har GUID-er som stemmer og emner som åpner seg —
den gjør bare noe galt, og vieweren har ingen grunn til å si fra.

Det skjedde: en fil laget før kamerafeilen ble rettet lå ved siden av to ferske,
og den eneste måten å skille dem på var å regne ut avstanden fra kameraet til
objektet.

Versjonen hører hjemme der et menneske ser den, ikke i en fil bare et skript
leser. `bcf.version` er unntatt: `DetailedVersion` der er BCF-formatets versjon,
og å skrive verktøyets versjon i det feltet ville vært å svare på et annet
spørsmål enn det som stilles.

#### Scenario: Emnet oppgir versjonen
- **WHEN** funnene skrives som emner for en BCF-viewer
- **THEN** hvert emne oppgir versjonen av verktøyet
- **AND** versjonen er synlig i emnet, ikke bare i en fil ved siden av

#### Scenario: Formatets egen versjon er ikke verktøyets
- **WHEN** BCF-fila oppgir hvilken versjon av BCF-formatet den følger
- **THEN** det feltet er uendret av hvilken versjon verktøyet har

#### Scenario: Fila er fortsatt reproduserbar
- **WHEN** de samme funnene skrives to ganger med samme tidsstempel og samme
  utgave av verktøyet
- **THEN** filene er byte-identiske
