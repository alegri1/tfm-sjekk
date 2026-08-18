## Context

Se `proposal.md` for hvorfor. Kravene står i `specs/verdiuttrekk/spec.md`.

Det som former løsningen er tre ting i dagens kode:

- Verdiuttrekket har tre strategier på rad, og den siste — «riktig pset, ta første
  ikke-tomme verdi» — har ingen nøkkel. Utfallet avgjøres av rekkefølgen
  egenskapene tilfeldigvis har i IFC-fila.
- Parseren bygger regexen sin fra `Grammatikk`, altså fra data. Skilletegnene
  `++`, `=`, `-` og `%` er derimot faste i mønsteret, og de samme tre er allerede
  hardkodet som en stige i feilforklaringen.
- Ekstraksjonsgrensa: alt som skal ut til kontrollene må være picklebar
  pydantic-data, fordi federering leser hver fil i egen prosess.

## Goals / Non-Goals

**Goals:**
- Én definisjon av «ligner dette på en TFM-ID», brukt både som port for en gjettet
  verdi og som valg av meldingens presisjon.
- Verdiuttrekket kan gjøre rede for hvor hver verdi kom fra, uten at kontrollene
  må vite noe om IFC.

**Non-Goals:**
- Ingen ny meldingstekst for verdier der alle markørene finnes. Se «Utenfor
  omfanget» i proposal.
- Ingen endring i hvilke kontroller som finnes eller hva de sjekker. K9s heuristikk
  er riktig; det er inndataene den har fått som har vært gale.

## Decisions

### Formtesten: høyst én strukturmarkør kan mangle

Målt mot fjorten strenger — fabrikatnavn, modellbetegnelser, kommentarer, og
TFM-ID-er ødelagt på fem ulike måter — forkaster **alle** kandidatgrensene alt
søppelet. De skiller seg bare på ødelagte, men ekte TFM-verdier.

| Kandidat | Forkaster søppel | Ødelagt TFM |
|---|---|---|
| full parsing | ja | forkaster alt — gjør K2 blind |
| løs regex (samme form, løsnet sifferantall) | ja | forkaster små bokstaver og manglende `++` |
| «starter med `++`» | ja | forkaster TFM uten `++` |
| **høyst én av `++`, `=`, `-` mangler** | **ja** | **godtar alle fem** |

Valget er ikke «hvor tolerante skal vi være», men «når kan verktøyet si noe
spesifikt som også er sant». Med to av tre markører til stede kan parseren
navngi den delen som mangler, og anvisningen er da verdt å følge. Med færre er
den ærlige meldingen at strengen ikke ser ut som en TFM-ID.

Markørene hentes fra samme sted som parseren bruker dem, slik at de ikke kan
komme i utakt.

### Samme dom brukes to steder

Formtesten er porten for gjetningsveien **og** velger meldingens presisjon på alle
veier. Én funksjon, to kall. Alternativet — en egen terskel for hver — ville latt
dem konkludere ulikt om samme streng, og det er nettopp den slags avvik ingen
oppdager før en bruker gjør det.

### Formtesten er ikke konfigurerbar

§14 sier at regelsettet leveres som data, men det gjelder kunnskap prosjektet har
og verktøyet ikke: sifferantall, pset-navn, klasser per fag, MMI-skala. Denne
terskelen er noe annet — en indre grense for når verktøyet tør å uttale seg. Ingen
BIM-koordinator kan sette den fornuftig, og to prosjekter som satte den ulikt ville
ikke fått ulik TFM-tolkning, bare ulik kvalitet på feilmeldingene.

### Proveniens som data på objektet

Hvor verdien kom fra følger objektet som picklebare felter: hvilken strategi som
traff, og hvilket egenskapssett og felt verdien faktisk ble lest fra. Kontrollene
leser det som strenger og trenger ikke vite hva et pset er.

Alternativet — å regne det ut på nytt i rapporten — er umulig: bare loaderen har
sett IFC-fila.

### MMI: nivåangivelse, ikke «tekst med siffer i»

Dagens normalisering trekker ut alle sifre fra hva som helst, og gjør «sjekket av
RIE 12.03» til nivå «1203». Ny regel: verdien må *være* en nivåangivelse — et tall,
eventuelt med `MMI` foran og mellomrom rundt.

Vurdert og forkastet: å kreve at verdien står i `gyldige_verdier`. Det ville
blandet sammen «er dette et MMI-nivå» med «er det et lovlig nivå», og K9 må fortsatt
kunne flagge 275 som utenfor skalaen.

### `tfm_type` beholdes, kandidatlista rettes

Feltet leses uten at noen bruker det, men §3 navngir `TFM11_Type` eksplisitt som et
av de vanlige egenskapssettene i norske Revit-maler, og K7 har en nærliggende
framtidig bruk: å sammenligne typen mot komponentlista i mastera.

Det som må vekk er `Type` i kandidatlista. Et navn som brukes til søk på tvers av
alle egenskapssett må være distinkt, og `Type` finnes i
`Pset_ManufacturerTypeInformation` i praktisk talt enhver modell.

## Risks / Trade-offs

**En ekte, men sterkt ødelagt TFM-verdi kan bli demotert fra K2 til K1** → Objektet
flagges fortsatt; meldingen blir mindre spesifikk, ikke borte. Asymmetrien er
akseptabel: en upresis melding om et objekt som faktisk har et problem koster
mindre enn en presis melding om et problem som ikke finnes.

**Grensen er valgt mot oppdiktede strenger** → Fjorten strenger jeg fant på, ikke
funn fra en ekte modell. De dekker de formene jeg klarte å forestille meg, og det
er en annen liste enn den virkeligheten fører. Må prøves mot en ekte fagmodell før
den regnes som satt.

**BREAKING: `Type` fjernes fra standardlista** → Prosjekter som lener seg på
standardverdien får endret oppførsel. Men dagens oppførsel leser fabrikatnavn inn i
et felt ingen bruker, så endringen retter noe som var galt. Prosjekter som trenger
`Type` kan sette det selv i `tfm-sjekk.toml`.

**Proveniens gjør meldingene lengre** → BCF-tittelen kuttes på 100 tegn.
Opphavet hører hjemme i beskrivelsen og kommentaren, ikke i tittelen.

## Migration Plan

Ingen datamigrering. Endringen i standardverdien for `egenskapsnavn_type`
dokumenteres i README, og `tfm-sjekk.toml` i repoet oppdateres slik at eksempelet
viser den nye lista.

Rulles tilbake ved å reversere endringen; ingen tilstand er skrevet noe sted.

## Open Questions

- Hvilke nesten-treff forekommer faktisk i norske fagmodeller? Er TFM-ID uten `++`
  vanlig fordi noen strippet prefikset i eksport, eller er det en form jeg fant på?
  Svaret kan justere markørsettet senere, men endrer ikke tilnærmingen: én
  formtest, brukt to steder.
