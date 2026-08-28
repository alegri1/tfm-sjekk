## ADDED Requirements

### Requirement: Oppsummeringen skal telle alle gradene den fant

Oppsummeringen av en kjøring SKAL oppgi antallet for hver alvorlighetsgrad som
forekommer blant funnene. En grad uten funn SKAL ikke nevnes.

Antallene SKAL stemme med rapportene: summen av gradene i oppsummeringen er
antallet funn i rapportfilene.

Oppsummeringen er det første og ofte det eneste den som kjørte verktøyet leser.
Nevner den bare to av tre grader, har leseren ingen måte å vite at det ligger
flere rader i rapporten — og et funn ingen vet om er like usynlig som et funn
som aldri ble meldt.

Gradene som ikke avgjør exit-koden er ikke mindre verdt å vite om. En advarsel
og et infofunn endrer ikke porten, men de er nettopp de funnene som ellers går
ubemerket forbi.

#### Scenario: Kjøringen har funn av alle tre grader
- **WHEN** en kjøring gir 13 feil, 1 advarsel og 3 infofunn
- **THEN** oppgir oppsummeringen alle tre tallene
- **AND** summen av dem er antallet funn i rapporten

#### Scenario: En grad har ingen funn
- **WHEN** en kjøring gir feil, men ingen infofunn
- **THEN** nevner oppsummeringen ikke infofunn

#### Scenario: Entall og flertall
- **WHEN** en grad har nøyaktig ett funn
- **THEN** står ordet for den graden i entall

### Requirement: Oppsummeringen skal navngi hver fil kjøringen skrev

Oppsummeringen SKAL navngi hver rapportfil kjøringen skrev, ikke et utvalg av
dem.

Stiene SKAL skrives med plattformens eget skilletegn hele veien.

En bruker som ikke vet at et format finnes, leter ikke etter det. Navngir linja
to av fire filer, er de to andre skrevet til ingen — og et regneark som ligger
usett ved siden av rapporten er samme slags stille tap som et utelatt funn.

#### Scenario: Alle skrevne filer navngis
- **WHEN** en kjøring skriver en HTML-rapport, en CSV, et regneark og en BCF
- **THEN** navngir oppsummeringen alle fire

#### Scenario: Stien er skrevet i plattformens form
- **WHEN** en sti oppgis i oppsummeringen
- **THEN** bruker hele stien det samme skilletegnet
