# tfm-sjekk

Validerer TFM-merking i IFC-modeller mot NS 3457-serien og prosjektets TFM-master.

> **Status: under utvikling.** Alle kontrollene K1–K9 virker, og rapportene
> (BCF 2.1, HTML, CSV) er på plass. BCF-fila er ikke prøvd i en ekte viewer ennå.
> Hypotesen bak verktøyet er ikke validert — se §11 i spesifikasjonen.

---

## Problemet

Norske byggeprosjekter krever tverrfaglig merking (TFM) av objekter i BIM-modellene,
men i praksis er merkingen inkonsistent. Feil oppdages ofte først ved modelleveranse
til arkiv eller ved overlevering til FDV — altså for sent og for dyrt.

En TFM-ID ser slik ut:

```
++115080=3600.001.04-JVZ001%JVZ.001.008
```

Skriv `4310` der `4310.001.00` mangler kursnummer, eller gjenbruk `QLF001` i to
fagmodeller, og ingen oppdager det før i FDV-fasen.

## Hvorfor ikke bare IDS eller Solibri?

**IDS** er per design begrenset til det som kan avgjøres på ett objekt om gangen.
Det dekker K1–K5. Men det kan ikke uttrykke at ingen to objekter deler
komponentforekomst-ID, at et system finnes i prosjektets master, eller at et
kursnummer stemmer med fordelingen objektet er tilkoblet.

**Solibri** gjør relasjonssjekker, men regelsettet er internasjonalt og generisk —
det kan ikke NS 3451-tabellen, NS 3457-8-kodene eller PA 0805s regler, og det koster
lisens.

Nisjen er norsk-spesifikk, relasjonell, gratis og kjørbar i CI.

## Kontrollene

| # | Kontroll | Grad | Status |
|---|---|---|---|
| K1 | Alle objekter i konfigurerte IFC-klasser har en TFM-verdi | feil | ✅ |
| K2 | TFM-ID-en parser mot grammatikken | feil | ✅ |
| K3 | Systemkoden finnes i NS 3451 tabell 8 | feil | ✅ |
| K4 | Systemkoden er angitt så spesifikt som mulig (PA 0805) | advarsel | ✅ |
| K5 | Komponentkoden finnes i NS 3457-8 | feil | ✅ |
| K6 | Komponentforekomster er unike, også på tvers av fagmodeller | feil | ✅ |
| K7 | Systemer og typer finnes i prosjektets TFM-master (SIMBA) | feil | ✅ |
| K8 | Elektro: kurs-/sløyfenummer utfylt og konsistent | feil | ✅ |
| K9 | MMI/prosesstatus satt og konsistent | info | ✅ |

## Installasjon

```bash
uv sync          # utvikling
# pipx install tfm-sjekk   (når v1 er publisert)
```

**Uten Python:** last ned den frittstående binæren fra siste kjøring av
`bygg`-arbeidsflyten under Actions — artefaktene heter `tfm-sjekk-windows`,
`tfm-sjekk-macos` og `tfm-sjekk-linux`. Én fil, ingen installasjon. Mange
BIM-koordinatorer har ikke Python og får ikke lov til å installere det heller
(§6).

Bygge den selv:

```bash
uv run pyinstaller tfm-sjekk.spec --noconfirm   # → dist/tfm-sjekk[.exe]
```

Binæren blir rundt 57 MB, fordi `ifcopenshell` alene er 82 MB på disk, og
bruker et par sekunder på å starte: én fil betyr at alt pakkes ut i minnet ved
hver kjøring. Det er byttehandelen mot å slippe installasjon.

### Uten kommandolinje

**Dra IFC-filene oppå `tfm-sjekk.exe`** i Utforskeren. Rapportene havner i en
mappe som heter `rapport` ved siden av modellene. Flere filer på én gang
federeres, som er det K6 trenger for å finne duplikater på tvers av fagmodeller.

Uten kodetabeller hopper K3, K4, K5 og K7 over — de trenger `--systemtabell`,
`--komponenttabell` og `--master`, og da må du på kommandolinja. Resten kjører.

**Dobbeltklikk** viser en kort bruksanvisning og lar vinduet stå til du trykker
Enter. Uten det ville Windows lukket konsollen i samme øyeblikk programmet var
ferdig, og du hadde ikke rukket å lese noe.

## Bruk

```bash
tfm-sjekk sjekk rie.ifc riv.ifc \
    --systemtabell min-ns3451.csv \
    --komponenttabell min-ns3457-8.csv \
    --master tfm-master.xlsx \
    --config tfm-sjekk.toml \
    --ut rapport/
```

Flere filer federeres og kontrolleres samlet — det er slik K6 finner duplikater
på tvers av fagmodeller. Exit-kode 0 ved ingen feil, 1 ved feil, slik at verktøyet
kan stå som port i en leveranseprosess.

Hver kjøring skriver fire filer til `--ut`:

| Fil | Til hva |
|---|---|
| `funn.bcfzip` | BCF 2.1 — åpnes i Solibri, Catenda, Dalux, BIMcollab |
| `rapport.html` | Én selvstendig fil med sorterbar tabell, til deling |
| `funn.xlsx` | For analyse i Excel — frosset overskriftsrad og filter |
| `funn.csv` | Semikolonseparert UTF-8, for skript og pandas |

Prøv det med demomodellene:

```bash
uv run python eksempler/lag_demomodell.py
uv run tfm-sjekk sjekk eksempler/demo-rie.ifc eksempler/demo-riv.ifc eksempler/demo-elektro.ifc \
    --systemtabell eksempler/FIKTIV-systemkoder.csv \
    --komponenttabell eksempler/FIKTIV-komponentkoder.csv \
    --master eksempler/FIKTIV-tfm-master.csv
```

`tfm-sjekk kontroller` lister kontrollene og statusen deres.

## Om standardene og kodetabellene

**NS 3451 og NS 3457-serien er betalte standarder fra Standard Norge. Kodetabellene
følger ikke med dette verktøyet, og de skal ikke legges i dette repoet.**

Du peker på dine egne CSV-filer med `--systemtabell` og `--komponenttabell`:

```
kode;beskrivelse
2310;<beskrivelse fra standarden>
```

Filene under `eksempler/` er oppdiktede og ikke-normative — de finnes bare for at
testene og demoen skal kunne kjøre.

Dette gjør verktøyet lovlig å publisere, og det gjør det generelt: en byggherre med
eget kodeverk kan bruke det med sin egen tabell.

## Elektrokontrollene (K8)

Dette er kontrollen som krever at man forstår både IFC og et kursopplegg, og
den går i tre trinn:

- **K8a** — for NS 3451 kapittel 4 og 5 skal undernummeret være utfylt; det er
  kurs-/sløyfenummeret. Fordelinger er unntatt: tavla er roten kursene går ut
  fra, ikke noe som selv ligger på en kurs, så `=4310.001.00` er riktig der.
- **K8b** — alt som mates fra en fordeling skal tilhøre fordelingens system.
  Sammenligningen går på systemet (`4310.001`), ikke på systemforekomsten
  (`4310.001.12`) — undernummeret er nettopp det som skal variere.
- **K8c** — to *ulike* kurser på samme fordeling skal ikke ha samme kursnummer.
  At ti armaturer deler kurs 12 er normalt; at kurs 12 finnes to ganger er ikke.

Fordelingen finnes ved IFC-klasse (`IfcElectricDistributionBoard` i IFC4,
`IfcElectricDistributionPoint` i 2x3) og hva som henger på den ved å følge
koblingene mellom `IfcDistributionPort`-ene. Søket stopper i neste fordeling,
slik at en underfordeling blir sin egen rot.

K8c trenger at kursene er gruppert i modellen (`IfcDistributionCircuit` /
`IfcElectricalCircuit`). Mangler de, sier verktøyet fra én gang framfor å gjette.
Klassenavnene ligger under `[elektro]` i `tfm-sjekk.toml`.

## Excel: bruk `funn.xlsx`, ikke CSV-en

De to filene har hver sin jobb, og grunnen er verdt å kjenne til.

CSV er tekst, og Excel må gjette to ting: skilletegnet og tegnkodingen.
Skrivebords-Excel deler på listeskilletegnet fra regionsinnstillingene —
semikolon på en norsk maskin — mens **Excel på web antar komma** og legger hele
rapporten i kolonne A. Løsningen på det, en `sep=;`-linje øverst, setter
samtidig Excel på en parse-vei som **ignorerer BOM-en**, og da blir «følger» til
«fÃ¸lger». Innenfor én CSV kan Excel gi riktige tegn eller riktige kolonner,
ikke begge.

`funn.xlsx` har ingenting å gjette: tegn og kolonner ligger strukturert i fila,
og den åpner likt i begge utgavene av Excel. Overskriftsraden er frosset og
filtrerbar. `openpyxl` var allerede en avhengighet for å lese TFM-mastera, så
formatet koster ikke noe ekstra.

`funn.csv` er dermed fri til å være det maskinlesbare formatet: semikolon,
UTF-8 med BOM, ingen direktivlinje. `csv`-modulen, pandas og `Import-Csv` leser
den rett fram.

## BCF-fila

BCF er forskjellen mellom «interessant skript» og «noe vi tar i bruk»: funnene
åpnes i verktøyene folk allerede sitter i, og hvert emne har et viewpoint som
velger objektet det gjelder. Kontroll-ID-en ligger både i tittelen og som
`Labels`, så det er lett å filtrere per kontroll i viewer-en. Samlefunn som
peker på modellen som helhet (K7 og K8c) får emne uten viewpoint — det er
ingenting å zoome til.

Fila skrives direkte som zip + XML, uten BCF-bibliotek. Formatet er lite nok
til at avhengigheten ikke lønner seg, og det holder PyInstaller-binæren mindre.

**Utdata er deterministisk.** Emne-GUID-ene er utledet fra innholdet i funnet,
ikke trukket tilfeldig, og zip-oppføringene har fast tidsstempel. Et emne som
allerede er importert i en viewer beholder derfor identiteten sin mellom
kjøringer.

Det siste som varierer er `CreationDate`. Sett `--opprettet` for å låse den, så
blir hele fila byte-identisk og kan sammenlignes i CI:

```bash
tfm-sjekk sjekk modell.ifc --opprettet 2026-01-01T12:00:00Z
```

Verdien tolkes som ISO 8601 og regnes om til UTC, så `2026-01-01T13:00:00+01:00`
gir samme fil. En verdi uten tidssone leses som UTC, ikke lokal tid — ellers
ville to maskiner fått ulik fil av samme kommando. Uten flagget brukes klokka nå.

## Prosesstatus (K9)

MMI-skalaen varierer mellom byggherrer, så den ligger under `[mmi]` i
`tfm-sjekk.toml`. «MMI 300», «mmi300» og «300» leses som samme nivå.

K9 spør om MMI er satt, om verdien er i skalaen, og om den er konsistent
innenfor systemet (`4310.001` — ikke per kurs; en modenhetsgrad hører til
systemet som helhet). Sprikende MMI rapporteres mot flertallet i systemet, så
meldingen peker på de få objektene som er glemt.

Graden er **info**, ikke feil: et system *skal* ha objekter på ulike nivåer
midt i en prosjekteringsfase. En modell der ingen objekter har MMI antas å ikke
bruke MMI, og gir ingen funn — sett `krev_pa_alle = true` hvis prosjektet
krever det på alt.

## TFM-mastera

`--master` tar prosjektets egen TFM-master som XLSX eller CSV. Formatet er ikke
standardisert, så verktøyet gjenkjenner **kolonneoverskrifter**, ikke arknavn: alle
ark leses, og ark uten en kjent kolonne hoppes over. Overskriftsraden trenger ikke
stå øverst — logo og revisjonstabell over tabellen er greit.

```
systemforekomst;komponenttype
3600.001.04;JVZ.001.008
```

Prefikser folk skriver av gammel vane (`=3600.001.04`, `++115080=3600.001.04`)
normaliseres bort, så mastera og modellen trenger bare være enige om innholdet.
Heter kolonnene noe annet hos deg, settes navnene under `[master]` i
`tfm-sjekk.toml`.

K7 går begge veier. Et system eller en komponenttype modellen bruker uten at det
står i mastera er en **feil**. Oppføringer i mastera som ikke er modellert
rapporteres som **info** og teller ikke mot exit-koden — de kan like gjerne være
prosjektert men ikke tegnet ennå, og å skille det fra utgåtte oppføringer krever
prosesstatus (K9).

## Avgrensning

Ingen GUI, ingen 3D-visning, ingen Revit-plugin, ingen webapp, ingen skriving tilbake
til modellen, ingen støtte for samferdsel. Se §3 og §10 i spesifikasjonen.

## Utvikling

```bash
uv sync
uv run pytest
uv run ruff check .
```

Arkitekturen i korthet: `tfm_sjekk.ifc` er eneste modul som importerer
`ifcopenshell` og returnerer ren, picklebar data. Alt derfra — parser, kontroller,
rapporter — jobber mot `Kontekst`, som holder hele den federerte modellen. Hver
kontroll er en ren funksjon `Kontekst -> list[Funn]`. Det er den grensen som gjør
K6–K8 mulige, og som lar kontrollene testes uten en eneste IFC-fil.

Koblingsgrafen følger samme regel: portene i IFC leses i `loader.py` og legges
igjen der som `IfcObjekt.tilkoblet` — en liste med GlobalId-er. Kontrollene ser
en graf av rene strenger og har aldri hørt om `IfcDistributionPort`.

Full spesifikasjon: [`specification/tfm-sjekk-spesifikasjon.md`](specification/tfm-sjekk-spesifikasjon.md).
Paragrafhenvisninger i koden (§4, §8, …) peker dit.

## Publisering

`publiser`-arbeidsflyten bygger og laster opp til PyPI når en tag pushes:

```bash
git tag v0.1.0 && git push origin v0.1.0
```

Taggen sjekkes mot `version` i `pyproject.toml` før noe bygges. Et hjul med
feil versjonsnummer kan ikke trekkes tilbake fra PyPI — versjonen er brent for
godt — så det er verdt et eget steg. Testene kjøres i samme jobb, siden en
tag-push ikke utløser `test`-arbeidsflyten.

Autentiseringen er **trusted publishing**: PyPI stoler på en OIDC-billett fra
GitHub Actions, og det finnes ingen API-nøkkel å lekke. Oppsettet gjøres én
gang, før første tag:

1. Lag prosjektet på [pypi.org](https://pypi.org) — eller bruk «pending
   publisher» hvis navnet ennå ikke er tatt.
2. Under **Publishing → Add a new publisher**, velg GitHub og fyll inn eier,
   repo, workflow-fil `publiser.yml` og miljø `pypi`.
3. Lag miljøet `pypi` under repoets **Settings → Environments**. Vil du ha en
   godkjenning før hver utgivelse, legg til deg selv som «required reviewer»
   der.

`workflow_dispatch` kjører bygg og pakkesjekk uten å publisere, så kjeden kan
prøves før du binder deg til et versjonsnummer.

## Lisens

MIT.
