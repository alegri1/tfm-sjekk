## ADDED Requirements

### Requirement: En oppsettfil som ikke lar seg lese skal gi en melding

Kan ikke oppsettfila tolkes som TOML, SKAL verktøyet stoppe med en melding som
navngir fila og sier hva som er galt. Verktøyet SKAL IKKE avslutte med en
tilbakesporing fra Python.

En byterekkefølgemarkør (BOM) SKAL ikke være en lesefeil. Notisblokk og
PowerShell skriver den, og fila ser da helt riktig ut i editoren.

Oppsettet er den ene fila brukeren redigerer selv, og med en fast rute i den
redigeres den i hvert prosjekt. En tilbakesporing sier ingenting om hvilken fil
det gjaldt eller hva som måtte rettes, og den ser ut som en feil i verktøyet
framfor en feil i fila.

#### Scenario: Oppsettet er skrevet med BOM
- **WHEN** oppsettfila begynner med en byterekkefølgemarkør og ellers er gyldig
  TOML
- **THEN** fila leses som om markøren ikke var der

#### Scenario: Oppsettet er ikke gyldig TOML
- **WHEN** oppsettfila ikke lar seg tolke som TOML
- **THEN** kjøringen stopper med en melding som navngir fila og oppgir hva
  tolkningen stoppet på
- **AND** ingen rapport skrives
