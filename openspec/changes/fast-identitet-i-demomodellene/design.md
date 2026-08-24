## Context

Se proposal.md — Why.

`syntetisk.py` har seks funksjoner som skriver en fil, og én privat hjelper
(`_romlig_struktur`) som lager den romlige kjeden. Til sammen 25 kall til
`guid.new()`.

`rapport/bcf.py` har allerede mønsteret vi trenger: et fast navnerom og `uuid5`
over innholdet. Kommentaren der sier hvorfor navnerommet aldri må endres —
«ellers bytter alle emner identitet».

## Goals / Non-Goals

**Goals:**

- To kjøringer av generatoren skal gi byte-identiske filer.
- En BCF laget før en regenerering skal fortsatt peke på de samme objektene.

**Non-Goals:**

- Å gjøre `guid.new()` deterministisk generelt. Fiksturen er ikke det eneste
  som bruker den, og et globalt grep ville rammet mer enn det løser.
- Å legge `.ifc`-filene i repoet. De er avledet, og `*.ifc` er ignorert av
  juridiske grunner (§8). Determinisme er nettopp svaret på at de må lages
  lokalt.

## Decisions

### En teller per fil, ikke innholdet som nøkkel

Nøkkelen blir `«filnavn:løpenummer»`, ikke noe utledet av objektet. Grunnen er
at innholdet ikke er unikt: demomodellene har med vilje to objekter med samme
TFM-verdi — det er K6-duplikatet — så en innholdsnøkkel ville gitt to entiteter
samme identitet.

Prisen er at et objekt satt inn midt i lista forskyver identiteten til alle
etter det. Det er akseptabelt: da har dataene endret seg, og BCF-en skal lages
på nytt uansett. Garantien vi trenger er *samme inndata gir samme utdata*, ikke
at identiteten overlever en endring i modellen.

### Generatoren lages lokalt i hver funksjon

En lukking opprettet av `sti.name` øverst i hver `lag_*`-funksjon, sendt videre
til `_romlig_struktur`. Alternativet var en modulglobal teller som nullstilles
— færre signaturendringer, men delt muterbar tilstand i en fikstur som kjøres
fra tester i vilkårlig rekkefølge. Det ville virket helt til to tester kjørte
parallelt.

### Hele fila, ikke bare produktene

BCF-en peker bare på produkter, så strengt tatt holder det å gjøre dem stabile.
De øvrige gjøres likevel: en fil der halvparten av identitetene er faste ser
stabil ut, og den neste som sammenligner to kjøringer vil tro at forskjellen
betyr noe.

`ifcopenshell.template.create` trekker sin egen GUID til prosjektet, men tar
imot `project_globalid`. Uten den ville geometrimodellene fortsatt vært
ustabile på ett punkt.

## Risks / Trade-offs

**Alle eksisterende BCF-filer slutter å matche én siste gang** → Identitetene
endres når dette tas i bruk, så en BCF laget før må lages på nytt. Det er
engangs, og det er prisen for at det aldri skjer igjen.

**Navnerommet må aldri endres** → Samme forbehold som i `bcf.py`. Endres det,
bytter hver eneste entitet identitet på én gang. Det står som en kommentar der,
og skal stå som en kommentar her.

**Testene kan begynne å avhenge av bestemte GUID-er** → De bør ikke det, men nå
blir det mulig. En test som fester seg til en konkret GUID ville brukket ved
enhver endring i modellen, og det er en dårlig test uansett — verdt en linje i
fiksturen som sier fra.
