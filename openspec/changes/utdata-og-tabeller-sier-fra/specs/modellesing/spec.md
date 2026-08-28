## ADDED Requirements

### Requirement: En kodetabell eller master som ikke lar seg lese skal gi en melding

Kan ikke en oppgitt kodetabell eller TFM-master leses, SKAL verktøyet avslutte
med en melding som navngir fila og sier hva som er galt, og med den samme
exit-koden som når en modellfil ikke lar seg lese.

Meldingen SKAL være verktøyets egen, som for modellfiler. Det gjelder også der
en melding allerede finnes inne i koden: en `ValueError` som sier nøyaktig
hvilken kolonne som mangler er ikke en melding så lenge den når brukeren som en
traceback.

#### Scenario: Kodetabellen er tom
- **WHEN** en oppgitt kodetabell er tom
- **THEN** avslutter verktøyet med en melding som navngir fila
- **AND** vises ingen traceback

#### Scenario: Kodetabellen mangler en kolonne den trenger
- **WHEN** en oppgitt kodetabell mangler kolonnen med kodene
- **THEN** sier meldingen hvilken kolonne som mangler

#### Scenario: Mastera er ikke det formatet endelsen lover
- **WHEN** en fil med endelsen .xlsx ikke er et regneark
- **THEN** sier meldingen at fila ikke lot seg lese som regneark
- **AND** navngir den fila

### Requirement: Tabellene skal leses før modellene

Verktøyet SKAL lese kodetabellene og TFM-mastera før det leser modellene.

En federert runde bruker førtisju sekunder på 24 456 objekter. En skrivefeil i
en tabellsti skal ikke koste den tiden før den oppdages — samme grunn som at
tidsstempelet valideres først i dag.

#### Scenario: En ubrukelig tabell oppdages med en gang
- **WHEN** en kjøring får oppgitt en kodetabell som ikke lar seg lese
- **THEN** stopper den før modellene leses
