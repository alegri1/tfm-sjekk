## Context

Se `proposal.md` for hvorfor. Kravene står i `specs/dekning/spec.md`.

Tre ting i dagens kode former løsningen:

- `Kontekst.relevante_objekter()` beregner allerede omfanget, ved å matche
  `config.ifc_klasser` mot hele arvekjeden på hvert objekt. Tallet finnes; det er
  bare ingen som spør etter det.
- Alle funn er `Funn`, og rapportformatene rendrer den listen. Et funn uten
  GlobalId er allerede en etablert form — K7 og K8c bruker den for saker som
  gjelder modellen som helhet.
- CLI-en skriver «N objekter» og sender samme tall til HTML-en som «objekter
  kontrollert». Det tallet er antall *leste* objekter.

## Goals / Non-Goals

**Goals:**
- Fravær av funn skal være entydig: en ren rapport skal kunne skilles fra en
  kjøring som ikke undersøkte noe.
- Dekningen skal være synlig uten at noen leter etter den.

**Non-Goals:**
- Ingen endring i hva `ifc_klasser` inneholder eller hvordan omfanget beregnes.
  Denne endringen rapporterer om omfanget; den justerer det ikke.
- Ingen dekningsgrad per kontroll. At K3 hoppes over uten kodetabell rapporteres
  allerede, og det er en annen slags mangel.

## Decisions

### Dekningen er en kontroll, ikke et rapportfelt

Alternativet var å regne ut og vise tallet i rapportlaget. Det ble forkastet av tre
grunner:

Et funn arver hele maskineriet — det havner i BCF, HTML, XLSX og CSV uten at hvert
format må lære et nytt begrep, det kan slås av og få endret grad i `tfm-sjekk.toml`
som enhver annen kontroll, og det sorteres deterministisk sammen med resten.

Rapportlaget ville dessuten trengt en ny vei inn for et tall som ikke er et funn, og
BCF har ingen naturlig plass til noe slikt utenfor et emne.

Kontrollen er ikke en av K1–K9 i §4. Den kontrollerer ikke modellen, men kjøringen,
og bør navngis så det synes.

### Advarsel, ikke feil

Avgjort med brukeren. Exit-koden er porten i en leveranseprosess (§5), og verktøyet
står allerede i CI. Et legitimt kjør på en ARK-modell skal ikke begynne å feile av
en oppgradering.

Vurdert og forkastet: et `--krev-objekter N`-flagg. Det er eksplisitt og
ikke-brytende, men krever at noen kjenner flagget og velger et tall — og tallet er
vanskelig å velge fornuftig. Advarselen når alle uten at noen må vite om den.

### Per fagmodell

Avgjort med brukeren, og samme resonnement som K9 bruker for MMI: en federering av
RIE, RIV og ARK skal si fra om ARK-fila selv om kjøringen samlet har objekter nok.
Vurdert samlet ville nettopp det tilfellet man helst vil oppdage gått stille forbi.

`IfcObjekt.kildefil` bærer allerede filnavnet, så grupperingen er den samme som K9
gjør.

### Dekningstallet er to tall, ikke ett

Antall lest og antall i omfanget. Ett tall kan ikke uttrykke forskjellen mellom «412
objekter, ingen relevante» og «412 objekter, alle kontrollert», og det er nettopp
den forskjellen evnen finnes for.

HTML-ens «objekter kontrollert» er i dag antall leste objekter. Den etiketten er
misvisende og rettes samtidig.

## Risks / Trade-offs

**En advarsel som ingen leser er nesten like stille som ingenting** → Derfor kreves
dekningstallet i rapporten uansett utfall, ikke bare når omfanget er tomt. Advarselen
er påminnelsen; tallet er beviset.

**Støy i federeringer der tomme fagmodeller er normalt** → En arkitekt som alltid
kjører ARK sammen med RIE får en advarsel hver gang. Kontrollen kan slås av per
prosjekt i `tfm-sjekk.toml`, som enhver annen. Det er en bevisst handling, og det er
riktig nivå: den som slår den av vet hva den betyr.

**Et nytt funn endrer demoens fasit** → Golden-file-tester og demokjøringen må
oppdateres. Ingen risiko, men det berører flere tester enn selve endringen.

## Open Questions

- Bør dekningen også oppgis per IFC-klasse i fagmodellen, ikke bare totalt? Det ville
  gjort det lettere å se at *nesten* alt er i omfanget bortsett fra proxyene. Kan
  legges til senere uten å endre kravene her.
