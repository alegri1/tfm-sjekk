## Context

Se proposal.md — Why.

`delt_identitet` grupperer på GlobalId og melder de identitetene som finnes i
mer enn én fil. Innenfor én fil teller den ikke, og docstringen sier hvorfor:
IFC krever unikhet der, så det er «en annen sak».

Den saken er ikke tatt, og `_etter_id` og `parsede` er begge nøklet på GlobalId
alene. To objekter i samme fil kollapser derfor stille, og K6 melder et duplikat
som ikke finnes.

## Goals / Non-Goals

**Goals:**

- Duplikat identitet innenfor én fil meldes, med en melding som skiller seg fra
  den om flere filer.
- K6 melder ikke et duplikat som bare er to objekter som deler parseresultat.
- `tfm-sjekk oppsett` svarer som `tfm-sjekk sjekk` på en ødelagt fil.

**Non-Goals:**

- Ikke bytte nøkkelen i `_etter_id` til `(kildefil, global_id)`. Se avgjørelsen
  under — argumentet fra D3 står, og en sammensatt nøkkel løser ikke dette.
- Ikke velge hvilket av to objekter som er «det rette». Verktøyet gjetter ikke;
  det sier at fila må eksporteres på nytt.
- Ikke validere IFC-filen for øvrig. §3 avgrenser mot skjemavalidering.

## Decisions

### `delt_identitet` teller forekomster, ikke filer

I dag returnerer den `{global_id: [filer]}` og filtrerer på `len(filer) > 1`.
Den skal i stedet bære nok til å skille de to tilfellene: hvilke filer, og hvor
mange objekter.

Et duplikat innenfor én fil har `len(filer) == 1` og `antall > 1`. Et duplikat
på tvers har `len(filer) > 1`. Begge er «identiteten er ikke entydig», og D3
melder dem hver for seg.

**Vurdert og forkastet:** en egen `D4` for tilfellet i én fil. D3 svarer allerede
på spørsmålet «er resultatet til å stole på?», og det er samme spørsmål her. To
kontroller som svarer på det samme ville tvunget leseren til å lære forskjellen
på dem uten at det finnes en.

### Nøkkelen i `_etter_id` blir stående

Fristelsen er å bytte til `(kildefil, global_id)` og la problemet forsvinne. Det
gjør det ikke: innenfor én fil er den sammensatte nøkkelen den samme nøkkelen.

Argumentet fra D3 gjelder fortsatt, og det er hele grunnen til at verktøyet
melder framfor å velge: to objekter med samme ID er enten ETT objekt telt to
ganger, eller to objekter som ved en feil deler ID. Ingen nøkkel svarer på det.

### K6 tier om objekter med delt identitet

K6 leter etter komponentforekomster brukt flere ganger. Grunnlaget er
`med_tfm()`, som parer objekter med parseresultat på GlobalId — og der to
objekter deler identitet er den paringen feil.

K6 hopper derfor over de identitetene D3 har meldt. Det er ikke å skjule et
funn: et ekte duplikat mellom to objekter som *har* hver sin identitet meldes
fortsatt, og D3 sier hvorfor de andre ikke ble undersøkt.

**Vurdert og forkastet:** å la K6 melde som før og stole på at D3-advarselen
forklarer det. Et `feil`-funn med en oppdiktet TFM-verdi er ikke noe en advarsel
lenger nede redder. Den som leser rapporten leser feilene først, og de skal
være sanne.

### Meldingen skiller de to tilfellene

    flere filer   samme modell er sendt inn to ganger  →  fjern den ene fila
    én fil        fila bryter IFC-kravet om unikhet    →  eksporter på nytt

To ulike handlinger. En felles melding ville tvunget leseren til å finne ut selv
hvilken av dem som gjelder — og det er nøyaktig den jobben «hoppet over — tre
årsaker, ett ord» handlet om.

### `oppsett` bruker den samme `_som_brukerfeil`

En linje. Den ble glemt i 0.9.3 fordi jeg rettet stedet feilen viste seg, ikke
alle stedene funksjonen kalles. En test dekker den nå, så neste kommando som
leser modeller ikke kan glippe like stille.

## Risks / Trade-offs

**K6 tier om noe den før meldte** → En fil med duplikat identitet og et ekte
TFM-duplikat mellom nettopp de objektene får ikke K6-funnet. D3 melder at de
ikke ble undersøkt, så det er ikke stille — men det er en kontroll som ser
mindre enn før i akkurat det tilfellet. Alternativet er å melde noe usant.

**Advarsel, ikke feil** → En fil som bryter IFC-kravet om unik identitet stenger
ikke porten. Det er samme valg som for D3, og av samme grunn: exit-koden avgjøres
av merkingen, og dette er en eksportfeil. K1–K9 melder fortsatt det de finner på
objektene.

**Ingen ekte fil å prøve mot** → Duplikat GlobalId er konstruert her ved å
redigere en fikstur. Snowdon har ingen. At det forekommer i praksis er noe jeg
har lest, ikke noe jeg har sett i denne mappa, og det skal stå i tasks.md så det
ikke leses som mer enn det er.
