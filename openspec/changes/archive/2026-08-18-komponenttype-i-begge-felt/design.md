## Context

Se `proposal.md` for hvorfor. Kravene står i `specs/komponenttype/spec.md`.

Tre ting former løsningen:

- `TfmId.komponenttype` er en avledet egenskap på den parsede ID-en, og finnes bare
  når `%`-delen er med. `IfcObjekt.tfm_type` er en rå streng fra et egenskapssett.
  De to er ulike typer med samme betydning.
- K7 leser `tfm.komponenttype` direkte og hopper over objektet når den er `None`.
- `normaliser` i `tabeller/master.py` gjør allerede en verdi sammenlignbar med en
  parset TFM-ID: trimmer, fjerner prefikser, store bokstaver. Mastera og modellen
  sammenlignes gjennom den i dag.

## Goals / Non-Goals

**Goals:**
- Én kilde til et objekts komponenttype, som kontrollene kan spørre om.
- Et sprik mellom de to feltene blir synlig.

**Non-Goals:**
- Ingen endring i hva K7 gjør med en komponenttype den har fått. Det er kilden som
  utvides, ikke sjekken.
- Ingen ny konfigurasjon. Hvilket egenskapssett typen leses fra er allerede data.

## Decisions

### Oppslaget hører i Kontekst, ikke på IfcObjekt

`IfcObjekt` er ren uttrekksdata og vet ikke om parsing; `TfmId` kjenner ikke
egenskapssettene. Regelen om forrang trenger begge, og `Kontekst` er stedet som
allerede holder dem sammen — den har `parsede` ved siden av `objekter`.

Alternativet, å legge komponenttypen på `IfcObjekt` i loaderen, ble forkastet: da
måtte loaderen parse TFM-ID-en for å finne `%`-delen, og parsing er noe `Kontekst`
gjør én gang for alle. To parsesteder er én for mange.

### Sammenligningen går gjennom samme normalisering som mastera

`%`-delen kommer fra en parset ID og er allerede normalisert av grammatikken;
typefeltet er rå tekst fra et regneark-aktig felt, med samme slurv som mastera har
— mellomrom, små bokstaver, kanskje et `%` foran. `normaliser` håndterer nettopp
det, og er allerede den funksjonen modellen og mastera møtes i.

Å skrive en egen sammenligning her ville gitt to definisjoner av «samme
komponenttype», og de ville før eller siden vært uenige.

### T1 står utenfor K-serien

Samme resonnement som for D1: §4 definerer K1–K9, og `specification/` er fasit for
§-numrene og vokser ikke per endring. Et «K10» ville vært et nummer uten paragraf
bak seg. T-en står for type.

At kontrollen ikke er i §4 betyr ikke at den er mindre viktig — bare at
spesifikasjonen ble skrevet før noen så at den samme opplysningen står to steder.

### Spriket undertrykker K7-funnet, ikke omvendt

Når de to feltene er uenige, har objektet ingen avklart komponenttype. K7 kan da
ikke si noe meningsfullt om mastera, og et funn derfra ville hvilt på et vilkårlig
valg mellom to verdier. T1 melder spriket; K7 tier om det objektet.

Vurdert og forkastet: å la K7 bruke `%`-delen ved sprik, siden den har forrang
ellers. Men forrangsregelen finnes for å velge når det ikke er noen konflikt —
å bruke den til å overkjøre en konflikt ville gjort en uavklart situasjon til en
tilsynelatende avklart.

## Risks / Trade-offs

**Nye feil i modeller som passerer i dag** → Objekter med begge feltene og ulikt
innhold gir nå exit 1. Det er tilsiktet: spriket er en ekte merkefeil. Men det er
den slags endring som kan overraske noen som har verktøyet i CI, og graden er verdt
en innvending før implementasjon.

**K7 får flere objekter å melde om** → En modell uten `%`-deler har til nå hatt K7
stille om komponenttyper. Nå meldes de som ikke står i mastera. Igjen tilsiktet, men
det kan gi et hopp i antall funn ved første kjøring etter oppgraderingen.

**Demoen viser ingenting av dette i dag** → Ett av femten objekter har `%`-del, og
ingen har `TFM11_Type`. Fikstursettene må utvides, ellers demonstrerer endringen seg
selv bare i testene. Det er samme drift som mastera og kodetabellen hadde.
