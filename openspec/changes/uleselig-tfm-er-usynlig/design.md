## Context

Se proposal.md — Why. Mekanismen er én linje i `Kontekst`:

```python
def med_tfm(self):
    return [(o, self.parsede[o.global_id]) for o in self.objekter if o.global_id in self.parsede]
```

`parsede` og `parsefeil` fylles side om side i `Kontekst.bygg`. Sju kontroller
leser `med_tfm()`; ingen leser `parsefeil` unntatt K2. Tallet finnes altså
allerede — det er bare ingen som spør etter det.

    lest ──► i omfanget ──► med tolkbar TFM ──► kontrollert av K3–K9
                    │                │
                    │                └── parsefeil: usynlig for sju kontroller
                    └── utenfor ifc_klasser

Dekningen svarer på det første trinnet. Det andre er ikke målt.

## Goals / Non-Goals

**Goals:**
- Tallet som allerede finnes blir synlig.
- En systematisk konvensjonsfeil ser annerledes ut enn en håndfull skrivefeil.
- K2-meldingen sier hva funnet koster, ikke bare hva som er galt.

**Non-Goals:**
- Ingen ny toleranse i parseren. Verktøyet skal ikke gjette hva brukeren mente.
- Ingen liste over hvilke kontroller som ble hoppet over per objekt. Det er sju
  numre i hver eneste K2-melding, og det ville drukne selve feilen.
- Ingen endring i hvilke objekter kontrollene ser.

## Decisions

### Konvensjonsfunnet er en advarsel, ikke en feil

Samme grad som D1, og av samme grunn: verktøyet står som port i en
leveranseprosess (§5), og et prosjekt med en annen grammatikk skal ikke stenge
døra på et funn som handler om oppsettet.

De enkelte K2-funnene er fortsatt feil, og de avgjør exit-koden. Advarselen sier
noe *om* dem: at de er så mange at forklaringen sannsynligvis ligger et annet
sted.

### Funnet fyrer bare når noe faktisk har en TFM

«Ingen tolkbar TFM» og «ingen TFM i det hele tatt» er ulike ting. Det siste er
K1s jobb, og en umerket modell skal ikke i tillegg få en advarsel om
grammatikken.

Betingelsen er derfor: fagmodellen har objekter med TFM-verdi i omfanget, og
ingen av dem parset.

### Vurderingen er per fagmodell

Som D1 og K9. I en federering kan RIE-en være riktig merket mens RIV bruker en
annen konvensjon — samlet vurdering ville latt nettopp det gå stille forbi.

*Alternativ vurdert:* en terskel, som «over 80 % falt ut». Avvist: terskelen
ville vært et tall uten begrunnelse, og «alle» er den ene grensen som ikke
trenger forsvares. Faller 90 % ut, står de 10 % igjen som ekte funn — og de
enkelte K2-meldingene sier fortsatt hva som er galt.

### Tallet hører til dekningen, ikke til en ny tabell

Dekningen har allerede to tall per fagmodell. Et tredje hører hjemme der framfor
i en egen bolk: den som leser dekningen leser den for å vite hva som ble
undersøkt, og «i omfanget, men uleselig» er et svar på nettopp det.

Kolonnen vises bare når noe faktisk falt ut. En kolonne med null i hver rad i
hver kjøring blir ikke lest — samme vurdering som at unntak vises i raden
framfor i en egen liste.

*Alternativ vurdert:* alltid vise kolonnen, så fraværet av tall betyr noe. Men
kravet sier at det skal oppgis når alt lot seg tolke; en linje i oppsummeringen
dekker det uten en tom kolonne i hver rad.

### K2-meldingen får én setning, ikke en oppramsing

    Plasseringen «11508» har 5 siffer, forventet 6. Objektet er derfor ikke
    kontrollert av de øvrige kontrollene.

Ikke «hoppet over av K3, K4, K5, K6, K7, K8, K9». Numrene ville tatt plassen fra
selve feilen, og de endrer seg om en kontroll kommer til.

## Risks / Trade-offs

**Meldingen blir lengre, og K2 kan ha mange funn** → Setningen er kort og lik i
hver. I XLSX og CSV er den en kolonne; i BCF er den emnets beskrivelse. Verdt å
se på i rapporten før det kalles ferdig.

**Advarselen kan fyre på en fagmodell med ett eneste merket objekt** → Da er den
teknisk riktig og praktisk støy. Grensen «alle» er likevel den ærligste; en
terskel ville vært et tall uten begrunnelse.

**Et tredje tall i dekningstabellen** → Vises bare når det er noe å vise. Men
tabellen begynner å bli bred, og den skal leses i mørk modus på en skjerm.
