## Purpose

Beskriver hva verktøyet sier om hvor mye av en modell det faktisk undersøkte.
Uten dette er fravær av funn tvetydig: det kan bety at alt er i orden, eller at
ingen kontroll hadde noe å se på. De to skal ikke se like ut i en rapport som
brukes som port i en leveranseprosess.

## Requirements

### Requirement: Rapporten sier hvor mye som ble sjekket

Verktøyet SKAL oppgi hvor mange objekter som var i omfanget, av hvor mange objekter
som ble lest, per fagmodell. Tallet SKAL oppgis også når det ikke er funnet noe å
melde.

Et dekningstall som bare vises når noe er galt er verdiløst: det er nettopp den rene
rapporten en leser trenger å kunne stole på.

#### Scenario: Dekningen oppgis ved en ren kjøring
- **WHEN** en fagmodell er kontrollert uten funn
- **THEN** rapporten oppgir antall objekter i omfanget og antall objekter lest for
  den fagmodellen

#### Scenario: Dekningen oppgis per fagmodell ved federering
- **WHEN** flere fagmodeller kontrolleres i samme kjøring
- **THEN** dekningen oppgis for hver av dem, ikke bare samlet

### Requirement: Tomt omfang i en fagmodell gir et funn

Når ingen av objektene i en fagmodell er i omfanget, SKAL verktøyet melde det som
et funn med grad advarsel — **med mindre fagmodellen er unntatt med vilje** i
oppsettet.

Vurderingen SKAL gjøres per fagmodell. En federering der én fil er uten tekniske
fag er nettopp tilfellet som ellers går stille forbi, og det er den fila funnet
skal peke på.

Unntaket er nødvendig fordi funnet ellers mister sin verdi. Et prosjekt som med
vilje federerer inn ARK og RIB for kontrollene på tvers, ville fått en advarsel
per fil hver eneste kjøring — og en advarsel som alltid står der leses ikke.
Funnet skal fortsatt fyre når dekningen mangler ved en forglemmelse; det er
forskjellen mellom de to som nå kan uttrykkes.

#### Scenario: Ingen objekter i omfanget
- **WHEN** en fagmodell er lest, men ingen av objektene er i noen av de konfigurerte
  IFC-klassene
- **THEN** rapporten inneholder et funn med grad advarsel om at ingenting ble
  kontrollert i den fagmodellen

#### Scenario: Én tom fagmodell blant flere
- **WHEN** en kjøring omfatter tre fagmodeller, og bare én av dem har null objekter
  i omfanget
- **THEN** funnet gjelder den ene fagmodellen
- **AND** de to andre gir ikke funn om dekning

#### Scenario: Modell uten objekter i det hele tatt
- **WHEN** en fil ikke inneholder noen objekter verktøyet leser
- **THEN** rapporten sier fra om det på samme måte

#### Scenario: Fagmodellen er unntatt med vilje
- **WHEN** oppsettet gir en fagmodell et tomt sett IFC-klasser
- **THEN** rapporten melder ikke manglende dekning for den fagmodellen

### Requirement: Tomt omfang endrer ikke exit-koden

Et funn om tomt omfang SKAL ha grad advarsel og SKAL ikke gjøre exit-koden ulik
null alene.

Verktøyet står allerede som port i CI hos den som bruker det, og et legitimt kjør
på en modell uten tekniske fag skal ikke begynne å feile. Advarsler teller ikke mot
exit-koden (§5), og det er derfor graden er den riktige.

#### Scenario: Ren modell med tomt omfang
- **WHEN** en kjøring gir null feil, men et funn om tomt omfang
- **THEN** exit-koden er 0

#### Scenario: Tomt omfang sammen med ekte feil
- **WHEN** en kjøring har både et funn om tomt omfang i én fagmodell og minst én
  feil i en annen
- **THEN** exit-koden er 1, slik feilen alene ville gitt

### Requirement: Funnet peker på årsaken

Funnet om tomt omfang SKAL nevne hvilken innstilling som avgjør omfanget, og hvilke
IFC-klasser fagmodellen faktisk inneholder.

Den som leser rapporten skal kunne rette konfigurasjonen ut fra meldingen alene.
Uten klassene fila inneholder er beskjeden «ingenting ble sjekket» uten anvisning.

#### Scenario: Meldingen navngir innstillingen og klassene
- **WHEN** en fagmodell med bare `IfcWall` og `IfcSlab` gir tomt omfang
- **THEN** meldingen nevner innstillingen som styrer omfanget
- **AND** den nevner klassene som faktisk finnes i fagmodellen

### Requirement: Antall leste objekter skiller seg fra antall i omfanget

Der verktøyet i dag oppgir «objekter kontrollert», SKAL det skilles mellom antall
objekter som ble lest fra fila og antall som var i omfanget for kontrollene.

Dagens tall er antall leste objekter, presentert som om det var antall
kontrollerte. Nettopp den forskjellen er det denne evnen finnes for.

#### Scenario: Tallene er ulike og begge oppgis
- **WHEN** en fagmodell har 412 leste objekter og 0 i omfanget
- **THEN** rapporten oppgir begge tallene
- **AND** den framstiller ikke 412 som antall kontrollerte objekter

### Requirement: En hoppet kontroll skal si hvorfor den ikke kjørte

Oppgir verktøyet at en kontroll ble hoppet over, SKAL det oppgi årsaken. Årsaken
SKAL skille mellom at kontrollen er slått av i oppsettet, at data den krever
mangler, og at den ikke er implementert ennå.

Årsaken SKAL følge med både til konsollen og til rapporten.

De tre er motsatte handlinger for den som leser: la det være, skaff dataene,
vent på en senere utgave. Ordet «hoppet over» alene sier ikke hvilken, og en
kontroll som aldri kjørte er verre enn en fagmodell uten objekter i omfanget —
den så ikke engang etter.

#### Scenario: Kontrollen mangler data
- **WHEN** en kontroll krever en kodetabell eller en TFM-master som ikke er
  oppgitt
- **THEN** oppgis det at kontrollen ble hoppet over fordi dataene mangler

#### Scenario: Kontrollen er slått av
- **WHEN** en kontroll er slått av i oppsettet
- **THEN** oppgis det at den ble slått av, ikke at data mangler

#### Scenario: Årsaken står også i rapporten
- **WHEN** en kjøring hopper over en kontroll
- **THEN** oppgir rapporten den samme årsaken som konsollen

### Requirement: Årsaken skal si hva som skal til

Mangler en kontroll data, SKAL meldingen navngi både kommandolinjeflagget og
nøkkelen i oppsettet som kan skaffe dem.

Meldingene i dette verktøyet leses av en BIM-koordinator, ikke av en utvikler.
Forskjellen mellom «mangler systemtabell» og «oppgi --systemtabell, eller
«systemtabell» i oppsettet» er forskjellen mellom å lete i dokumentasjonen og å
rette én linje — samme grunn som at en ukjent nøkkel foreslår den nærmeste
gyldige.

#### Scenario: Meldingen navngir flagget og nøkkelen
- **WHEN** en kontroll hoppes over fordi en kodetabell mangler
- **THEN** nevner meldingen flagget som oppgir tabellen
- **AND** den nevner nøkkelen som gjør det samme i oppsettet

### Requirement: Objekter med uleselig TFM skal telles

Verktøyet SKAL oppgi hvor mange objekter i omfanget som har en TFM-verdi som
ikke lot seg tolke. Tallet SKAL oppgis per fagmodell, ved siden av dekningen.

Et objekt med uleselig TFM er lest, det er i omfanget, og det er likevel ikke
kontrollert av de kontrollene som krever en tolket ID. Uten tallet ser en slik
fagmodell like undersøkt ut som en der alt ble kontrollert.

Dette er samme tvetydighet som evnen ellers finnes for å fjerne, én etasje inn:
dekningen svarer på om objektet var i omfanget, ikke på om det var lesbart nok
til å bli kontrollert.

#### Scenario: Noen objekter har uleselig TFM
- **WHEN** en fagmodell har objekter i omfanget der TFM-verdien ikke lar seg
  tolke
- **THEN** oppgir rapporten hvor mange det gjelder for den fagmodellen

#### Scenario: Alt lot seg tolke
- **WHEN** alle objektene i omfanget har en TFM som lot seg tolke
- **THEN** oppgis det, slik at fravær av tallet ikke må tolkes

### Requirement: Meldingen om syntaksfeil skal si hva den koster

Meldingen om at en TFM-verdi ikke følger grammatikken SKAL si at objektet
dermed ikke er kontrollert av de øvrige kontrollene.

Meldingen sier i dag hva som er galt med strengen. Den sier ikke at objektet
samtidig er uunderøkt for ukjent systemkode, duplisert forekomst, master-avvik
og kursnummer. Den som leser rapporten skal kunne se at et syntaksfunn skjuler
mer enn det viser.

#### Scenario: Meldingen nevner konsekvensen
- **WHEN** et objekt får et funn om at TFM-verdien ikke følger grammatikken
- **THEN** sier meldingen også at objektet ikke er kontrollert av de øvrige
  kontrollene

### Requirement: En fagmodell der alt faller ut skal meldes særskilt

Er det ingen objekter i omfanget som har en tolkbar TFM, mens fagmodellen har
objekter med TFM-verdi, SKAL verktøyet melde det som et eget funn med grad
advarsel.

Enkeltfeil rettes objekt for objekt. Faller alt ut, er det ikke enkeltfeil —
det er en merkekonvensjon som ikke stemmer med grammatikken i oppsettet, og
handlingen er å se på oppsettet framfor på modellen. De to skal ikke se like ut.

Funnet SKAL nevne innstillingen som avgjør grammatikken, på samme måte som
funnet om tomt omfang navngir innstillingen som avgjør omfanget.

#### Scenario: Ingen TFM-verdi lot seg tolke
- **WHEN** en fagmodell har objekter med TFM-verdi i omfanget, og ingen av dem
  lot seg tolke
- **THEN** meldes det som et funn med grad advarsel
- **AND** meldingen nevner innstillingen som avgjør grammatikken

#### Scenario: Noen lot seg tolke
- **WHEN** minst ett objekt i fagmodellen har en tolkbar TFM
- **THEN** meldes det ikke som en konvensjonsfeil
- **AND** de enkelte syntaksfunnene meldes som før

#### Scenario: Ingen objekter har TFM i det hele tatt
- **WHEN** ingen objekter i fagmodellen har en TFM-verdi
- **THEN** meldes det ikke som en konvensjonsfeil
- **AND** fraværet meldes som før, av kontrollen for manglende TFM

### Requirement: Samme objektidentitet i flere fagmodeller skal meldes

Går samme IFC-identitet igjen blant objekter i omfanget, SKAL verktøyet melde
det som et funn med grad advarsel. Det gjelder både når identiteten går igjen i
flere fagmodeller og når den går igjen flere ganger i samme fil.

Identiteten brukes til å feste et funn til en fil og til å bære parseresultatet.
Er den ikke entydig, peker funn på vilkårlige filer, og to objekter deler ett
parseresultat. Undersøkelsen er da gjort, men resultatet er ikke til å stole på —
og det er et annet tilfelle enn at noe ikke ble undersøkt.

Innenfor én fil er følgen verre enn på tvers. To objekter med hver sin TFM-verdi
får ett felles parseresultat, og verktøyet melder da et duplikat som ikke finnes
i modellen — et funn som er usant, ikke bare upresist.

Funnet SKAL navngi fagmodellene og hvor mange objekter det gjelder, og si at
fil-tilhørigheten i de øvrige funnene er upålitelig for dem.

De to tilfellene SKAL skilles i meldingen. De krever ulik handling: samme modell
sendt inn to ganger fjernes fra kjøringen, mens en fil som bryter IFC-kravet om
unikhet må eksporteres på nytt.

#### Scenario: Samme modell er sendt inn to ganger
- **WHEN** to fagmodeller inneholder objekter i omfanget med samme identitet
- **THEN** meldes det som et funn med grad advarsel
- **AND** funnet navngir fagmodellene og antallet

#### Scenario: Samme identitet to ganger i én fil
- **WHEN** én fagmodell inneholder to objekter i omfanget med samme identitet
- **THEN** meldes det som et funn med grad advarsel
- **AND** navngir funnet fila og antallet
- **AND** sier meldingen at fila bryter IFC-kravet om unik identitet

#### Scenario: De to tilfellene ser ulike ut
- **WHEN** en kjøring har både en identitet delt mellom to filer og en identitet
  som går igjen i én fil
- **THEN** er de to funnene ulike, og hvert av dem sier hva som skal gjøres

#### Scenario: Hver identitet finnes bare ett sted
- **WHEN** ingen identitet i omfanget går igjen
- **THEN** meldes det ikke

### Requirement: Delte objekter utenfor omfanget skal ikke meldes

Går en identitet igjen bare på objekter som ikke er i omfanget, SKAL det ikke
meldes.

Lenkede eksporter fra Revit legger delte objekter — rutenett, romlig struktur —
inn i hver fil. Det er normalt og uten følger: objektene kontrolleres ikke, og
ingen funn festes til dem. En advarsel her ville stått i hver eneste federerte
kjøring og sluttet å bli lest.

#### Scenario: Et delt rutenett i flere fagmodeller
- **WHEN** flere fagmodeller inneholder samme objekt utenfor omfanget
- **THEN** meldes det ikke

### Requirement: Verktøyet skal ikke velge mellom like identiteter

Verktøyet SKAL IKKE slå sammen, forkaste eller på annen måte velge mellom
objekter som deler identitet.

Hvilket av to like objekter som er det rette, kan bare den som sendte inn filene
svare på. Å velge ett ville gjort en tvetydighet til et svar, og resultatet ville
sett like rent ut som en riktig kjøring.

#### Scenario: Begge objektene blir stående
- **WHEN** to fagmodeller deler et objekt i omfanget
- **THEN** telles begge i dekningen for hver sin fagmodell

### Requirement: Oppsummeringen skal telle alle gradene den fant

Oppsummeringen av en kjøring SKAL oppgi antallet for hver alvorlighetsgrad som
forekommer blant funnene. En grad uten funn SKAL ikke nevnes.

Antallene SKAL stemme med rapportene: summen av gradene i oppsummeringen er
antallet funn i rapportfilene.

Oppsummeringen står to steder — i konsollen og øverst i rapporten — og de to
SKAL bruke de samme ordene om de samme tallene.

Oppsummeringen er det første og ofte det eneste den som kjørte verktøyet leser.
Nevner den bare to av tre grader, har leseren ingen måte å vite at det ligger
flere rader i rapporten — og et funn ingen vet om er like usynlig som et funn
som aldri ble meldt.

Gradene som ikke avgjør exit-koden er ikke mindre verdt å vite om. En advarsel
og et infofunn endrer ikke porten, men de er nettopp de funnene som ellers går
ubemerket forbi.

#### Scenario: Kjøringen har funn av alle tre grader
- **WHEN** en kjøring gir 13 feil, 1 advarsel og 3 infofunn
- **THEN** oppgir oppsummeringen alle tre tallene
- **AND** summen av dem er antallet funn i rapporten

#### Scenario: En grad har ingen funn
- **WHEN** en kjøring gir feil, men ingen infofunn
- **THEN** nevner oppsummeringen ikke infofunn

#### Scenario: Entall og flertall
- **WHEN** en grad har nøyaktig ett funn
- **THEN** står ordet for den graden i entall
- **AND** står det likt i konsollen og i rapporten

#### Scenario: Ingen funn i det hele tatt
- **WHEN** en kjøring gir ingen funn av noen grad
- **THEN** sier oppsummeringen at det ikke ble funnet noe
- **AND** ramser den ikke opp gradene med null

### Requirement: Oppsummeringen skal navngi hver fil kjøringen skrev

Oppsummeringen SKAL navngi hver rapportfil kjøringen skrev, ikke et utvalg av
dem.

Stiene SKAL skrives med plattformens eget skilletegn hele veien.

En bruker som ikke vet at et format finnes, leter ikke etter det. Navngir linja
to av fire filer, er de to andre skrevet til ingen — og et regneark som ligger
usett ved siden av rapporten er samme slags stille tap som et utelatt funn.

#### Scenario: Alle skrevne filer navngis
- **WHEN** en kjøring skriver en HTML-rapport, en CSV, et regneark og en BCF
- **THEN** navngir oppsummeringen alle fire

#### Scenario: Stien er skrevet i plattformens form
- **WHEN** en sti oppgis i oppsummeringen
- **THEN** bruker hele stien det samme skilletegnet

### Requirement: Et duplikat som skyldes delt identitet skal ikke meldes som en merkefeil

Deler to objekter i omfanget identitet, SKAL verktøyet ikke melde en
komponentforekomst som brukt flere ganger når det bare er parseresultatet de
deler.

To objekter med hver sin TFM-verdi er ikke et duplikat. Meldes de som ett, får
den som skal rette modellen beskjed om å finne to like TFM-er som ikke finnes —
og den ene av de to verdiene blir aldri kontrollert.

#### Scenario: To ulike TFM-verdier på samme identitet
- **WHEN** to objekter i samme fil har samme identitet og hver sin TFM-verdi
- **THEN** meldes det ikke at en komponentforekomst er brukt på to objekter
- **AND** meldes den delte identiteten i stedet

### Requirement: Alle kommandoer som leser modeller skal si fra på samme måte

Kan ikke en modellfil leses, SKAL enhver kommando som leser modeller svare på
den samme måten: en melding, og koden som betyr at kjøringen ikke kunne
gjennomføres.

Kravet ble innført for kontrollkjøringen. En kommando som leser de samme filene
og svarer annerledes på den samme fila, er en kommando som lyver om verktøyet.

#### Scenario: Oppsettforslag på en ødelagt fil
- **WHEN** kommandoen som foreslår et oppsett får en fil som ikke lar seg lese
- **THEN** gir den en melding og den samme exit-koden som kontrollkjøringen
- **AND** vises ingen traceback
