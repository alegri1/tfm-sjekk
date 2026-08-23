## Context

Se proposal.md — Why.

`config.py` har sju pydantic-modeller: `Grammatikk`, `PsetOppsett`,
`MmiOppsett`, `ElektroOppsett`, `MasterOppsett`, `KontrollOppsett` og
`Konfigurasjon`. Ingen av dem setter `extra`, så pydantics standard gjelder:
ukjente nøkler forkastes uten et ord.

`Konfigurasjon.les(sti)` leser TOML-en og bygger modellen. CLI-en kaller den, og
har allerede et mønster for oppsettfeil: en sti som peker feil blir
`typer.BadParameter` og exit 2.

`kontroller` er `dict[str, KontrollOppsett]`. Nøklene der er kontroll-ID-er —
`K4`, `K8` — og de er ikke en fast liste. `extra="forbid"` på `KontrollOppsett`
rører ikke det: det er verdiene i ordboka som er modeller, ikke nøklene.

## Goals / Non-Goals

**Goals:**

- En konfigurasjon som ikke ble forstått skal stoppe kjøringen, ikke endre den
  i stillhet.
- Meldingen skal si hva som er galt og hvor, på norsk, uten at brukeren må
  kjenne pydantic.

**Non-Goals:**

- Å validere *verdier* strengere. `foring_klasser = ["IfcFinnesIkke"]` er
  fortsatt lov og fortsatt ufarlig — et klassenavn som ikke finnes i skjemaet
  treffer aldri noe. Det er nøkler dette handler om.
- Å innføre en versjonsnøkkel i fila. Se avveiningen under.
- Å røre `oppsett`-kommandoen. Fila den skriver skal fortsatt leses, og det
  er en prøve, ikke en endring.

## Decisions

### Stopp, ikke advar

En advarsel er mildere, og den koster ikke noe å overse. Verktøyet skriver
allerede flere linjer til stderr under en kjøring, og en linje til blant dem er
ikke et vern.

Det avgjørende er hva som skjer *etterpå*. Med en advarsel fortsetter kjøringen
og produserer en rapport laget med standardverdier der brukeren hadde skrevet
noe annet. Rapporten er da gal på en måte ingen kan se — og den blir delt i
Teams. Med en stopp får du ingen rapport, og du vet hvorfor.

Presedensen står allerede i `oppsettfunn`: en sti som peker feil stopper
kjøringen framfor å la kontrollen hoppe over, «fordi brukeren ville trodd hun
kjørte med master og fått en rapport uten K7-funn som ser ren ut». Det er samme
setning, ett nivå ned.

### `extra="forbid"` på alle sju, ikke bare på `Konfigurasjon`

Settes den bare på toppnivå, fanges `tfm_mastr` men ikke `foring_systemkode` i
`[elektro]` — og seksjonene er der de fleste nøklene bor.

Bivirkningen er at en feilstavet seksjon også fanges, siden `[elektrp]` blir en
ukjent nøkkel på toppnivå. Det er ønsket: for den som skrev fila er de tre
feilene den samme feilen.

### Oversettelse framfor pydantics egen tekst

`ValidationError` gir «Extra inputs are not permitted» med en feltsti og en
`input_value`. Det sier hverken hva som er galt eller hva det skulle stått, og
det er engelsk i et verktøy der alt annet er norsk.

Feilen fanges i `Konfigurasjon.les` og oversettes. Forslaget om nærmeste nøkkel
kommer fra `difflib.get_close_matches` mot modellens egne feltnavn — de er
tilgjengelige på `model_fields`, så lista kan ikke drive fra modellen.

`difflib` ligger i standardbiblioteket. §6 sier at binæren skal være til å
distribuere, og hver avhengighet koster megabyte; dette koster ingen.

## Risks / Trade-offs

**En konfigurasjon skrevet for en nyere utgave stopper et eldre verktøy** →
Reell, og den er ikke gratis. Skriver et prosjekt `foring_systemkoder` i fila
si, vil en kollega med `v0.5.0` nå få en stopp der hen før fikk en kjøring.

Motargumentet er at kjøringen aldri var riktig: den gamle utgaven kjente ikke
regelen, så rapporten var laget på andre premisser uansett. Forskjellen er bare
om brukeren fikk vite det. En stopp med «Ukjent nøkkel «foring_systemkoder»»
peker rett på at verktøyet er for gammelt; en stille kjøring gjør ikke det.

Vi tar den kostnaden med åpne øyne. Blir den et problem i praksis, er svaret en
versjonsnøkkel i fila — ikke å gå tilbake til taushet.

**Fila `oppsett` skriver må fortsatt leses** → Den skrev en gang `ifc_klasser`
etter `[pset]`, og med dette kravet ville den fila stoppet kjøringen. Feilen er
rettet, og en test kjører allerede forslaget gjennom `--config`. Den testen blir
strengere av seg selv nå, uten at noe må legges til.

**Repoets egen `tfm-sjekk.toml` må fortsatt leses** → Den er både dokumentasjon
og oppsett, og den brukes i CI-røyktesten og i demomappa. En egen test på at
akkurat den fila leses uten innsigelse er billig og fanger en hel klasse feil.
