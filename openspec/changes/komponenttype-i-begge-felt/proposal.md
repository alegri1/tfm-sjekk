## Why

Komponenttypen står to steder i en modell, og verktøyet ser bare det ene:

```
TFM11_Forekomst:  ++115080=3600.001.04-JVZ001%JVZ.001.008
                                               └── %-delen, som K7 bruker
TFM11_Type:       JVZ.001.008
                  └── leses inn som tfm_type, og brukes ingen steder
```

`tfm_type` leses i loaderen og lagres på `IfcObjekt`. Ingen kontroll rører den.
Den eneste referansen i testene slår fast at den er `None`.

Det er to tapte muligheter i det:

**De to feltene kan sprike, og ingen oppdager det.** Samme opplysning i to felt er
nettopp der en modell går ut av synk med seg selv — noen retter TFM-ID-en uten å
rette typefeltet, eller motsatt. Det er samme slags relasjonelle sjekk som K6 og
K8, og ingen andre verktøy gjør den.

**K7 hopper over objekter uten `%`-del.** `krev_komponenttype` er `false` som
standard, fordi mange prosjekter utelater `%`-delen — og da er `TFM11_Type` den
eneste kilden til komponenttypen. I demoen har ett av femten objekter en `%`-del.
K7 sjekker altså komponenttyper mot mastera for en forsvinnende liten del av en
typisk modell, mens opplysningen ligger rett ved siden av, ulest.

Å bære en ubrukt verdi er dessuten en felle: da `Type` sto i kandidatlista, plukket
`tfm_type` opp fabrikatnavn fra `Pset_ManufacturerTypeInformation` uten at noen
merket det, nettopp fordi ingen leste feltet.

## What Changes

- **Ny kontroll T1: komponenttypen skal være den samme i begge feltene.** Har et
  objekt både en `%`-del og en `TFM11_Type`, og de ikke er like, er det et funn.
- **Graden er feil.** Det er en selvmotsigelse i merkingen, av samme slag som K6
  (duplikat komponentforekomst) og K8b (feil system på fordelingen), og de er begge
  feil. Verdien lar seg ikke avgjøre uten å rette modellen.
- **Kontrollen står utenfor K-serien**, som D1. §4 definerer K1–K9, og
  `specification/` er fasit for §-numrene og vokser ikke per endring. Et «K10»
  ville vært et nummer uten paragraf bak seg.
- **K7 bruker `TFM11_Type` når `%`-delen mangler.** Da får K7 en komponenttype å
  sjekke mot mastera for objekter den i dag hopper over. Er begge til stede, har
  `%`-delen forrang — den er en del av TFM-ID-en, som er det merkingen egentlig er.
- **Sprikende verdier gir ikke K7-funn i tillegg.** T1 melder allerede at de to er
  uenige; K7 skal ikke melde at «den ene av dem» ikke står i mastera, når spørsmålet
  om hvilken som gjelder er uavklart.

## Capabilities

### New Capabilities
- `komponenttype`: hvordan verktøyet fastslår et objekts komponenttype når den kan
  stå to steder, hva som skjer når de to er uenige, og hvilken kilde som gjelder når
  bare én finnes.

### Modified Capabilities
<!-- Ingen. K7s bruk av komponenttypen mot mastera er uendret; det er kilden til
     verdien som utvides, og den hører hjemme i den nye evnen. -->

## Impact

**Kode:** en ny kontroll, `kontekst.py` for et felles oppslag av komponenttypen, og
`k7_master.py` som bytter fra `tfm.komponenttype` til det oppslaget.

**Nye funn i eksisterende modeller.** Objekter som har begge feltene med ulikt
innhold vil nå gi feil, og K7 vil melde komponenttyper den før hoppet over. For en
modell som er i orden endres ingenting; for en som ikke er det, er det hele poenget.
Graden er verdt en innvending før implementasjon, siden den påvirker exit-koden.

**En felle sprang da verdien ble tatt i bruk.** `TFM` sto i både
`egenskapsnavn_forekomst` og `egenskapsnavn_type`, så en modell uten
`TFM11_Type`-pset fikk hele TFM-ID-en lest inn som komponenttype gjennom søket på
tvers av egenskapssett — og T1 meldte sprik på hvert eneste objekt. Det brøt kravet
om distinkte feltnavn i `verdiuttrekk`, usynlig så lenge `tfm_type` var ubrukt.
Navnet er fjernet fra typelista. **BREAKING** for prosjekter som lener seg på
standardverdien.

**Demoen har ett objekt med `%`-del.** Den må utvides for å vise både et sprik og
et objekt der `TFM11_Type` er eneste kilde — ellers demonstrerer ingenting av dette.

**Prøving:** en modell der begge feltene finnes. De to offentlige filene som er
prøvd tidligere har verken TFM-merking eller `TFM11_Type`, så dette må prøves mot en
norsk fagmodell for å si noe om hvor vanlig spriket er.
