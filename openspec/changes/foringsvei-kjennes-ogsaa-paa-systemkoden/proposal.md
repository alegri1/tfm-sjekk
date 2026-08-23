## Why

K8 kjenner en føringsvei igjen på IFC-klassen. Det holder så lenge eksporten gir
kabelrøret en klasse som sier hva det er.

Det gjør den ikke alltid. I en ekte Revit-eksport av Snowdon Towers kom seksten
koblingsbokser ut som `IfcBuildingElementProxy` — en anonym boks. TFM-en deres
sier `4360`, altså kabelforing; IFC-klassen sier ingenting. K8 tror på
IFC-klassen, krever kursnummer, og melder seksten funn om objekter som ikke
ligger på noen kurs og aldri kommer til å gjøre det.

Funnene er ikke gale. Verktøyet *kan* ikke vite at en proxy er en føringsvei —
det er nettopp derfor `oppsett`-kommandoen finnes. Men prosjektet har allerede
sagt hva objektet er, i TFM-ID-en, og verktøyet leser den ikke.

Proxyer er ikke et særtilfelle. README-en sier det selv: en ekte eksport legger
ofte utstyr der. I den samme modellen var 934 av objektene proxyer.

## What Changes

- Ny nøkkel `elektro.foring_systemkoder`. Er et objekts systemkode i lista,
  regnes objektet som føringsvei uansett hvilken IFC-klasse det har.
- **Standardlista er tom.** NS 3451 er en betalt standard, og hvilken kode som
  betyr føringsvei er innhold derfra (§8). Mekanismen hører hjemme i verktøyet;
  koden hører hjemme hos prosjektet, som resten av regelsettet (§14).
- De to måtene å kjenne igjen en føringsvei på virker ved siden av hverandre:
  et objekt er unntatt hvis IFC-klassen **eller** systemkoden sier det.
- Uendret ellers: `foring_klasser` beholder standardlista si, unntaket gjelder
  fortsatt bare kravet om kursnummer, og ingen annen kontroll rører seg.

## Capabilities

### New Capabilities

Ingen.

### Modified Capabilities

- `kursnummer`: Nytt krav om at prosjektet skal kunne oppgi hvilke systemkoder
  som er føringsvei, med tom standardliste. De fire eksisterende kravene står
  uendret — ingen av dem slutter å gjelde, og oppførselen uten konfigurasjon er
  den samme som i dag.

## Impact

- **`config.py`:** `ElektroOppsett.foring_systemkoder: list[str] = []`.
- **`kontekst.py`:** `er_foringsvei` tar imot den parsede TFM-ID-en i tillegg til
  objektet, slik at den kan se på systemkoden. Det er en signaturendring på en
  metode K8 er eneste bruker av.
- **`kontroller/k8_elektro.py`:** kallet i `_a_kursnummer_utfylt`.
- **`tfm-sjekk.toml`:** nøkkelen dokumentert, med tom liste og begrunnelsen for
  hvorfor den er tom.
- **Uendret:** de øvrige kontrollene, `tfm_sjekk.ifc`, rapportformatene,
  Dynamo-skriptene.
- **Prøving:** demomodellene har ingen proxy med føringsvei-kode, så de kan ikke
  skille rett fra galt her. Testene bygger derfor sine egne objekter: en proxy
  merket med en konfigurert systemkode skal være unntatt, og den samme proxyen
  uten konfigurasjon skal fortsatt meldes. Mot Snowdon-eksporten skal
  funntallet gå fra 177 til 161 når `4360` er konfigurert, og stå på 177 uten.
