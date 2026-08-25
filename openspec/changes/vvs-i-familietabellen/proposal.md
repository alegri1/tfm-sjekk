## Why

Målet er et komplett eksempel å vise fram: Snowdon Towers federert med alle
tekniske fag merket, ikke bare elektro.

`FAMILIER` er ren elektro — 4310 tavler, 4320 lys, 4330 uttak, 4360 føringsvei,
5300 data. HVAC og Plumbing har ingen av navnene, så hvert eneste RIV-objekt
faller til `STANDARD = ("4390", "QLX")`, en elektro-restkode. Modellen ville blitt
merket, rapporten ville sett hel ut, og hver ID ville vært systematisk gal.

Uten merking er det verre: `IfcAirTerminal` og `IfcSanitaryTerminal` arver begge
`IfcFlowTerminal`, så RIV havner i omfanget og gir K1 på hvert objekt — nøyaktig
det arkitektmodellen gjorde med 675 funn.

**Dette prøver ikke verktøyet.** Det er vurdert: K8 avgrenser seg på systemkode
(`er_elektro` er «4» eller «5»), og at den lar VVS i fred er allerede prøvd med
`demo-riv.ifc`. K6 på tvers er prøvd med et plantet duplikat. Dette er en demo vi
lager, ikke en test vi kjører, og det er verdt å kalle det det.

## What Changes

- `FAMILIER` får VVS-familiene fra Snowdon Towers: ventilasjon, varme, sanitær.
- **Kodene er funnet på, som de elektro er.** NS 3451 og NS 3457-serien er betalte
  standarder, og innholdet skal aldri inn i dette repoet (§8). Det står allerede
  med store bokstaver over tabellen; VVS-radene arver det forbeholdet.
- Samme tabell i `dynamo/tfm_fra_revit.py` og `verktoy/legg_til_tfm.py`, som i
  dag. Én test holder dem synkronisert, og den fanger opp de nye radene av seg
  selv.
- `dynamo/LES-MEG.md` sier at én tabell dekker alle fag, og hvorfor det virker.

## Lagt til underveis: løpenummeret ruller over

Funnet ved å kjøre merkingen mot de ekte modellene, ikke ved å lese koden.

Komponentens løpenummer er tre siffer, og telleren står per (systemkode, kurs).
VVS har ingen kurs, så alt havnet i én bøtte: **61 % av HVAC og 79 % av Plumbing
fikk firesifret løpenummer** — ugyldig grammatikk på noe som så ferdig merket ut.
Elektromodellen slapp unna fordi ekte kursnumre ga den 64 bøtter.

To ting løser det, og bare den ene er kode:

1. **`IN[1]` leser `System Name` for VVS.** Ingen kodeendring — `kursnummer()`
   trekker ut sifre av hva som helst. Én ledning i Dynamo. Gir undernummeret ekte
   innhold: «Mechanical Supply Air 22» → «22».
2. **Over 999 ruller det over i systemets løpenummer.** `3100.001.01-JSR999`
   etterfølges av `3100.002.01-JSR001`. Det er der formatet er ment å gå.

Tatt med her og ikke som egen endring fordi VVS-tabellen er ubrukelig uten den —
uten overrullingen er fire av fem merkede rør ugyldige.

Overrullingen er delvis fiksjon, og det står i koden: hvilke 999 som havner i
«system 1» følger rekkefølgen inn, ikke noe i bygget. Alternativet var
`komponent_lopenummer_siffer = 4`, som ville gitt prosjektet en grammatikk ingen
andre bruker og skjult at grensen finnes.

## Hva runden fant

Kjørt 25. august 2026 mot seks ekte fagmodeller — 24 456 objekter, 47 sekunder.

    RIE       177  K8 — elektroobjekt uten kursnummer
    HVAC      331  K6 — duplikat
    RIV-san   331  K6 — duplikat
    ARK/RIB/Site   unntatt

**De 662 K6-funnene er ekte, og de er det mest interessante i runden.**
Rørmodellen inneholder 331 avtrekkskanaler, og de ligger i de samme
`Mechanical Exhaust Air`-systemene som HVAC-modellens egne. **31 systemnavn er
identiske i begge filene** — samme system, delt over to Revit-modeller.

Ventilasjonsingeniøren tegnet hovedføringen, rørprosjekterende tegnet avtrekket
fra våtrommene, og begge koblet til de samme luftsystemene. Ingen av modellene
har en feil alene. Kollisjonen finnes bare på tvers, og bare et verktøy som
leser alle filene sammen kan se den.

Det er den ekte grunnen til å federere, demonstrert uten at noe er plantet.

Merkingen skapte den ikke — den avslørte den. Tabellen koder etter hva objektet
*er*, ikke hvilken fil det ligger i, og ga derfor rørmodellens kanaler
systemkode 3600. Hadde de fått en sanitærkode, ville kollisjonen vært skjult.

Funnet står. Å nummerere sammenhengende på tvers av modellene ville krevd at
merkingen ser begge samtidig, og Dynamo ser bare det aktive dokumentet.

## Capabilities

Ingen. Verktøyets oppførsel er uendret — `FAMILIER` er data i et skript som
merker en Revit-modell, og `tfm-sjekk` leser den aldri. `skip_specs: true`.

## Impact

- `dynamo/tfm_fra_revit.py` og `verktoy/legg_til_tfm.py`: nye rader i `FAMILIER`.
- `dynamo/*.dyn` må oppdateres med `verktoy/oppdater-grafene.py`, ellers bærer
  grafene en eldre kopi av skriptet.
- `tests/test_merking.py`: at ingen ny nøkkel skygger for en eksisterende, og at
  VVS-familier faktisk får 3xx.
- `dynamo/LES-MEG.md`.

**Prøves hos konsumenten:** grafen må kjøres mot HVAC- og Plumbing-modellene i
Revit, og resultatet leses. En familietabell som ser riktig ut i en test kan
fortsatt bomme på hvert eneste familienavn i den ekte modellen — det er nettopp
det `elementer_med_tfm` i sammendraget finnes for å avsløre.
