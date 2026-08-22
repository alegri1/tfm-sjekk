## Why

En full kjøring krever i dag fem flagg:

```
tfm-sjekk sjekk rie.ifc riv.ifc \
    --systemtabell tabeller/ns3451.csv \
    --komponenttabell tabeller/ns3457-8.csv \
    --master TFM-master.xlsx \
    --config tfm-sjekk.toml \
    --ut rapport
```

Fire av dem peker på filer som er de samme hver eneste gang gjennom hele
prosjektet. De må likevel skrives på nytt for hver kjøring, eller huskes i et
skript ingen andre har.

Det står i veien for bruk. Fra §11-samtalen vet vi at målgruppa er små og
mellomstore prosjekter uten dRofus, som arbeider seg gjennom faser i Revit — ikke
team med et ferdig oppsatt CI-oppsett. En kommando som må slås opp hver gang, blir
kjørt sjeldnere enn en som kan skrives fra hodet.

`tfm-sjekk.toml` finnes allerede, men holder bare kolonnenavn og grammatikk. Den
vet ikke hvor mastera ligger, og den blir ikke funnet uten at du peker på den.

## What Changes

- `tfm-sjekk.toml` kan holde stiene til TFM-mastera og de to kodetabellene.
- Fila **finnes automatisk**: ved siden av den første modellen, ellers i
  arbeidskatalogen. `--config` peker fortsatt et bestemt sted når du vil det.
- Kjøringen **sier hvilket oppsett den leste**, eller at den ikke fant noe. Et
  oppsett som virker uten at brukeren vet om det, er verre enn ingen.
- Stier i konfigurasjonen tolkes **relativt til konfigurasjonsfila**, ikke til
  arbeidskatalogen, slik at fila kan flyttes og deles sammen med tabellene.
- Et flagg på kommandolinja vinner over det som står i fila.
- **En sti som står i konfigurasjonen og ikke finnes, er en feil.** Ikke oppgitt i
  det hele tatt er fortsatt et valg, og kontrollen hopper over som før.

Etter dette:

```
tfm-sjekk sjekk rie.ifc riv.ifc
```

## Capabilities

### New Capabilities
- `oppsettfunn`: Hvordan verktøyet finner konfigurasjonen sin, hvordan stier i den
  tolkes, hva som vinner når både flagg og fil sier noe, og hva som skjer når en
  oppgitt sti ikke finnes. Alt sammen er usynlig for brukeren med mindre verktøyet
  sier fra — og et oppsett som endrer resultatet i stillhet er en felle.

### Modified Capabilities

Ingen. Ingen kontroll endrer hva den finner eller melder.

## Impact

- **`config.py`:** felter for de tre stiene, og oppslag som finner fila.
- **`cli.py`:** `sjekk` og `oppsett` bruker funnet oppsett når `--config` mangler,
  og melder hvilken fil som ble lest.
- **Uendret:** kontrollene, uttrekket, rapportene, BCF.
- **Prøving:** kjøres fra en annen mappe enn modellen ligger i, og ved
  dra-og-slipp — det er de to tilfellene der «arbeidskatalogen» og «ved siden av
  modellen» er ulike, og hele grunnen til at rekkefølgen betyr noe.
