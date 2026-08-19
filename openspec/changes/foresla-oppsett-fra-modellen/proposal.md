## Why

Verktøyet vet allerede hvor det fant TFM-verdiene, og hvor sikkert det var: hver
verdi bærer en `Verdikilde` med `KONFIGURERT`, `GJENKJENT_FELT` eller `GJETTET`.
Den opplysningen står i rapporten som en forklaring på ett funn, og forsvinner så.
Brukeren kan lese seg til at verdien lå i et annet egenskapssett enn forventet,
men må selv oversette det til et `tfm-sjekk.toml` — objekt for objekt, i en
rapport som kan ha hundrevis av funn.

Det samme gjelder omfanget, og der er det verre. Sier D1 «0 av 412 objekter i
omfanget», har verktøyet oppdaget nøyaktig det som er galt og lar brukeren stå
der. Klassene finnes i meldingen, men hvilken av dem som er den riktige å legge
til er overlatt til gjetning — selv om verktøyet allerede har lest TFM-verdier
på dem og dermed vet svaret.

Første møte med et nytt prosjekt er nettopp der dette koster mest: du har en
fagmodell, ingen `tfm-sjekk.toml`, og en rapport som enten er tom eller full av
funn du ikke vet om er ekte.

## What Changes

- Ny underkommando `tfm-sjekk oppsett <filer>` som leser modellene, aggregerer
  verdikildene, og skriver et forslag til `tfm-sjekk.toml`. Den kjører ingen
  kontroller og trenger verken master eller kodetabeller.
- Forslaget inneholder **bare det som avviker fra standardverdiene**. Alt annet
  utelates, slik at prosjektets fil viser hva som er særegent ved prosjektet, og
  slik at en senere retting i standardverdiene fortsatt når fram.
- Hvert forslag skrives med **beviset i en kommentar over seg**: hvor mange
  objekter verdien ble funnet på, og med hvilken sikkerhet. Et forslag uten
  belegg er en gjetning i ny innpakning, og skal kunne overprøves uten å kjøre
  verktøyet på nytt.
- Forslaget omfatter også `ifc_klasser`, men bare klasser som ligger utenfor
  omfanget **og har TFM-verdier**. At en klasse finnes i fila er ikke bevis for
  at den hører hjemme i omfanget; at objektene er merket, er det.
- Skriver til stdout som standard. Med `--ut <fil>` skrives fila, men en
  eksisterende fil overskrives ikke uten `--overskriv`.

## Capabilities

### New Capabilities
- `oppsettforslag`: Hvordan verktøyet utleder et konfigurasjonsforslag fra det
  det faktisk fant i modellene — hvilke funn som kvalifiserer til å bli
  konfigurasjon, hvilket belegg som kreves, hva som holdes utenfor, og hvordan
  forslaget gjør rede for seg selv.

### Modified Capabilities

Ingen. Uttrekket i `verdiuttrekk` og dekningsberegningen i `dekning` er
uendret — denne endringen leser det de allerede produserer. `les_modell` leser
i dag TFM-verdier for alle produkter, ikke bare de i omfanget, så også
klasseforslaget hviler på data som allerede finnes.

## Impact

- **Ny kode:** en modul som utleder forslaget fra `Kontekst`, og en som skriver
  TOML. Ingen ny avhengighet: `tomllib` leser, og utskriften er få nok
  konstruksjoner til å formes direkte — en skriver gir dessuten kontroll over
  kommentarene, som er halve poenget og som ingen TOML-writer bevarer.
- **`cli.py`:** ny underkommando. `_med_standardkommando()` må fortsatt sende en
  filsti uten kommandoord til `sjekk`, ikke til `oppsett`.
- **Uendret:** `tfm_sjekk.ifc`, parseren, kontrollene og rapportene. Grensen mot
  ifcopenshell røres ikke.
- **Prøving:** forslaget skal kjøres mot demomodellene, og resultatet skal kunne
  legges rett inn som `--config` i en påfølgende `sjekk` uten at noe brekker. Det
  er den egentlige prøven — at fila verktøyet skriver, er en fil verktøyet leser.
