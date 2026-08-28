## Context

Se proposal.md — Why.

Lesedelen er mekanisk: `ModellFeil` finnes fra 0.9.3, og `cli.py` gjør den
allerede til exit 2 uten rapport. Tabellene skal inn i samme mønster.

Skrivedelen er den som krever et valg. `cli.py` skriver i dag fire filer rett på
sine endelige stier:

    skrevet = [
        skriv_html(...),   ← ferdig
        skriv_csv(...),    ← ferdig
        skriv_xlsx(...),   ← krasjer her
        skriv_bcf(...),    ← kjøres aldri
    ]

Halvveis gjennom lista er to filer nye, én er ødelagt og én er fra forrige
runde. Ingenting i mappa sier hvilken som er hvilken.

## Goals / Non-Goals

**Goals:**

- Tabellfeil blir meldinger med exit 2, som modellfeil.
- Tabellene leses før modellene.
- Utmappa er enten helt ny eller helt urørt.
- En låst rapportfil gir en melding som nevner den vanligste årsaken.

**Non-Goals:**

- Ikke vente på at fila låses opp, og ikke prøve på nytt. Verktøyet er ikke en
  vaktprosess; det sier fra og lar brukeren lukke Excel.
- Ikke skrive til et alternativt filnavn — `funn (2).xlsx` løser låsen og lager
  en verre sak: to regneark fra ulike runder i samme mappe.
- Ikke røre innholdet i noen rapport. Dette handler om når filene treffer disken.

## Decisions

### Alt skrives til en midlertidig mappe, og flyttes på plass til slutt

Rapportene skrives til en midlertidig mappe **ved siden av** utmappa, og først
når alle fire er ferdige flyttes de på plass.

Feiler skrivingen, ryddes den midlertidige mappa bort og utmappa er urørt.

**Ved siden av, ikke i systemets temp-mappe.** `Path.replace` er atomisk
innenfor samme filsystem og faller tilbake på kopier-og-slett over
filsystemgrenser — og på Windows er temp ofte på en annen stasjon enn
prosjektmappa. Ved siden av er det garantert samme volum.

**Vurdert og forkastet:** å skrive til `.tmp`-navn i utmappa selv. Da må hver
skrivefunksjon kjenne mønsteret, og en avbrutt kjøring etterlater
`rapport.html.tmp` ved siden av rapporten. En egen mappe forsvinner i ett kall.

**Vurdert og forkastet:** å sjekke skrivetilgang på forhånd. Det er en
kappløpssituasjon — Excel kan åpne fila mellom sjekken og skrivingen — og et
forsøk som feiler er uansett det eneste sikre svaret.

### Flyttingen kan også feile, og da er det for sent

Er `funn.xlsx` låst, feiler ikke skrivingen til den midlertidige mappa; den
feiler når fila flyttes på plass. Da kan tre filer allerede være flyttet.

Derfor flyttes de **i motsatt rekkefølge av hvor sannsynlig det er at de er
låst**: regnearket først, så BCF-en, så CSV-en, så HTML-en. Regnearket er det
som står åpent i Excel, og BCF-en det som er importert i en viewer.

Det gjør vinduet lite, men ikke null, og det skal sies rett ut: **flyttingen er
ikke atomisk over fire filer.** Ingen enkel mekanisme gir det på Windows uten et
transaksjonslag vi ikke skal ha. Feiler den midt i, sier meldingen hvilken fil
det gjaldt, og at mappa nå kan inneholde filer fra to runder — det ene tilfellet
der verktøyet ikke kan holde løftet, og da skal det si det.

**Vurdert og forkastet:** å ta en sikkerhetskopi av utmappa først og rulle
tilbake. Det dobler skrivetiden på hver eneste kjøring for et tilfelle som
krever at en fil låses i vinduet mellom to flyttinger.

### Meldingen nevner Excel

    «funn.xlsx» kunne ikke skrives: tilgang nektet. Er fila åpen i et annet
    program? Lukk den og kjør på nytt. Ingen av rapportfilene er endret.

Den siste setningen er halve poenget. Uten den vet ikke brukeren om mappa er til
å stole på.

### Rettet under bygging: feilen måtte ut av `ifc/`

Designet sa «gjenbruk `ModellFeil`». Den ligger i `ifc/loader.py`, og en import
derfra i `tabeller/` ville dratt ifcopenshell inn i en modul som leser CSV — mot
regelen om at `ifc/` er eneste sted som vet om det biblioteket. `les_kodetabell`
ville i praksis krevd ifcopenshell installert.

Klassen ligger nå i `tfm_sjekk/feil.py`, fri for avhengigheter, og heter
**`FilFeil`**: «en fil verktøyet skulle lese eller skrive, og ikke kunne».
Navnet `ModellFeil` sto seg ikke når den samme typen skulle bære en kodetabell
og en rapportfil. Den er én utgave gammel og ikke en del av noe API andre
bruker.

Argumentet fra designet står: **én type, ikke tre.** Cli-en har nøyaktig én
utgang for dem, og tre typer med samme håndtering ville vært tre steder å
glemme én.

### Rettet under bygging: to `ValueError` til i mastera

`les_master` reiser to feil med gode meldinger — «fant ingen gjenkjennelig
kolonneoverskrift», «fant kolonneoverskriftene, men ingen verdier under dem».
Begge nådde brukeren som traceback med exit 1, akkurat som de andre. De er med.

### Tabellene leses først, og feilen er `ModellFeil`

Lesingen flyttes opp foran `les_modeller`, dit tidsstempelet allerede
valideres, og av samme grunn.

Unntakstypen gjenbrukes framfor en ny `TabellFeil`. Den heter riktignok
«Modell», men den betyr «en fil verktøyet skulle lese, og ikke kunne» — og
cli.py har allerede nøyaktig én utgang for det. To typer med samme håndtering
ville vært to steder å glemme.

## Risks / Trade-offs

**Diskbruk under skriving** → Rapportene finnes i to eksemplarer i det korte
vinduet før flyttingen. Snowdon-rapporten er under en megabyte; det er ikke et
problem i praksis, men det er en endring.

**En kjøring som avbrytes med Ctrl-C etterlater en midlertidig mappe** →
Den ryddes i en `finally`, men et hardt drept prosess rekker ikke det. Mappa får
et navn som sier hva den er, så den ikke ser ut som en rapport.

**Flyttingen er ikke atomisk over fire filer** → Se avgjørelsen over. Vinduet er
mindre enn i dag med god margin, og det ene tilfellet der løftet ikke holder blir
sagt fra om framfor å være taust.

**Tabeller leses før modellene** → En kjøring der både tabellen og en modell er
ødelagt melder nå tabellen først. Det er riktig rekkefølge — den oppdages på et
sekund framfor etter førtisju — men meldingen er en annen enn før.
