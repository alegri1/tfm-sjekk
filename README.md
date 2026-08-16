# tfm-sjekk

Validerer TFM-merking i IFC-modeller mot NS 3457-serien og prosjektets TFM-master.

> **Status: under utvikling (uke 0–1 av åtte).** K1–K8 virker.
> K9 (MMI) og BCF-eksport er ikke implementert ennå.
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
| K9 | MMI/prosesstatus satt og konsistent | info | ⬜ valgfri |

## Installasjon

```bash
uv sync          # utvikling
# pipx install tfm-sjekk   (når v1 er publisert)
```

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

## Lisens

MIT.
