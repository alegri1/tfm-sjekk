## Why

Fra §11-samtalen 2026-08-20 med en erfaren RIE/BIM-koordinator: **en tidlig modell
har ikke krav til plassering.** Byggnummeret `++115080` er ikke bestemt, eller ikke
ført inn ennå, mens systemet og komponenten er merket og skal kunne kontrolleres.

I dag avviser parseren hele TFM-ID-en når `++`-delen mangler. Konsekvensen er at
verktøyet er ubrukelig i tidligfase: hvert eneste objekt får et syntaksfunn om en
del prosjektet ennå ikke har bestemt, og de ekte feilene drukner.

Samme samtale slo fast hvem verktøyet er for. Store prosjekter bruker dRofus og
får korrekt TFM tilbake i Revit; små og mellomstore gjør det ikke, og der er
verktøyet «gullverdt». Det segmentet arbeider seg gjennom faser i Revit, ikke
gjennom en federert leveransekontroll — så nettopp tidligfasen er der verktøyet
skal virke.

§14 sier at regelsettet skal leveres som data fordi TFM-tolkningene varierer.
Dette er den varasjonen: ikke mellom prosjekter, men mellom faser i samme
prosjekt.

## What Changes

- Ny innstilling `grammatikk.krev_plassering` (standard `true`, altså dagens
  oppførsel). Settes den `false`, godtas en TFM-ID uten `++`-delen.
- `TfmId.plassering` blir valgfri. Alt som leser den må tåle at den mangler.
- **K6s unikhetsnøkkel bygges av delene som finnes.** En ID med plassering og en
  uten havner i hvert sitt nøkkelrom og kolliderer ikke med hverandre.
- Feilmeldingene skal fortsatt være riktige: mangler `++` mens den er påkrevd,
  navngis den delen som før. Er den valgfri, nevnes den ikke.

Ingen eksisterende oppsett endrer oppførsel: standardverdien er `true`.

## Capabilities

### New Capabilities
- `grammatikk`: Hvilke deler en TFM-ID må ha for å bli godtatt, hvilke som kan
  gjøres valgfrie, og hva som identifiserer én komponent når en valgfri del
  mangler. Dekker både formkravet og den identiteten K6 måler unikhet på, fordi
  de to er samme spørsmål sett fra hver sin side.

### Modified Capabilities

Ingen. `verdiuttrekk` krever allerede at «Forventningene SKAL komme fra den
konfigurerte grammatikken, slik at de ikke kan komme i utakt med regelen som
faktisk avviser verdien». Blir plassering valgfri, følger meldingene av det
kravet uten at kravet endres — men at det faktisk stemmer, skal prøves.

## Impact

- **`config.py`:** `Grammatikk.krev_plassering`, ved siden av `krev_komponenttype`
  som allerede gjør det samme for `%`-delen.
- **`parser.py`:** `bygg_monster` pakker `++`-delen i `(?:...)?` når den er
  valgfri — samme grep som allerede brukes for komponenttypen. `_forklar` må
  slutte å navngi en del som ikke kreves.
- **`modell.py`:** `TfmId.plassering: str | None`, og `global_forekomst` bygges
  av delene som finnes.
- **`kontroller/k6_unikhet.py`:** leser `global_forekomst` og trenger ingen
  endring, men oppførselen endres og må prøves.
- **Uendret:** `tfm_sjekk.ifc`, uttrekket, rapportene, de øvrige kontrollene.
  `ligner_tfm_id` krever to av tre markører — uten `++` gjenstår `=` og `-`, så
  gjenkjenningen holder. Det skal prøves, ikke antas.
- **Prøving:** en demomodell i tidligfase, kjørt med og uten `krev_plassering`,
  slik at forskjellen er noe man kan se og ikke bare lese om.
