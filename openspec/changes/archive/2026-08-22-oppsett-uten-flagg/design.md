## Context

Se `proposal.md` for hvorfor. Det som former løsningen er at
`Konfigurasjon.les(sti)` i dag tar imot en sti eller `None`, og ved `None` gir
standardverdiene. Den vet ingenting om hvor den kom fra.

Det er nettopp det som må endres: så snart fila kan holde *stier*, må objektet
huske hvor det selv ble lest fra, ellers kan ikke en relativ sti tolkes.

## Goals / Non-Goals

**Mål:**
- `tfm-sjekk sjekk modell.ifc` skal være hele kommandoen i et oppsatt prosjekt.
- Ingenting skal virke i det skjulte: kjøringen sier hvilken fil den leste.
- En sti som peker feil skal stoppe kjøringen, ikke stille slå av en kontroll.

**Ikke mål:**
- Søk oppover i mappetreet. To steder er nok, og de er begge til å peke på i en
  setning. Et søk som går oppover kan plukke opp en fil langt unna, og da er
  «hvilken fil ble lest» ikke lenger et spørsmål man kan svare på uten å kjøre.
- Miljøvariabler eller et globalt oppsett i hjemmemappa. Oppsettet hører til
  prosjektet, ikke til maskinen.
- Å endre hva kontrollene gjør når en tabell mangler helt.

## Decisions

### `Konfigurasjon` husker hvor den ble lest fra

Et felt `kilde: Path | None` settes av `les()`. Stiene til master og tabeller
løses mot `kilde.parent` når de er relative.

Uten det måtte hver bruker av konfigurasjonen få stien sendt med ved siden av, og
den koblingen ville før eller siden glippet ett sted. Objektet som bærer stiene
skal bære opphavet sitt.

*Vurdert og forkastet:* å løse stiene til absolutte allerede i `les()`. Da hadde
ikke feltet trengtes — men konfigurasjonen ville ikke lenger vært det fila sa, og
en feilmelding kunne ikke gjengi stien slik brukeren skrev den.

### Oppslaget er to steder, i rekkefølge

Modellens mappe, så arbeidskatalogen. Første treff vinner.

Rekkefølgen følger av hvor brukeren er. Ved dra-og-slipp er arbeidskatalogen
programmets egen mappe, som ikke har med prosjektet å gjøre — det er samme
innsikt som allerede ligger bak `_med_rapportmappe`, som legger rapporten hos
modellen og ikke hos exe-en.

### Kjøringen sier hvilket oppsett den leste

Én linje, først i utskriften, før noe annet skjer:

```
Oppsett: rie-modeller\tfm-sjekk.toml
Leser 2 modell(er)…
```

eller, når ingen finnes:

```
Oppsett: ingen funnet, bruker standardverdiene
```

Det er det som gjør automatisk oppslag forsvarlig. Uten linja kunne to kjøringer
av samme kommando gi ulikt svar uten at noe forklarte hvorfor — og en fil som
kommer inn i et repo ville endret en port i CI i stillhet.

### En manglende fil stopper kjøringen

`--systemtabell` har `exists=True` i dag, så Typer avviser en gal sti før noe
kjøres. Stier fra konfigurasjonen har ingen slik kontroll, og må få en.

Feilmeldingen skal navngi både stien slik den sto i fila og stien den ble løst
til. De to er ulike, og det er nettopp forskjellen mellom dem som er forvirrende
når noe er galt.

## Risks / Trade-offs

**En fil man ikke visste om endrer resultatet** → Det er den reelle prisen for
automatisk oppslag, og hele grunnen til meldingslinja. Er den ikke der, skal denne
endringen ikke gjøres.

**CI kan plukke opp en fil som kommer inn i repoet** → Samme mekanisme, og samme
vern: linja står i loggen. Et bygg som vil være sikker, kan fortsatt oppgi
`--config` eksplisitt.

**To steder kan ha hver sin fil** → Modellens mappe vinner, og linja sier hvilken
som ble brukt. Kravet prøver tilfellet eksplisitt, for det er det eneste der
rekkefølgen er synlig.

**Flere modeller i ulike mapper** → Oppslaget bruker den *første* modellen. I en
federering ligger fagmodellene som regel sammen; gjør de ikke det, er
`--config` svaret. Verdt å si i dokumentasjonen framfor å finne på en regel som
gjetter.

## Migration Plan

Ingen. Et prosjekt uten `tfm-sjekk.toml` oppfører seg som før. Et prosjekt som har
en, får den lest — og linja i utskriften sier fra første gang det skjer.

## Open Questions

Ingen som kan utsettes uten å endre spesifikasjonen eller oppgavene.
