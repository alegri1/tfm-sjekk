## Context

Se proposal.md — Why. Det som avgjør hvor liten endringen kan være, er hvordan
kontrollene henter objektene sine i dag:

```
  relevante_objekter()   filtrerer på ifc_klasser    K1, D1 (via dekning)
  med_tfm()              filtrerer IKKE              K3 K4 K5 K6 K7 K8, K9
  k.objekter             filtrerer IKKE              T1, K9
  k.parsefeil            filtrerer IKKE              K2
```

**Bare K1 og D1 følger omfanget.** De øvrige leser objekter som har en TFM-verdi,
uansett klasse — og en unntatt fagmodell har som regel ingen. Følgen er at
endringen berører to kontroller og ingen av de relasjonelle: K6 fortsetter å
finne duplikater på tvers av en unntatt fil uten at én linje i den røres.

Det var ikke planlagt slik. Det er en gunstig følge av at `med_tfm()` alltid har
lest hele modellen, og det er verdt å skrive ned før noen «rydder» i det.

## Goals / Non-Goals

**Goals:**
- Omfanget kan settes per fagmodell.
- Et bevisst unntak ser ikke ut som en forglemmelse — hverken i D1 eller i
  utskriften.
- Uten den nye nøkkelen er oppførselen bit for bit som før.

**Non-Goals:**
- Ingen egen konfigurasjonsfil per fagmodell. Ruten og oppsettet hører til
  prosjektet og skal kunne leses i én fil.
- Ingen automatisk gjenkjenning av fag fra filnavn. «Architectural» i et filnavn
  betyr ikke at fila skal unntas, og en gjetning her ville vært den slags
  usynlige avgjørelse verktøyet ellers unngår.
- Ingen unntak per klasse eller per objekt. Fila er enheten.

## Decisions

### Filnavnmønster, ikke full sti

`[fagmodell."*Architectural*"]`, ikke en absolutt sti.

Objektene bærer `kildefil`, som er filnavnet alene — det er allerede det som
vises i rapporten og i BCF-en. En sti ville dessuten gjort oppsettet umulig å
sende til en kollega, som er den samme grunnen til at de andre stiene løses mot
oppsettfila.

Mønsteret er nødvendig fordi Revit navngir lenkede eksporter etter verten:
`Snowdon Towers Sample Electrical-Snowdon Towers Sample Architectural.ifc`. Et
eksakt filnavn ville måttet skrives om hver gang vertsmodellen får nytt navn.

*Alternativ vurdert:* treff på IFC-en `LongName` eller på `IfcProject`-navnet.
Mer «riktig» på papiret, og verre i praksis: begge er tomme eller like i
eksporter fra Revit, og en nøkkel som ofte ikke finnes er ikke en nøkkel.

### Flere mønstre som treffer samme fil: det mest spesifikke vinner

Treffer to mønstre, gjelder det lengste. Er de like lange, er det en feil i
oppsettet, og kjøringen stopper.

Å velge det første i en vilkårlig rekkefølge ville vært en gjetning forkledd som
et svar — samme regel som `_hvor_horer_nokkelen_hjemme` allerede følger når den
nekter å peke på ett av flere steder.

### Tomt sett betyr unntatt, og det er den eneste måten å unnta på

Ingen egen `aktiv = false`-nøkkel. En fagmodell er unntatt når klasselista er tom.

To måter å si det samme ville før eller siden kommet i konflikt — hva betyr
`aktiv = true` med tom liste? — og lista svarer allerede presist: null klasser i
omfanget er null objekter å kontrollere.

### D1 spør oppsettet, ikke tallene

`dekning()` gir `(0, N)` for både et bevisst unntak og en forglemmelse. Tallene
kan ikke skille dem, og de skal ikke prøve.

D1 må derfor slå opp om fila er unntatt. Det binder kontrollen til
konfigurasjonen på en måte den ikke var før, og det er riktig her: forskjellen
mellom de to tilfellene *er* en opplysning som bare oppsettet har.

### Utskriften nevner unntaket på dekningslinja

    ARK.ifc: unntatt — kontrolleres ikke for TFM
    RIE.ifc: 1492 av 2439 objekter i omfanget

Ikke som en egen bolk lenger nede. Den som leser dekningen leser den for å vite
hva som ble sett på, og en fil som mangler fra den lista er verre enn en som står
der med en forklaring.

## Risks / Trade-offs

**Et mønster som treffer for bredt slår av kontroller i stillhet** → Derfor står
unntaket i utskriften ved hver kjøring. `*` som mønster ville unntatt alt, og
linja ville sagt det for hver eneste fil.

**D1 kan ikke lenger si fra om en fil noen unntok ved en feil** → Sant, og prisen
er tatt bevisst. Unntaket er en setning noen har skrevet i oppsettet; en tom
dekning er noe som skjedde. Verktøyet kan skille dem, men ikke vurdere om
setningen var klok.

**Bevisgrunnlaget er én modell** → Se proposal.md. Endringen koster ingenting for
den som ikke bruker den, og det er den avveiningen som gjør det forsvarlig å
bygge på ett tilfelle.

**Snowdon-ARK kan være usedvanlig sammenblandet** → Autodesks demonstrasjons-
modell skal vise mange fag i én fil. En norsk leveranse med tydelig fagdeling kan
ha færre armaturer i ARK. Det gjør ikke problemet mindre ekte, bare mindre
hyppig — og en RIE som møter det, møter 675 funn på én gang.
