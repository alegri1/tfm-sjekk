## Context

Se proposal.md — Why.

`bcf.py` har `FORFATTER = "tfm-sjekk"`, som brukes to steder: `CreationAuthor`
på emnet og `Author` på kommentaren. Verdien er en parameter på `skriv_bcf`,
men den er ikke eksponert i CLI-en — ingen bruker oppgir sitt eget navn i dag.

## Goals / Non-Goals

**Goals:**

- En BCF laget av en eldre utgave skal la seg kjenne igjen uten å regne på
  innholdet.
- Versjonen skal være synlig der noen ser den.

**Non-Goals:**

- Å advare om at fila er gammel. Verktøyet vet ikke hvilken utgave som er den
  nyeste, og en påstand om det ville vært gjetning. Å oppgi hva som lagde fila
  er et faktum; å vurdere om det er gammelt nok, er leserens sak.
- Å røre de tre andre rapportformatene. HTML har allerede en bunntekst, og CSV
  og XLSX leses av skript som ikke spør etter dette. Kommer behovet, er det en
  egen sak.

## Decisions

### `CreationAuthor`, ikke `DetailedVersion`

`bcf.version` har et felt som heter `DetailedVersion`, og det er fristende.
Det er feil: feltet beskriver hvilken utgave av BCF-*formatet* fila følger, og
en viewer kan bruke det til å bestemme hvordan den skal leses. Å skrive
`tfm-sjekk 0.6.1` der ville vært å svare på et annet spørsmål.

`CreationAuthor` er per emne og vises i emnelista. Det er også semantisk riktig:
det er verktøyet som har forfattet emnet, ikke et menneske. Andre verktøy gjør
det samme — «Solibri Model Checker v9.10» er en vanlig verdi i feltet.

### Versjonen leses av pakken, ikke skrives i koden

`importlib.metadata.version` gir den samme verdien som `pyproject.toml`. En
streng skrevet i `bcf.py` ville drevet fra den ved første bump, og det er
nøyaktig den slags drift denne endringen finnes for å fange.

Klarer oppslaget ikke å finne pakken — det skjer om modulen kjøres fra en
kildemappe uten installasjon — faller den tilbake på navnet uten versjon.
Et emne uten versjon er dårligere enn ett med, men bedre enn en kjøring som
stopper fordi metadata mangler.

## Risks / Trade-offs

**BCF-en endrer seg ved hver versjonsbump** → Det er hensikten. Kravet om
reproduserbarhet gjelder innenfor én utgave, og det er den garantien som betyr
noe: samme funn og samme tidsstempel gir samme fil.

**Feltet kan bli lest som et menneske** → `CreationAuthor` heter «author», og en
BIM-koordinator kan lure på hvem «tfm-sjekk 0.6.1» er. Det er akseptabelt:
alternativet er at ingen kan se hva som lagde fila, og navnet står allerede der
uten versjon i dag.
