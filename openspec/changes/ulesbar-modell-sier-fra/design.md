## Context

Se proposal.md — Why.

Mønsteret finnes allerede i repoet. `OppsettFeil` reises i `config.py`, fanges i
`cli.py` og blir til `typer.BadParameter` — som gir exit 2, en melding med et
hint om hvilket flagg det gjelder, og ingen rapport. Denne endringen speiler det
for modellfiler.

Det som er nytt her, og som ikke fantes for oppsettet: lesingen skjer i en
**prosesspool**. `les_modeller` sender én fil per arbeider, og et unntak derfra
kommer tilbake gjennom `ProcessPoolExecutor` uten at noe sier hvilken fil som
reiste det.

## Goals / Non-Goals

**Goals:**

- Tre utfall — tom fil, ikke-IFC, avkuttet fil — gir samme slags svar: en
  melding med filnavnet, exit 2, ingen rapport.
- Filnavnet overlever prosessgrensen.

**Non-Goals:**

- Ikke reparere eller gjette på en halv fil. Verktøyet leser modeller; det
  fikser dem ikke.
- Ikke fortsette med de filene som gikk bra. Se avgjørelsen under.
- Ikke validere IFC-en utover å kunne lese den. Det finnes egne verktøy for
  skjemavalidering, og §3 avgrenser mot dem.
- Ikke røre `IfcObjekt` eller noe annet som krysser prosessgrensen som data.

## Decisions

### Én ny unntakstype, `ModellFeil`, ved siden av `OppsettFeil`

Reises i `ifc/loader.py`, fanges i `cli.py`, blir til `typer.BadParameter` med
`param_hint="modeller"`. Den bærer stien og en kort forklaring.

**Vurdert og forkastet:** å la `OSError` og ifcopenshells egne unntak boble opp
og bare fange dem i `cli.py`. Da måtte cli-en kjenne igjen unntakstypene til et
bibliotek den ellers ikke importerer, og den arkitektoniske regelen er at
`tfm_sjekk.ifc` er eneste modul som vet om ifcopenshell. Oversettelsen hører
hjemme der grensen går.

### Kjøringen stopper, den fortsetter ikke med resten

Er én av seks fagmodeller uleselig, stopper hele kjøringen.

Fristelsen er å hoppe over den ene og rapportere de fem — brukeren får da
*noe*. Men K6 leter etter komponentforekomster brukt i flere filer, og D3 etter
delt identitet på tvers. Uten den sjette fila ser et duplikat ut som en unik ID.
Rapporten ville vært **feil, ikke ufullstendig**, og ingenting i den ville
avslørt det.

Det er det samme valget som at en rute uten treff stopper med exit 2 framfor å
gi en tom, grønn rapport.

### Filnavnet legges på i arbeideren, ikke utledes i hovedprosessen

`_les_en` fanger og reiser `ModellFeil` med stien i seg. Unntaket pickles
tilbake med teksten i behold.

**Vurdert og forkastet:** å utlede fila av rekkefølgen på resultatene fra
`pool.map`. Den rekkefølgen finnes ikke når kartet avbrytes av et unntak.

`ModellFeil` må være picklebar — den arver `Exception` og bærer bare strenger,
så det holder. En test dekker det, fordi det er akkurat den slags som virker i
den sekvensielle veien og ryker i den parallelle. `les_modeller` går sekvensielt
under to filer, så en test med én fil ville aldri nådd prosesspoolen.

### Avkuttet fil kjennes igjen på avslutningsmarkøren, ikke på noe klokere

IFC-SPF krever `END-ISO-10303-21;` til slutt. Mangler den, er fila avkuttet.

Sjekken leser slutten av fila, ikke hele. Den koster ingenting og krever ingen
kunnskap om innholdet.

**Vurdert og forkastet:** å sammenligne objekttallet med noe forventet, eller å
advare når en fil er «mistenkelig liten». Begge krever et tall uten begrunnelse.
Avslutningsmarkøren er formatets eget krav, og en fil uten den er avkuttet etter
formatets egen definisjon — ikke etter vår vurdering.

**Merk:** dette fanger en fil som er kuttet på slutten, som er det en avbrutt
skriving gir. En fil der noe mangler i midten, men slutten er intakt, går
gjennom. Det er greit: den varianten krever at noen har redigert fila, ikke at
en overføring stoppet.

### Meldingen sier hva slags feil, ikke bare at det er en

Tre tekster, fordi de krever tre ulike handlinger:

    tom / kan ikke åpnes   →  finn fila igjen, eller sjekk rettighetene
    ikke IFC               →  sjekk at det er riktig fil og riktig format
    avkuttet               →  eksporter på nytt

## Risks / Trade-offs

**En fil ifcopenshell kan lese, men vi avviser** → Skriver noen en IFC uten
avslutningsmarkør og den ellers er komplett, stopper vi en kjøring som ville
gått. Markøren er obligatorisk i ISO 10303-21, så en fil uten den er ødelagt
etter formatets egen definisjon — men vi er strengere enn ifcopenshell er, og
det er verdt å vite om. Meldingen sier hva som mangler, så det er en
femsekunders diagnose framfor et mysterium.

**Exit 2 der noen kanskje forventer 1** → En CI-jobb skrevet som «alt annet enn
0 er avvisning» merker ingen forskjell. En som skiller på 1 vil nå se 2 på en
ødelagt fil. Det er hele hensikten, men det er en synlig endring for den som har
bygget noe rundt exit-koden.

**Federering stopper på én dårlig fil** → En koordinator med seks modeller der
den ene er halvlastet får ingen rapport i det hele tatt. Alternativet er en
rapport som er feil på en måte ingen kan se, og valget er tatt der før.
