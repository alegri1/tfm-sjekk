## Context

Se proposal.md — Why. Det som former løsningen her er tre ting som allerede
finnes i koden:

- `finn_oppsett([])` faller tilbake til arbeidskatalogen når ingen modell peker
  ut en mappe. Den faste ruten trenger derfor ingen ny oppslagsregel: en `.cmd`
  ved siden av `tfm-sjekk.toml` finner oppsettet av seg selv.
- `Konfigurasjon.sti(felt)` løser én sti mot oppsettfila. `modeller` er en liste,
  og trenger sin egen variant av samme regel.
- `_fra_oppsett` har allerede mønsteret «flagget vinner, og en sti fra fila som
  ikke finnes er en feil». De nye nøklene skal oppføre seg likt.

For grafene er den bærende begrensningen at Dynamos Python-node lagrer skriptet
som en **streng inne i `.dyn`-fila**. Den leser ikke fra `dynamo/*.py`, og den
vet ikke at fila har endret seg.

## Goals / Non-Goals

**Goals:**
- Runden er én kommando uten argumenter, og ruten står ett sted.
- Grafene er noe man åpner, ikke noe man bygger.
- Kopien inne i en `.dyn` kan ikke drive fra kilden uten at bygget sier fra.

**Non-Goals:**
- Ingen `vakt`-modus som følger med på en mappe. Det er neste steg om friksjonen
  fortsatt kjennes, og det skal måles etter denne endringen, ikke før.
- Ingen kontroll flyttes inn i Dynamo-grafen.
- Grafene versjoneres ikke mot Dynamo-versjoner. Én fil per graf, bygget i
  Dynamo 4.1.1; eldre Dynamo får bygge selv, og stegene blir stående.

## Decisions

### Modellstiene kan være mønstre, ikke bare filnavn

`modeller = ["eksport/*.ifc"]` skal virke, ikke bare eksplisitte filnavn.

Det følger av hva ruten er til for: brukeren skal legge eksporten et fast sted,
ikke vedlikeholde en liste over hva den ble hetende. Revit navngir eksporten
etter modellen, og en RIE som legger til en fagmodell skal ikke måtte huske å
redigere oppsettet også.

*Alternativ vurdert:* bare eksplisitte filnavn. Mer forutsigbart å lese, men
flytter vedlikeholdet til brukeren og gjør «legg fila her» til «legg fila her og
skriv den opp». Mønsteret er den ene tingen som gjør ruten fast.

**Rekkefølgen sorteres.** Et mønster gir filsystemets rekkefølge, og den er ikke
garantert lik mellom maskiner. Rapporttittelen er `", ".join(m.name)`, og
BCF-fila skal være byte-identisk for samme funn og samme `--opprettet`. Usortert
ville den ikke vært det, og feilen ville bare vist seg på en annen maskin.

### Et mønster uten treff er en feil, ikke en tom kjøring

Dette er hele grunnen til at ruten er trygg å skrive én gang. Se spec-en for
kravet; her står hvorfor det ble en feil og ikke en advarsel: ruten leses aldri
igjen etter at den er skrevet. En eksport som havnet i feil mappe ville gitt en
tom, grønn rapport hver eneste runde, og ingenting i rapporten ville sagt at den
handlet om null objekter.

Meldingen oppgir både mønsteret slik det sto og mappa det ble løst mot — samme
form som `_fra_oppsett` bruker i dag, fordi «finnes ikke» uten stien er ubrukelig
når stien er relativ til en fil brukeren ikke tenkte på.

### `--ut` fra oppsettet, men dra-og-slipp beholder sin egen regel

`_med_rapportmappe` legger på `--ut` ved dra-og-slipp, og et påsatt flagg vinner
over oppsettet. Konsekvensen er at en fil dratt oppå exe-en gir rapporten ved
siden av *fila*, ikke i prosjektets faste rapportmappe.

Det er riktig vei. Dra-og-slipp er en engangshandling som peker på en bestemt
fil, og rapporten skal dukke opp der brukeren nettopp så. Den faste ruten er for
den gjentatte kjøringen, og den kjøres fra `.cmd`-fila.

### Grafene er kilden for ledningene, `.py`-filene er kilden for skriptet

To filer beskriver det samme, og de kan drive fra hverandre — det har allerede
skjedd. Løsningen er å gi hver av dem ett ansvar:

```
   dynamo/tfm_til_revit.py       fasit for skriptet
            │
            │  verktoy/oppdater-grafene.py   (skriver)
            ▼
   dynamo/tfm-sjekk-tfm-til-revit.dyn
            │
            │  tests/test_dynamo.py          (vokter)
            ▼
        bygget feiler når de er ulike
```

En test som bare sammenligner ville krevd manuell innliming ved hver endring i
skriptet, og en test man ikke kan fikse på ett sekund blir slått av. Skriveren og
vokteren er samme regel sett fra to sider: `verktoy/oppdater-grafene.py` limer
inn, testen sier fra når noen glemte å kjøre den.

*Alternativ vurdert:* la `.dyn`-en laste skriptet fra disk ved kjøring. Dynamo
har ingen mekanisme for det i en Python-node, og en `exec(open(...))`-krok ville
gjort en fil på brukerens maskin til del av kjøringen — verre å feilsøke enn
kopien, og et nytt sted ting kan være av ulik alder.

### Hardkodede stier byttes mot verdier som feiler høylytt

`til-revit`-grafen har i dag `C:\Users\aleks\Desktop\...\funn.csv` i en
`StringInput`-node. Den skal ikke inn i repoet.

Erstatningen er ikke tom streng, men en tydelig plassholder som ikke kan finnes —
`C:\prosjekt\rapport\funn.csv`. `les_fil` kaster på en fil som ikke finnes, og en
graf som stopper med «finnes ikke» på en sti brukeren ser er selvforklarende. En
tom streng ville gitt en mindre lesbar feil lenger inne, og en relativ sti ville
vært tvetydig: Dynamo løser dem mot verten, ikke mot `.dyn`-fila.

Samme behandling av `"115080";` i `fra-revit`. Det er en ekte plasseringskode fra
Snowdon-kjøringen, og en ekte verdi som ser riktig ut er farligere enn en gal:
den ville merket en fremmed modell med Snowdons bygning uten at noe protesterte.

### `.dyn`-filene ligger i `dynamo/`, ikke i `eksempler/`

De hører sammen med skriptene de bærer en kopi av, og `oppdater-grafene.py`
skriver mellom naboer. `eksempler/` er FIKTIV-data etter §8; en Dynamo-graf er
ikke data.

## Risks / Trade-offs

**En `.dyn` med gyldig JSON kan ha en ledning som ikke fester seg** → Testen ser
bare på skriptkopien, ikke på grafen. Grafene må åpnes i Dynamo i Revit før
endringen kan kalles ferdig, og det er noe bare brukeren kan se. Står i
proposal.md under «Prøves hos konsumenten».

**Mønsteret kan plukke opp mer enn tenkt** — `*.ifc` i en mappe der noen la igjen
en gammel eksport → Dekningslinjene skriver hver fil for seg, og en fil som ikke
skulle vært med er synlig i utskriften. Kjøringen sier dessuten hvor mange
modeller den leste. Verktøyet tier ikke om hva det så på.

**En bruker som sender oppsettet videre sender også ruten** → Stiene er relative
til oppsettfila, så et prosjekt som flyttes i sin helhet virker fortsatt. En
absolutt sti gjør det ikke, men den var like ødelagt før denne endringen.

**Grafene blir en ny ting å vedlikeholde ved hver Dynamo-versjon** → De er JSON
med et versjonsfelt, og Dynamo åpner eldre filer. Blir det et problem, sier en
bruker fra; å versjonere dem i forkant ville vært å løse noe vi ikke har sett.
