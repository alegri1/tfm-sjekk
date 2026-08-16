# tfm-sjekk — spesifikasjon v1

Et åpent kommandolinjeverktøy som validerer TFM-merking i IFC-modeller mot NS 3457-serien og prosjektets TFM-master.

---

## 1. Problemet

Norske byggeprosjekter krever tverrfaglig merking (TFM) av objekter i BIM-modellene. Statsbyggs PA 0805 og SIMBA er de toneangivende kravsettene, og kommuner og private byggherrer kopierer dem i stor grad.

En TFM-ID ser slik ut (Statsbyggs eget eksempel, en tilluftsvifte):

```
++115080=3600.001.04-JVZ001%JVZ.001.008
```

Delt opp:

| Prefiks | Del | Innhold |
|---|---|---|
| `++` | Plassering | Byggnummer, normalt 6 siffer |
| `=` | Systemforekomst | Systemkode (4 siffer, NS 3451 tabell 8) . løpenummer (3 siffer) . undernummer (2–3 siffer) |
| `-` | Komponentforekomst | 3-bokstavskode (NS 3457-8) + 3-siffer løpenummer |
| `%` | Komponenttype | 3-bokstavskode + `.000.000` |

Undernummeret er fagavhengig: tur/retur for VVS, **kurs- eller sløyfenummer for elektro**.

I praksis er merkingen inkonsistent. Statsbygg skriver selv i SIMBA-veiledningen at det finnes flere ulike tolkninger av TFM-merking avhengig av prosjekt og driftsorganisasjon. Feil oppdages ofte først ved modelleveranse til arkiv eller ved overlevering til FDV — altså for sent og for dyrt.

**Hypotesen:** det finnes ikke et enkelt, åpent verktøy som sjekker om TFM-merkingen i en IFC-fil faktisk er syntaktisk gyldig og internt konsistent. Sjekk denne hypotesen før du skriver en linje kode (se §11).

---

## 2. Hvorfor IDS og Solibri ikke dekker dette

Dette avsnittet er selve produkttesen. Det er også det du skal si i intervjuer.

**IDS** (buildingSMART-standard siden juni 2024) er utmerket til krav som gjelder ett objekt om gangen: «alle vegger skal ha brannklasse», «denne egenskapen skal finnes og ha en verdi fra denne lista». IDS støtter regex-mønstre, så enkel syntakssjekk av en TFM-streng er faktisk mulig.

Men IDS er per design begrenset til det som kan avgjøres på ett objekt, uten forutgående beregning eller oppslag mot andre objekter. Det som *ikke* lar seg uttrykke:

- at ingen to objekter har samme komponentforekomst-ID
- at systemet en komponent viser til faktisk eksisterer i prosjektets systemliste
- at en elektrokomponents kursnummer stemmer med fordelingen den er tilkoblet
- at en overordnet systemkode ikke er brukt der en mer spesifikk finnes

**Solibri** gjør relasjonssjekker, men regelsettet er internasjonalt og generisk. Det kan ikke NS 3451-tabellen, NS 3457-8-kodene eller PA 0805s regler, og det koster lisens.

**Nisjen er altså:** norsk-spesifikk, relasjonell, gratis, og kjørbar i CI. Det er et lite og veldefinert hull. Ikke prøv å bli en Solibri-konkurrent.

---

## 3. Omfang v1

### Med

- Les IFC 2x3 og IFC4
- Hent TFM-verdier fra egenskapssett (`TFM11_Forekomst`, `TFM11_Type` er de vanlige i norske Revit-maler; gjør pset-navn konfigurerbart)
- Kjør kontrollene K1–K8 under
- Les prosjektets TFM-master (systemliste + komponentliste) fra CSV/XLSX
- Rapport: BCF-fil, HTML-rapport, CSV, og exit-kode for CI
- CLI: `tfm-sjekk modell.ifc --master tfm-master.xlsx --ut rapport/`

### Uten (bevisst)

Ingen GUI. Ingen 3D-visning. Ingen Revit-plugin. Ingen webapp. Ingen skriving tilbake til modellen. Ingen støtte for samferdsel. Alt dette er v2-diskusjoner — se §10.

Regel: hvis du ikke kan publisere v1 innen åtte uker, er omfanget for stort.

---

## 4. Kontrollene

Nummerér dem. Hver kontroll skal kunne slås av, ha alvorlighetsgrad (`feil` / `advarsel` / `info`), og en forklarende tekst på norsk i rapporten.

**K1 — Tilstedeværelse.** Alle objekter i konfigurerte IFC-klasser har en TFM-verdi. Uten dette blir resten meningsløst.

**K2 — Syntaks.** Strengen parser mot grammatikken i §1: riktige prefikser, riktig antall siffer og bokstaver, riktig rekkefølge. Dette er den kontrollen som fanger flest feil i praksis.

**K3 — Gyldig systemkode.** 4-sifferkoden finnes i NS 3451 tabell 8.

**K4 — Spesifisitetsregel.** PA 0805 sier at systemkoder skal angis mest mulig spesifikt, og at overordnede koder ikke skal brukes der underkoder finnes — eksempelet i standarden er at «2300 Ytterveggsystemer» ikke skal brukes når 2310, 2320 eller 2330 er tilgjengelige. Implementeres som: hvis kodetabellen har barn under koden som er brukt, gi advarsel.

**K5 — Gyldig komponentkode.** 3-bokstavskoden finnes i NS 3457-8.

**K6 — Unikhet.** Ingen duplikate komponentforekomst-IDer i modellen. Ved federering på tvers av fagmodeller: sjekk på tvers av alle filene som sendes inn.

**K7 — Referanseintegritet mot TFM-master.** SIMBA krever at prosjektet utarbeider en prosjektspesifikk TFM-master med tverrfaglig systemliste, komponentliste, komponentforekomster og komponenttyper. K7 sjekker at hvert system og hver komponenttype modellen bruker faktisk står i mastera — og motsatt, hvilke oppføringer i mastera som ennå ikke er modellert.

**K8 — Elektro-spesifikk konsistens.** Din faglige signatur. For systemer i NS 3451 kapittel 4 (elkraft) og 5 (tele og automatisering): undernummeret skal være utfylt og tolkes som kurs-/sløyfenummer. Kontroller at objekter tilkoblet samme fordeling har konsistent systemforekomst, og flagg kursnumre som gjentas innenfor samme fordeling. Dette er kontrollen ingen andre kommer til å skrive, fordi den krever at man forstår både IFC og et kursopplegg.

**K9 (valgfri, hvis tid).** Prosesstatus: er MMI-verdien satt, og er den konsistent innenfor et system? SIMBA stiller krav til prosesstatuskode.

---

## 5. Inn- og utdata

**Inn**
- Én eller flere `.ifc`-filer (federering)
- TFM-master som XLSX/CSV
- Kodetabeller som CSV (se §8 om hvorfor de ikke kan ligge i repoet)
- `tfm-sjekk.toml` for konfigurasjon: hvilke pset-navn, hvilke IFC-klasser per fag, hvilke kontroller aktive, alvorlighetsgrader

**Ut**
- **BCF 2.1** — viktigst. BCF er bare en zip med XML per emne (`markup.bcf`, `viewpoint.bcfv`, valgfri `snapshot.png`). IfcOpenShell har BCF-støtte, men formatet er enkelt nok til å skrive selv om du vil unngå avhengigheten. Poenget: funn åpnes direkte i Solibri, Catenda, Dalux og BIMcollab, altså i verktøyene folk allerede bruker. Dette er forskjellen mellom «interessant skript» og «noe vi tar i bruk».
- **HTML-rapport** — én selvstendig fil, sorterbar tabell, grupperbar per fag og kontroll. Dette er det folk deler i Teams.
- **CSV** — for videre analyse
- **Exit-kode** — 0 ved ingen feil, 1 ved feil. Gjør verktøyet kjørbart som port i en leveranseprosess.

---

## 6. Teknisk stack

Python. Ikke fordi det er best, men fordi IfcOpenShell er der og fordi bransjens egne folk skriver Python i Dynamo — terskelen for at noen andre bidrar blir lavere.

- `ifcopenshell` — IFC-parsing
- `lark` eller ren `re` for TFM-grammatikken. Start med regex; bytt til grammatikk først når reglene viser seg mer sammensatte enn ventet
- `pydantic` — datamodeller for parset TFM-ID, kontrollfunn, konfigurasjon
- `typer` — CLI
- `openpyxl` — TFM-master
- `jinja2` — HTML-rapport
- `pytest` + `hypothesis` — se §7
- `uv` for pakking, `ruff` for linting
- GitHub Actions: test på Linux/macOS/Windows, publiser til PyPI på tag

Distribuer som `pipx install tfm-sjekk` og som frittstående binærfil via PyInstaller. Mange BIM-koordinatorer har ikke Python installert og får ikke lov til å installere det heller.

---

## 7. Testing

Dette er der du viser at du er utvikler og ikke hobbyist, og det er derfor det er en egen paragraf.

- **Syntetiske IFC-filer.** Generer minimale modeller programmatisk med IfcOpenShell — ett objekt med korrekt TFM, ett med feil sifferantall, ett uten pset. Sjekk hver kontroll isolert. Disse er små nok til å ligge i repoet.
- **Property-based testing** på parseren med `hypothesis`: generer gyldige TFM-strenger fra grammatikken, verifiser at de parser; muter dem, verifiser at de avvises.
- **Golden files** for BCF- og HTML-utdata.
- **Én ekte modell.** Du trenger minst én reell IFC-fil for å oppdage hvor rotete virkeligheten er. Åpne eksempelmodeller finnes via buildingSMART, og du kan eksportere fra en Revit-prøvelisens. Ikke publiser prosjektdata du ikke eier.

---

## 8. Juridisk begrensning — les denne før du koder

NS 3451 og NS 3457-serien er betalte standarder fra Standard Norge. **Du kan ikke legge kodetabellene i et offentlig GitHub-repo.**

Designkonsekvens, og den er faktisk et salgsargument:

- Verktøyet leveres uten kodetabeller
- Brukeren peker på sin egen CSV: `--kodetabell ns3451.csv`
- Repoet inneholder kun en liten fiktiv eksempeltabell for testing, tydelig merket som ikke-normativ
- README sier eksplisitt at brukeren må ha gyldig tilgang til standardene

Dette gjør verktøyet lovlig å publisere, og det gjør det generelt: en byggherre med eget kodeverk kan bruke det med sin egen tabell. Skriv dette i README-en — det viser at du forstår bransjens rammer, ikke bare koden.

Lisens: MIT eller Apache 2.0. Ikke GPL, hvis du vil at et rådgiverfirma skal tørre å ta det i bruk internt.

---

## 9. Tidsplan — åtte uker på kvelder

| Uke | Leveranse |
|---|---|
| 0 | Valider hypotesen (§11). Ikke kod. |
| 1–2 | IFC inn, hent psets, få ut en liste over alle TFM-verdier i en modell. K1. |
| 3 | Parser + datamodell. K2. Testoppsett. |
| 4 | Kodetabeller, K3–K5. Konfigurasjonsfil. |
| 5 | K6–K7, TFM-master-innlesing. Federering av flere filer. |
| 6 | K8 — elektrokontrollene. Ta deg tid her; dette er differensiatoren. |
| 7 | BCF- og HTML-utdata. CLI-polering. |
| 8 | README på norsk, eksempelprosjekt, GitHub Actions, publisering. |

Hvis uke 6 sprekker, kutt K7 heller enn K8.

---

## 10. Etter v1

Ikke bygg noe av dette før v1 er publisert og noen faktisk har brukt det.

- **IDS-eksport.** Generer en IDS-fil for den delmengden av kontrollene som er per-objekt. Da komplementerer verktøyet IDS i stedet for å konkurrere, og du plasserer deg midt i den migreringen fra mvdXML som bransjen står i.
- **Revit-plugin** som kjører sjekken før eksport.
- **MMI-dashboard** — modenhetsstatus per fag over tid.
- **EFObasen-kobling** — berik objekter med el-nummer og produktdata via EFOs API, inkludert de strukturerte klimadataene.

---

## 11. Uke 0: valider før du koder

Fjorten år som utvikler har lært deg dette, men det er lett å hoppe over når man er ivrig etter å komme inn i en ny bransje.

Snakk med fem personer før du skriver kode:

1. En BIM-koordinator hos en stor rådgiver
2. En RIE som har levert til et Statsbygg-prosjekt
3. Noen i BIM-gruppa hos Statsbygg — de har en åpen henvendelsesadresse for BIM-spørsmål
4. En som selger eller supporterer Solibri i Norge, for å høre hva verktøyet deres *ikke* gjør
5. Noen aktiv i buildingSMART Norge

Spør: hvordan sjekker dere TFM i dag, hva går galt, og hva ville dere faktisk kjørt? Hvis tre av fem sier «vi sjekker manuelt i Excel», har du et produkt. Hvis alle sier «Solibri tar det», bytt idé — og da har du fem nye kontakter og har brukt to uker, ikke to måneder.

---

## 12. README-en er halve produktet

Skriv den på norsk. Struktur:

1. Problemet i tre setninger, med et eksempel på en feilmerket TFM-ID
2. Skjermbilde av HTML-rapporten
3. Installasjon i én linje
4. Kjøreeksempel i én linje
5. Kontrollene K1–K9 i tabell, med henvisning til hvilket krav hver enkelt springer ut av
6. Avgrensning: hva verktøyet *ikke* gjør, og hvorfor IDS og Solibri dekker andre ting
7. Om standardene og kodetabellene (§8)
8. Hvem du er — én setning: elkraft-master, utvikler, ny i BIM. Ærligheten er en styrke her.

---

## 13. Distribusjon

Norge er et lite marked. Når v1 er ute:

- LinkedIn-innlegg på norsk, ikke engelsk. Tagg buildingSMART Norge.
- Send lenka direkte til BIM-miljøene hos Statsbygg, Bane NOR og Nye Veier. De er kravstillerne, og de har ingen kommersiell interesse i å blokkere et gratis verktøy.
- Meld deg på et frokostmøte eller en fagsamling hos buildingSMART Norge og tilby en lynpresentasjon på ti minutter.
- Ikke send det til rekrutterere. Send det til fagfolk. Jobbene kommer den veien i denne bransjen.

---

## 14. Risikoer

| Risiko | Håndtering |
|---|---|
| Noen har bygget dette allerede | Uke 0. Søk GitHub på «TFM», «NS 3457», «IFC validering» først. |
| TFM-tolkningene varierer for mye til å validere generelt | Gjør alt konfigurerbart, ikke hardkodet. Lever regelsettet som data. |
| Du blir sittende for lenge i domenelesing | Sett tak: to uker på PA 0805, SIMBA og MMI-veilederen. Resten lærer du fra ekte modeller. |
| Ingen bruker det | Det er fortsatt en arbeidsprøve som beviser at du kan både IFC og elektro. Den funksjonen svikter ikke selv om produktet gjør det. |
