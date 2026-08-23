## Context

Se proposal.md — Why. Kort om dagens tilstand:

`Funn` har to felter. `tfm` er objektets egen TFM-forekomstverdi, satt av
`for_objekt` og aldri av kontrollene. `verdi` er verdien funnet handler om, og
kan overstyres — i dag gjør bare K9 det, med MMI-verdien.

Fire rapportformater leser dem:

| Format | Bruker i dag | Etikett |
|---|---|---|
| CSV | `tfm` og `verdi` | `tfm`, `verdi` |
| XLSX | `tfm` og `verdi` | «TFM», «TFM-verdi» |
| HTML | bare `verdi` | «TFM-verdi» |
| BCF | bare `verdi` | «TFM-verdi:» |

De to nederste er de feilmerkede. Begge har ett innsettingspunkt hver:
kolonnedefinisjonen i HTML-malen, og `_detaljer` i BCF-skriveren.

## Goals / Non-Goals

**Goals:**

- Etiketten stemmer med innholdet i alle fire formater.
- Hver rad og hvert emne identifiserer objektet sitt, også når kontrollen melder
  om noe annet enn TFM.

**Non-Goals:**

- Å endre `Funn.verdi`, kontrollene eller CSV/XLSX. De er riktige i dag.
- Å gi HTML-tabellen en GlobalId-kolonne. TFM-verdien er den nøkkelen mennesker
  bruker; GlobalId er for maskiner, og den står allerede i CSV og XLSX.
- Å la K9 slutte å legge MMI-verdien i `verdi`. Den gjør det med rette — feilen
  ligger i hva rapportene kaller feltet.

## Decisions

### Bytte kolonnens innhold framfor å legge til en kolonne

HTML-kolonnen «TFM-verdi» blir «TFM» og fylles fra `f.tfm`.

Alternativet var å beholde verdikolonnen og legge til en TFM-kolonne, slik CSV og
XLSX har begge. Det ble valgt bort fordi HTML-rapporten allerede viser hele
meldinga, og meldinga inneholder verdien funnet handler om — K9 skriver «MMI
«200» avviker fra resten av systemet …». En egen verdikolonne ville gjentatt
«200» i samme rad. Sju kolonner der seks holder, i en tabell som skal leses på én
skjerm og deles i Teams.

Konsekvensen er at HTML og CSV ikke lenger har samme kolonnesett. Det er greit:
kravet om like felter gjelder formatene som behandles videre, og HTML er ikke ett
av dem. Formatene skal ikke ha samme *kolonner* — de skal ikke lyve om dem.

Sorteringen i HTML-malen peker på kolonneindeks. Kolonnen bytter innhold, ikke
plass, så indeksen er uendret. Det er verdt å merke seg nettopp fordi det er
lett å «rydde» i en slik endring og flytte kolonnen samtidig.

### BCF får «TFM», ikke «TFM-verdi»

`_detaljer` bygger en kommentar av «Kontroll · Alvorlighet · Fil · IFC-klasse ·
TFM-verdi». Siste ledd bytter kilde og etikett.

Verdien funnet handler om står i `Description`, som viewerne viser i sin helhet.
Emnet mister altså ingenting.

Alternativet var å la BCF være. Begrunnelsen fra sist — «den peker på objekter
med GlobalId og trenger ingen tekstnøkkel» — holder for kobling, og BCF-en kobler
riktig i dag. Men emnet leses også som tekst, og eksporteres til rapporter der
viewpointet ikke følger med. Da er «TFM-verdi: 200» det eneste som står igjen.

### Tomt felt, ikke «None»

Begge steder må tomt håndteres uttrykkelig. HTML-malen har allerede
`{{ f.verdi or '' }}` og beholder mønsteret; `_detaljer` har allerede en
`if f.verdi`-test som blir `if f.tfm`.

Det er ikke pedanteri: `f.tfm` er tom for K1 (objektet mangler TFM) og for K7s
meldinger om mastera. K1 er den kontrollen som melder *nettopp* at verdien
mangler, og en rad som viser «None» der ville motsi sin egen melding.

### Prøven hviler på ett enkelt funn

I hele demoen er det nøyaktig ett funn der `tfm` og `verdi` er ulike: K9-avviket
på `IfcOutlet` i `demo-elektro.ifc`. For de andre seksten er de like, og en test
mot dem ville passere både før og etter endringen.

Testene skal derfor ikke bare kontrollere at feltet finnes, men at det for et
K9-funn inneholder TFM-verdien og **ikke** MMI-verdien. En test som bare sjekker
at kolonnen er utfylt, beviser ingenting her.

Enhetstestene bygger sine egne `Funn` med ulik `tfm` og `verdi` framfor å hvile
på demomodellen. Demoen er en fikstur som endres når den utvides — det har skjedd
før i dette repoet — og et krav om at to felter skal skilles bør ikke kunne
brekke fordi noen la til et objekt.

## Risks / Trade-offs

**HTML og CSV får ulike kolonnesett** → Bevisst, og begrunnet over. Risikoen er
at noen leser HTML-tabellen som en visning av CSV-en. Kolonnen heter «TFM» i
begge, og betyr det samme i begge; det er verdikolonnen som bare finnes i CSV.

**Verdien funnet handler om blir bare synlig i meldinga i HTML og BCF** → Den er
allerede der, i alle meldinger, formulert av kontrollen som meldte. Mister vi
den, mister vi den fra meldinga, og det er en større feil som ville fanges av
langt flere tester.

**Endringen ser triviell ut og kan bli gjort uten test** → To linjer i to filer,
og begge passerer enhver eksisterende test. Nettopp derfor står prøven i egne
oppgaver, og nettopp derfor må den skille K9 fra resten.
