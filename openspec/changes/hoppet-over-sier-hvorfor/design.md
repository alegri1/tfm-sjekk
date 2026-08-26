## Context

Se proposal.md — Why. `kjor_alle` kjenner allerede årsaken; den kastes på vei ut:

```python
for kontroll in _REGISTER:
    if not kontroll.aktiv(k):
        hoppet_over.append(kontroll); continue
    if kontroll.krever_kodetabell and k.systemtabell is None and k.komponenttabell is None:
        hoppet_over.append(kontroll); continue
    if kontroll.krever_master and k.master is None:
        hoppet_over.append(kontroll); continue
```

Tre grener, én liste. Informasjonen finnes i kontrollflyten og forsvinner i
returverdien.

## Goals / Non-Goals

**Goals:**
- Årsaken overlever ut til konsollen og rapporten.
- Meldingen sier hva som skal til, ikke bare hva som mangler.

**Non-Goals:**
- **`--config` endres ikke.** Se under.
- Ingen ny kontroll og ingen nye funn. En hoppet kontroll skal ikke bli en rad i
  BCF-en; se under.
- Ingen endring i hvilke kontroller som hoppes over.

## Decisions

### `--config` beholder «bytt ut», ikke «slå sammen»

Fella som utløste endringen er at `--config tidligfase.toml` tar med seg
tabellstiene. Fristelsen er å la `--config` slå seg sammen med den funne
`tfm-sjekk.toml`.

Vi gjør det ikke. «Bruk denne fila» er en forutsigbar regel som kan leses av
filnavnet alene. Sammenslåing reiser straks spørsmål uten opplagte svar —
erstatter en liste eller utvider den? hva med en tom liste? — og resultatet av
en kjøring kunne da ikke leses ut av én fil. Det ville vært en ny og verre
tvetydighet enn den vi fjerner.

Fella forsvinner uansett når årsaken oppgis: ser du «hoppet over — ingen
systemtabell», vet du på ett sekund hva `--config` tok med seg.

### Årsaken er en verdi som følger kontrollen, ikke en streng CLI-en gjetter

`kjor_alle` returnerer `(kontroll, grunn)` framfor bare kontrollen. Alternativet
— å la CLI-en regne ut årsaken på nytt fra `Kontekst` — ville duplisert
betingelsene i `kjor_alle`, og de to kunne blitt uenige. Det er samme mønster som
har bitt her før: to steder sier det samme, og bare det ene oppdateres.

### En hoppet kontroll blir ikke et funn

D1 er et funn fordi tomt omfang som regel er en feil noen skal rette. En hoppet
kontroll er oftest et bevisst valg — de fleste som prøver verktøyet har ikke
kjøpt NS 3451 ennå, og fire info-rader i hver eneste kjøring blir ikke lest.

Grensen er at funn er ting i modellen; dette er ting ved kjøringen. Samme skille
som gjør at D1 står utenfor nummerserien K1–K9.

*Alternativ vurdert:* info-funn, så årsaken følger med i BCF og CSV. Det ville
gjort den synlig for den som bare får rapporten. Men prisen er fire rader i hver
kjøring uten tabeller, og det er den vanligste kjøringen.

### Meldingen navngir flagget og nøkkelen

    K3: hoppet over — ingen systemtabell (--systemtabell, eller «systemtabell» i oppsettet)

Ikke «mangler data». Kontrollen vet hvilken tabell den trenger, og navnene er
allerede skrevet i `Konfigurasjon`. Å oppgi dem koster ingenting og fjerner et
oppslag i dokumentasjonen.

## Risks / Trade-offs

**HTML-linja er ikke laget for flere linjer** → `Hoppet over: K3, K4, K5, K7` er
en `<p class="meta">`. Med årsaker blir den lengre enn den er tegnet for. Må
åpnes og ses på, i begge fargepaletter — står i proposal.md under «Prøves hos
konsumenten».

**Signaturen til `kjor_alle` endres** → Den kalles fra `cli.py`, fra tester og
fra `verktoy/`. Alle er i repoet, og typene fanger dem.

**Årsaken kan bli feil hvis rekkefølgen i `kjor_alle` endres** → Rekkefølgen ER
betydningen: en kontroll som både er slått av og mangler tabell skal melde at den
er slått av, for det er valget brukeren tok. Det bør stå i koden.
