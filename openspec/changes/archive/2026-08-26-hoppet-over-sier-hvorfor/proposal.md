## Why

Verktøyet sier hvilke kontroller som ble hoppet over, men ikke hvorfor:

    K3: hoppet over
    K4: hoppet over
    K5: hoppet over
    K7: hoppet over

Og i HTML-rapporten: `Hoppet over: K3, K4, K5, K7`.

Tre helt ulike årsaker faller sammen til det ene ordet — `kjor_alle` skiller
dem, og informasjonen kastes på vei ut:

    kontroll.aktiv(k) er usann          slått av i oppsettet, et bevisst valg
    krever_kodetabell, ingen tabell     mangler data
    krever_master, ingen master         mangler data

For brukeren er de tre motsatte handlinger: la det være, skaff tabellen, skaff
mastera. Meldingen sier ikke hvilken.

**Det biter konkret.** `--config` bytter ut hele oppsettet framfor å slå det
sammen med `tfm-sjekk.toml`. Kjører du `--config tidligfase.toml`, forsvinner
tabellstiene med, K3, K4, K5 og K7 hopper over, og rapporten blir **renere enn
den skulle vært**. Det eneste som sies er «hoppet over».

Det er samme tvetydighet `dekning` allerede finnes for å fjerne: fravær av funn
kan bety at alt er i orden, eller at ingen kontroll hadde noe å se på. Her er
det kontrollen selv som aldri kjørte, og det er verre — den så ikke engang etter.

## What Changes

- Hver hoppet kontroll oppgir **hvorfor**, i konsollen og i HTML-rapporten:

      K3: hoppet over — ingen systemtabell (--systemtabell, eller «systemtabell» i oppsettet)
      K7: hoppet over — ingen TFM-master (--master, eller «tfm_master» i oppsettet)
      K8: hoppet over — slått av i oppsettet

- Grunnen sier hva som skal til, ikke bare hva som mangler. En melding som
  navngir flagget og oppsettnøkkelen er forskjellen mellom å lete og å rette —
  samme grep som «Mente du …?» ved en ukjent nøkkel.
- «Ikke implementert ennå» blir stående som egen grunn, som i dag.
- `--config` endres **ikke**. Se design.md.

## Capabilities

### Modified Capabilities
- `dekning`: evnen dekker i dag hvor mye av en modell som ble undersøkt. Den
  utvides med hvilke kontroller som ikke kjørte, og hvorfor — samme spørsmål,
  ett hakk opp: ikke «så den på noe», men «så den etter i det hele tatt».

## Impact

- `src/tfm_sjekk/kontroller/__init__.py`: `kjor_alle` returnerer grunnen sammen
  med kontrollen framfor å kaste den.
- `src/tfm_sjekk/kontroller/base.py`: en grunn som kan navngis.
- `src/tfm_sjekk/cli.py`: linja som skriver den.
- `src/tfm_sjekk/rapport/html.py`: `Hoppet over` med grunn per kontroll.
- Kallere av `kjor_alle` i tester og i `verktoy/`.

**Prøves hos konsumenten:** kjør demomappa med `--config tidligfase.toml` — den
kjøringen er nettopp fella. Meldingen skal si at tabellene mangler, ikke bare at
kontrollene hoppet over. Og HTML-rapporten må åpnes; teksten er lengre nå, og
`Hoppet over`-linja er en `<p class="meta">` som ikke er laget for flere linjer.
