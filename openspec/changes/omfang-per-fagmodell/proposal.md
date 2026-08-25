## Why

Første ekte federering, 25. august 2026: Snowdon Towers med RIE, ARK, RIB og
tomt, eksportert fra Revit 2027 som lenkede IFC-er.

    15 403 objekter, 4 fagmodeller, 45,7 sekunder

      ARK    675  K1 — mangler TFM
      RIB      1  D1 — ingenting kontrollert (0 av 5112)
      Site     1  D1 — ingenting kontrollert (0 av 107)
      RIE    177  K8 — elektroobjekt uten kursnummer

RIE-ens 177 er de ekte. ARK-ens 675 er armaturer og sanitærutstyr arkitekten har
tegnet inn — `Pendant-Dome` (110), `Recessed Lamp` (179), `Sink Vanity` (31),
`Toilet-Domestic` (21), 46 familier i alt. De er `IfcFlowTerminal`, altså i
omfanget, og de har ingen TFM fordi de ikke er RIE-ens ansvar.

Rapporten er teknisk korrekt og ubrukelig som arbeidsliste: de ekte funnene
drukner fire mot én i objekter ingen skal merke.

**`ifc_klasser` gjelder hele kjøringen, ikke den enkelte fila.** Valget står
mellom å federere og drukne i ARK, eller å la være å federere — og da forsvinner
K6 på tvers av fag, som er hele grunnen til å federere.

Det er også spørsmålet D1-meldingen stiller uten å kunne svare på: «Er dette en
fagmodell som skal sjekkes, utvid `ifc_klasser`». For ARK er svaret verken
utvid eller la være, men *«denne fila skal ikke sjekkes for TFM, og jeg vil
fortsatt ha den med»*.

**Hva vi vet og ikke vet.** Funnet kommer fra én modell. Prosjekteieren kjenner
det ikke igjen fra egen praksis og sier selv at erfaringsgrunnlaget er tynt, og
Snowdon er Autodesks demonstrasjonsmodell — den kan være mer sammenblandet enn
en norsk leveranse med tydelig fagdeling. At *problemet* er ekte er sikkert; at
det er *vanlig* er en antakelse. Endringen er derfor lagt opp så den koster
ingenting for den som ikke trenger den: uten den nye nøkkelen oppfører verktøyet
seg nøyaktig som i dag.

## What Changes

- `tfm-sjekk.toml` får omfang per fagmodell: en seksjon som knytter et
  filnavnmønster til sin egen `ifc_klasser`.
- En tom liste betyr **«denne fila skal ikke sjekkes for TFM»**, og det er en
  gyldig og bevisst tilstand — ikke det samme som at omfanget ble tomt ved et
  uhell.
- **D1 melder ikke tomt omfang når det er bestemt.** Uten dette ville hver
  bevisst unntatt fagmodell gitt en advarsel om at ingenting ble kontrollert, og
  D1 ville sluttet å bety noe.
- Kjøringen sier hvilke filer som er unntatt og hvorfor, på samme linje som
  dekningen. En fil som ikke sjekkes skal ikke kunne bli usynlig.
- Filer uten treff i noen seksjon bruker `ifc_klasser` på toppnivå, som i dag.

**Ikke berørt, og det er poenget:** K3–K8 og T1 leser `med_tfm()` og
`k.objekter`, ikke `relevante_objekter()`. K6 fortsetter derfor å finne
duplikater på tvers av ARK og RIE selv når ARK er unntatt — som er nøyaktig det
som gjør federeringen verdt noe. Bare K1 og D1 følger omfanget.

## Capabilities

### New Capabilities
- `fagmodellomfang`: at omfanget kan settes per fagmodell framfor per kjøring, at
  en bevisst unntatt fagmodell ikke meldes som uteglemt, og at en fil som ikke
  sjekkes sier fra om det framfor å bli borte i stillhet.

### Modified Capabilities
- `dekning`: kravet «Tomt omfang i en fagmodell gir et funn» må skille bevisst
  unntak fra uhell. Slik det står nå ville hver unntatt fagmodell gitt en
  advarsel om at ingenting ble kontrollert.

## Impact

- `src/tfm_sjekk/config.py`: en ny seksjon, og oppslag fra filnavn til omfang.
- `src/tfm_sjekk/kontekst.py`: `relevante_objekter()` og `dekning()` må se på
  hvilken fil objektet kom fra. Begge er i dag rene funksjoner av `config`.
- `src/tfm_sjekk/kontroller/d1_dekning.py`: skille bevisst fra uhell.
- `src/tfm_sjekk/cli.py`: linja som sier hva som ble unntatt.
- `openspec/specs/dekning/spec.md` får en delta.
- `tests/`: ny fil for evnen, og `test_dekning.py`.

**Prøves hos konsumenten:** mot de fire ekte Snowdon-eksportene i
`C:\Users\aleks\Desktop\revit-eksport-files`. Med ARK unntatt skal de 675
K1-funnene forsvinne, RIE-ens 177 stå urørt, og K6 fortsatt kunne finne et
duplikat på tvers av de to filene. Det siste må prøves ved å plante ett.
