## Why

0.9.3 rettet modellfilene. De to andre stedene verktøyet møter omverdenen —
tabellene det leser, og filene det skriver — har den samme feilen.

### Rapportfila er åpen i Excel når du kjører på nytt

Det er selve rettingsrunden: kjør, åpne rapporten, rett modellen, kjør igjen. På
Windows nekter Excel andre å skrive til fila den har åpen.

Med en lås på `funn.xlsx` og en ny runde på en **annen** modell ser utmappa slik
ut etterpå:

```
rapport.html    3862 byte    ny        (fra denne runden)
funn.csv          73 byte    ny        (bare overskriftsraden)
funn.xlsx          0 byte    ØDELAGT   BadZipFile
funn.bcfzip     5491 byte    FRA FORRIGE RUNDE, byte-identisk
```

Fire filer fra to generasjoner, og ingenting sier fra. BCF-en er den farlige:
den ser fersk ut, ligger ved siden av en rapport fra denne runden, og den er den
fila som importeres i BIMcollab og tildeles folk. Regnearket er nullstilt, så
dataene fra forrige runde er borte også.

Exit-koden er **1** — «modellen har feil». Krasjen leses altså som «fortsatt
merkefeil». Utskriften er tretti linjer traceback gjennom `openpyxl` og
`zipfile`.

### Tabellene krasjer som modellfilene gjorde

```
tom kodetabell         IndexError i kodetabell.py:52              exit 1
CSV uten «kode»        ValueError — god melding, levert som traceback
falsk .xlsx-master     BadZipFile, seksti linjer gjennom openpyxl  exit 1
--ut peker på en fil   FileExistsError [WinError 183]             exit 1
```

Meldingene finnes til dels allerede — `kodetabell.py` reiser en `ValueError`
som sier nøyaktig hva som mangler. Den nås bare aldri som en melding.

Dette skjer dessuten **etter** at modellene er lest: en federert runde bruker
førtisju sekunder på 24 456 objekter og krasjer så på en tabell.

## What Changes

- En kodetabell eller TFM-master som ikke lar seg lese stopper kjøringen med en
  melding som navngir fila og sier hva som er galt, og med **exit 2** — som
  modellfilene siden 0.9.3.
- Tabellene leses **før** modellene. En feil i en tabell skal ikke koste en full
  federert kjøring før den oppdages.
- En rapportfil som ikke lar seg skrive stopper kjøringen med en melding som
  navngir fila og sier den vanligste årsaken, og med exit 2.
- **Utmappa skal aldri stå igjen med filer fra to runder.** Enten skrives alle
  fire, eller så er ingen av dem endret.
- `--ut` som peker på noe som ikke er en mappe er en feil med en melding, ikke
  en `FileExistsError`.

Ingen kontroll endrer oppførsel. Exit 0 og exit 1 betyr det samme som før.

## Capabilities

### New Capabilities

- `utdataskriving`: hva verktøyet garanterer om filene det skriver — at en
  kjøring enten etterlater fire filer fra samme runde eller ingen endring, og at
  en fil som ikke lar seg skrive blir sagt fra om.

### Modified Capabilities

- `modellesing`: kravene om melding, exit-kode og ingen halv rapport gjelder
  også kodetabeller og TFM-master. Evnen handler om grensen mot omverdenen, og
  en tabell som ikke lar seg lese er den samme grensen som en modell som ikke
  lar seg lese.

## Impact

- `src/tfm_sjekk/tabeller/kodetabell.py`, `tabeller/master.py`
- `src/tfm_sjekk/cli.py` — rekkefølgen på lesingen, og skrivingen
- `src/tfm_sjekk/rapport/` — skrivefunksjonene må kunne skrive til et annet sted
  enn den endelige stien
- `tests/test_master.py`, `tests/test_cli.py`, `tests/test_xlsx.py`
- README: exit-kodetabellen fra 0.9.3 nevner ikke tabeller eller skriving

Ingen nye avhengigheter. Ingen dataformater endres.
