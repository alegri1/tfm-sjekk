## Why

Verktøyet kan ikke skille en verdi det har **lest** fra en det har **gjettet**, og
gjetningene ender som presise, handlingsrettede og usanne funn i rapporten.

Tre målte tilfeller, alle fra modeller som er helt vanlige:

| Modellen inneholder | Verktøyet leser | Rapporten sier |
|---|---|---|
| pset `TFM11_Forekomst` med `Fabrikat`, `Modell`, `Vekt` | `"Systemair"` | K2: «Mangler ++-delen: plassering (6 siffer)» |
| samme pset, men feltet heter `TFM-ID` og står sist | `"Systemair"` | samme — står `TFM-ID` først, leses det riktig |
| pset `MMI` med bare et kommentarfelt | `"sjekket av RIE 12.03"` | K9: «1203 er ikke i skalaen», *pluss* «mangler MMI» på to andre objekter |

Den siste er den verste: en feillest verdi vipper K9s heuristikk for om fila i det
hele tatt bruker MMI, og produserer da funn om objekter som aldri var i nærheten av
problemet. Sprengradius er hele fagmodellen, ikke ett objekt.

Rapporten blander da sanne og usanne funn uten at leseren kan skille dem. §12 sier
README-en er halve produktet; den andre halvparten er at funnene stemmer. Et verktøy
som skal stå som port i en leveranseprosess (§5) taper tilliten sin på det første
funnet som viser seg å være oppdiktet.

## What Changes

- **Verdiuttrekket får proveniens.** Hver uttrukket verdi bærer med seg hvordan den
  ble funnet: fra konfigurert pset og felt, fra et gjenkjent feltnavn i et annet
  pset, eller ved gjetning.
- **Gjetningen må begrunnes.** Dagens siste fallback — «pset-et het riktig, ta
  første ikke-tomme verdi» — har ingen nøkkel og avgjøres av rekkefølgen
  egenskapene tilfeldigvis har i IFC-fila. En verdi funnet slik skal bare godtas
  hvis den er gjenkjennelig som det den utgir seg for å være.
- **Kandidatnavn skal være distinkte.** Et navn som brukes til å lete på tvers av
  alle egenskapssett må være distinkt nok til at et treff er bevis.
  **BREAKING:** `Type` fjernes fra `egenskapsnavn_type`; den treffer
  `Pset_ManufacturerTypeInformation` i praktisk talt enhver modell.
- **MMI-normaliseringen slutter å fordøye vilkårlig tekst.** «sjekket av RIE 12.03»
  blir i dag til nivå «1203».
- **Funn som hviler på en usikker verdi sier det.** Meldingen skal peke på årsaken
  brukeren kan gjøre noe med — at feltet ikke ble funnet der det var forventet —
  framfor å beskrive gjetningen som om den var data.
- **Meldingens presisjon skal svare til hva verktøyet vet.** Samme skjønn brukes
  også på den konfigurerte veien: i dag gir `Systemair` i TFM-feltet meldingen
  «Mangler «++»-delen: plassering (6 siffer)» — en presis anvisning om et felt som
  aldri inneholdt en TFM-ID. Parseren skiller ikke «dette er ikke en TFM-ID» fra
  «dette er en TFM-ID som mangler `++`».
- **`tfm_type` avklares.** Feltet leses og lagres, men ingen kontroll bruker det;
  K7 henter komponenttypen fra `%`-delen av den parsede forekomsten. Enten kobles
  det til noe, eller så slutter vi å lese det. Å bære en ubrukt verdi med den mest
  utsatte kandidatlista er en felle som allerede står oppspent.

## Capabilities

### New Capabilities
- `verdiuttrekk`: hvordan verktøyet finner TFM-forekomst, TFM-type og MMI i et
  objekts egenskapssett, hvor sikker den kan være på det den fant, og hva det har
  lov til å påstå om verdien. Dekker også hvordan en rå pset-verdi blir til et
  MMI-nivå. Skjønnet «ligner dette på en TFM-ID?» hører hjemme her fordi det brukes
  to steder — som port for en gjettet verdi og som valg av hvor spesifikk en
  feilmelding kan være — og de to må ikke kunne komme til ulik konklusjon.

### Modified Capabilities
<!-- Ingen. openspec/specs/ er tom; dette er den første spec-en i repoet. -->

## Impact

**Kode:** `ifc/loader.py` (`_finn`), `config.py` (`PsetOppsett`-standardverdier),
`modell.py` (`IfcObjekt`, `Funn`), `kontroller/k9_mmi.py` (`normaliser_mmi`),
og meldingstekster i kontrollene som rapporterer på en verdi.

**Konfigurasjon:** standardlista `egenskapsnavn_type` endres. Prosjekter som har
overstyrt den i `tfm-sjekk.toml` er upåvirket; de som lener seg på standarden får
endret oppførsel — til det bedre, men det er en endring.

**Ekstraksjonsgrensa er urørt.** Proveniens er tre strenger eller en enum på
`IfcObjekt`, altså picklebar data. Ingen kontroll trenger å importere
`ifcopenshell` for dette.

**Prøving:** enhetstester dekker de tre tilfellene i tabellen over, men den
avgjørende prøven er en ekte, rotete IFC-fil — helst en fagmodell fra et prosjekt,
ellers en offentlig fil fra buildingSMART. Ingen ekte modell har vært gjennom
verktøyet ennå, og alle fallbackene finnes nettopp for virkeligheten testmodellene
våre ikke inneholder.

## Utenfor omfanget

`_forklar` gir i dag samme generiske melding for alle verdier der alle
strukturmarkørene finnes, uansett hva som er galt i innholdet. Docstringen lover
noe annet — «forventet 6 siffer etter ++, fant 5» — men koden leverer det ikke.

Det er en mangel av samme familie, men det er en presisering av en melding som
allerede er sann. Denne endringen handler om meldinger som er usanne. Tas separat.
