## Why

Verktøyet kan ikke skille **«ingenting er galt»** fra **«jeg så ikke på noe»**. Begge
gir samme svar: null funn og exit 0.

Målt: en modell med tre objekter, alle uten TFM-merking, i klasser utenfor det
konfigurerte omfanget:

```
0 feil, 0 advarsler    EXIT=0
```

Grønt lys. Ingen kontroll hadde noe å se på.

Årsaken er at omfanget bestemmes av `ifc_klasser` i konfigurasjonen. Treffer ikke
lista modellens klasser, er omfanget tomt — og da har K1 ingen objekter å savne TFM
på, mens de øvrige kontrollene itererer over en tom liste.

Det er ikke et konstruert tilfelle. I buildingSMARTs egen VVS-eksempelmodell er
**2 av 6 objekter `IfcBuildingElementProxy`**, altså utenfor standardlista. En
Revit-eksport som legger uvanlig utstyr i proxyer, en ARK-modell kjørt gjennom et
oppsett for tekniske fag, eller en IFC 2x3-fil med andre klassenavn gir alle det
samme: null i omfanget, og en rapport som ser ren ut.

For et verktøy hvis salgsargument er «exit-kode 0/1, kjørbart som port i en
leveranseprosess» (§5), er dette en port som står åpen når den er feiljustert. Og
til forskjell fra en feilmelding som er gal, er denne stille: ingen blir varslet.

## What Changes

- **Rapporten sier alltid hvor mye som ble sjekket.** Antall objekter i omfanget
  mot antall objekter lest, per fagmodell. Tallet skal være synlig også når alt er
  i orden, slik at «0 av 412» ikke krever at noen leter etter det.
- **Tomt omfang i en fagmodell gir et funn.** Advarsel, ikke feil.
- **Exit-koden er uendret.** Et legitimt kjør på en modell uten tekniske fag skal
  ikke begynne å feile, og verktøyet står allerede i CI hos den som bruker det.
  Advarsler teller ikke mot exit-koden (§5), og det er nettopp derfor graden er
  riktig her.
- **Vurderingen gjøres per fagmodell.** Samme resonnement som K9 bruker for MMI: i
  en federering av RIE, RIV og ARK er det ARK-fila som skal si fra, selv om
  kjøringen samlet har 300 objekter i omfanget. Vurdert samlet ville nettopp det
  tilfellet man helst vil oppdage gått stille forbi.
- **Funnet peker på årsaken.** Meldingen skal nevne `ifc_klasser` og hvilke klasser
  fila faktisk inneholder, slik at den som leser den kan rette konfigurasjonen
  framfor å lure på hva som skjedde.

## Capabilities

### New Capabilities
- `dekning`: hva verktøyet sier om hvor mye av en modell det faktisk undersøkte.
  Dekker rapportering av omfanget per fagmodell, og hva som skjer når omfanget er
  tomt. Evnen finnes fordi fravær av funn ellers er tvetydig — den skiller et
  resultat fra en manglende undersøkelse.

### Modified Capabilities
<!-- Ingen. `verdiuttrekk` handler om hvordan en verdi finnes på et objekt som
     allerede er i omfanget; dekning handler om hvilke objekter som kom så langt. -->

## Impact

**Kode:** `kontekst.py` (omfanget er allerede beregnet der), en ny kontroll eller
en utvidelse av rapportlaget, og rapportformatene som skal vise dekningstallet.

**Rapportene:** HTML-en har allerede «objekter kontrollert» i tallrekka, men tallet
er antall *leste* objekter, ikke antall i omfanget — den forskjellen er hele saken,
og linja er i dag misvisende. XLSX og CSV har ingen naturlig plass til et
kjøringsnivå-tall; det hører i HTML-en og i CLI-utskriften.

**Ikke brytende.** Exit-koden endres ikke, og et nytt advarsel-funn påvirker ikke
`--opprettet`-determinismen i BCF-fila så lenge det behandles som ethvert annet funn
uten GlobalId.

**Prøving:** en ARK-modell eller en hvilken som helst IFC uten tekniske fag er nok
til å utløse tilfellet. buildingSMARTs `Building-Architecture.ifc` ligger offentlig
og er allerede brukt i dette prosjektet.
