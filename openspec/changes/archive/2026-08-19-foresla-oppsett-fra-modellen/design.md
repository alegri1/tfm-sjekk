## Context

Se `proposal.md` for hvorfor. Det som former løsningen er hvor dataene allerede
ligger.

`les_modell` leser TFM-forekomst, TFM-type og MMI for **alle** `IfcProduct`, ikke
bare for dem som er i omfanget, og legger en `Verdikilde` på hvert objekt for hver
verdi den fant. `Kontekst` holder alle objektene fra alle fagmodellene, og
`relevante_objekter()` er et filter over dem — ikke et utvalg gjort ved innlesing.

Alt denne endringen trenger finnes altså i `Kontekst` i dag. Ingen endring i
`tfm_sjekk.ifc`, i uttrekket eller i datamodellen. Det er verdt å si eksplisitt,
fordi det avgjør formen: dette er en avlesning, ikke en ny innsamling.

## Goals / Non-Goals

**Mål:**
- Utledningen er en ren funksjon `Kontekst -> Oppsettforslag`, testbar uten en
  eneste IFC-fil, på samme form som en kontroll.
- Forslaget er en delta mot konfigurasjonen som var i bruk under kjøringen, ikke
  mot standardverdiene som sådan. Det gjør `--config` meningsfull og gjør
  «kjør på nytt med eget forslag → tomt» til en prøve som faktisk sier noe.
- Fila som skrives er lesbar for et menneske først, for verktøyet nest.

**Ikke mål:**
- Å foreslå grammatikk, MMI-skala, alvorlighetsgrader, masterkolonner eller
  elektroklasser. Verdikildene sier ingenting om noen av dem, og et forslag uten
  belegg er nettopp det denne endringen finnes for å unngå.
- Å redigere en eksisterende `tfm-sjekk.toml` i stedet for å skrive en ny. En
  fletting måtte bevare brukerens kommentarer og rekkefølge, og det er en helt
  annen oppgave.
- Å avgjøre noe på brukerens vegne. Forslaget er et utkast som skal leses.

## Decisions

### Utledningen er en ren funksjon over `Kontekst`

Ny modul `tfm_sjekk/oppsett/`, med `utled(kontekst) -> Oppsettforslag` og en
skriver `til_toml(forslag) -> str`. `Oppsettforslag` er en pydantic-modell:
foreslåtte egenskapssett, feltnavn og klasser, hver med antall og kilde.

Dette følger formen kontrollene allerede har, og gir samme gevinst: hele
utledningen kan testes med en `Kontekst` bygget i minnet, og skriveren kan testes
mot et forslag uten å lese en modell.

*Vurdert og forkastet:* å utlede underveis i `les_modell`. Det ville flytte
domenekunnskap inn bak ifcopenshell-grensa og gjøre utledningen uprøvbar uten
IFC-filer, i bytte mot ingenting — dataene finnes uansett på utsiden.

### Delta måles mot konfigurasjonen som var i bruk

`utled` sammenligner det observerte med `kontekst.config`, ikke med
`Konfigurasjon()`. Kjøres kommandoen uten `--config`, er de to det samme; kjøres
den med, er forslaget det som mangler i *den* fila.

Dette er også det som gjør stabilitetskravet meningsfullt: et forslag brukt som
konfigurasjon skal gi et tomt forslag neste gang. Uten denne beslutningen ville
kjøring nummer to foreslå det samme om igjen.

### Klassifiseringen faller ut av `Kilde`, uten ny logikk

| Kilde | Hva observasjonen betyr | Forslag |
|---|---|---|
| `KONFIGURERT` | verdien lå der oppsettet sa | ingen |
| `GJENKJENT_FELT` | feltnavnet var konfigurert, egenskapssettet ikke | legg til egenskapssettet |
| `GJETTET` | egenskapssettet var konfigurert, feltnavnet ikke | legg til feltnavnet |
| `FORKASTET` | verdien hørte ikke hjemme der | ingen |

Kravet om at en forkastet verdi aldri blir konfigurasjon, trenger dermed ingen
egen kode — den følger av at bare de to midterste radene produserer noe. Det er
verdt å teste likevel, siden det er en regel og ikke en tilfeldighet.

### `ifc_klasser` foreslås av merkede objekter utenfor omfanget

Kandidatene er objekter der `tfm_forekomst` er satt, men som ingen konfigurert
klasse treffer via `er_av_type`. Den konkrete klassen (`ifc_klasse`) foreslås, ikke
en supertype: verktøyet vet at `IfcBuildingElementProxy` er merket, ikke at hele
`IfcBuildingElement` skal inn i omfanget.

Foreslåtte klasser skrives som hele lista — konfigurerte først, foreslåtte etter —
fordi `ifc_klasser` erstattes i sin helhet når den settes i TOML, i motsetning til
hvordan et menneske leser en «legg til»-oppføring.

### TOML skrives for hånd, uten ny avhengighet

Kommentarene bærer beviset, og det er halve poenget med endringen. Ingen
TOML-skriver for Python bevarer kommentarer knyttet til bestemte oppføringer uten
at dokumentet bygges som et tre først. Det som skal skrives er dessuten lite: noen
få tabeller med lister av strenger.

Skriveren siterer strenger med `"` og escaper `\` og `"`. Ingen av de aktuelle
verdiene — pset-navn, feltnavn, IFC-klassenavn — kan i praksis inneholde noe annet,
men en skriver som ikke escaper i det hele tatt er en skriver som produserer ugyldig
TOML den dagen den møter noe uventet.

*Vurdert og forkastet:* `tomli-w`. Den skriver gyldig TOML og ingen kommentarer.
Et forslag uten belegg er en gjetning i ny innpakning.

### Tomhet skilles i to

`Oppsettforslag` skiller «ingenting å foreslå» fra «ingenting å bygge på» ved å
bære antall leste objekter og antall objekter med TFM-verdi. Kommandoen sier hvilket
av de to tilfellene den står i.

Dette er samme lærdom som `dekning` allerede bærer: to tall, ikke ett, fordi ett
tall ikke kan skille «alt i orden» fra «ingenting sjekket».

### Kommandoen kjøres uten master og kodetabeller

`oppsett` bygger `Kontekst` med modellene og konfigurasjonen, og stopper der. Ingen
kontroller kjøres, så ingen tabeller trengs. Det er nettopp førstegangsbruken: du
har en fagmodell og ingenting annet.

## Risks / Trade-offs

**En gjetning basert på få objekter blir til varig konfigurasjon** → Beviset står i
fila, med antall og kilde, over hver oppføring. Ingen nedre grense settes: en
terskel ville forkastet observasjoner i stillhet, og et forslag brukeren aldri fikk
se er verre enn ett hen kan stryke. `--ut` nekter dessuten å overskrive, så en fil
blir aldri byttet ut uten at noen ba om det.

**En modell som er feilmerket forplanter feilen** → Ligger TFM-verdier på klasser
som ikke skal merkes, foreslås de klassene. Verktøyet kan ikke skille «feil
eksport» fra «riktig eksport i uvant klasse» — det er nettopp derfor forslaget er
et forslag, og derfor antallet står ved siden av.

**Kommandonavnet kolliderer med filstier** → `_med_standardkommando()` setter inn
`sjekk` når første argument ikke er et kjent kommandoord, slik at dra-og-slipp
virker. Lista over kjente kommandoord må utvides med `oppsett`, ellers havner en
fil som heter `oppsett.ifc` feil sted. Dekkes av en test.

**Forslaget er gyldig TOML, men gal konfigurasjon** → Den eneste virkelige prøven
er å bruke fila. Derfor kjøres forslaget tilbake gjennom `Konfigurasjon.les` i test,
og gjennom en faktisk `sjekk`-kjøring i den manuelle prøvingen.

## Migration Plan

Ingen. Ny underkommando, ingen endring i eksisterende oppførsel, ingen
filformater som må konverteres. Et prosjekt uten `tfm-sjekk.toml` virker som før.

## Open Questions

Ingen som kan utsettes uten å endre spesifikasjonen eller oppgavene.
