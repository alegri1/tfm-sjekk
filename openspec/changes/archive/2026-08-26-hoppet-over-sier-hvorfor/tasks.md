## 1. Årsaken overlever

- [x] 1.1 En navngitt grunn per hoppetilfelle: slått av, mangler kodetabell,
      mangler master, ikke implementert
- [x] 1.2 `kjor_alle` returnerer grunnen sammen med kontrollen
- [x] 1.3 Rekkefølgen i `kjor_alle` er betydningen — en kontroll som både er
      slått av og mangler tabell skal melde at den er slått av. Skriv det i koden
- [x] 1.4 Test: hver av de fire grunnene gir riktig verdi
- [x] 1.5 Test: slått av OG manglende tabell gir «slått av»

## 2. Meldingen sier hva som skal til

**Delt i to underveis.** Slått sammen ble konsollinja 140 tegn med to
tankestreker i, og K3, K4 og K5 gjentok den samme setningen. `Hoppgrunn` bærer
nå `tekst` og `raad` hver for seg, og kjøringen grupperes per grunn — ett sted,
brukt både i konsollen og i rapporten. Det så man først ved å kjøre.

- [x] 2.1 Grunnen formuleres ett sted, ikke i både CLI og HTML
- [x] 2.2 Manglende data navngir flagget og oppsettnøkkelen
- [x] 2.3 `cli.py` skriver grunnen etter kontroll-ID-en
- [x] 2.4 Test: meldingen for manglende systemtabell nevner `--systemtabell` og
      `systemtabell`
- [x] 2.5 Test: meldingen for manglende master nevner `--master` og `tfm_master`

## 3. Rapporten

- [x] 3.1 `skriv_html` tar grunnene, ikke bare ID-ene
- [x] 3.2 «Hoppet over» viser én linje per kontroll med grunn
- [x] 3.3 Test i `tests/test_html.py`: grunnen står i HTML-en
- [x] 3.4 Sjekk at ingen ny farge er innført uten at den finnes i begge paletter

## 4. Kallerne

- [x] 4.1 Alle kallere av `kjor_alle` i `src/`, `tests/` og `verktoy/` oppdatert
- [x] 4.2 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene

## 4b. Dekningstabellen motsa konsollen (funnet ved 5.4)

Rapporten viste tre oransje advarselstriper for de unntatte fagmodellene, ved
siden av «0 advarsler» i sammendraget — to påstander på samme side som motsa
hverandre. `omfang-per-fagmodell` rettet D1 og konsollinja, men `skriv_html`
fikk aldri vite hvilke filer som var unntatt.

Tatt med her og ikke som egen sak: endringen handler nettopp om at rapporten
skal si det samme som konsollen. Å rette linja over mens tabellen under motsier
den, ville vært halvt arbeid.

- [x] 4b.1 `skriv_html` tar imot hvilke fagmodeller som er unntatt
- [x] 4b.2 Raden viser «unntatt — kontrolleres ikke for TFM», ikke `0`
- [x] 4b.3 Dempet farge, IKKE advarselsfargen. Et bevisst unntak er ikke en
      forglemmelse, og det var nettopp forvekslingen
- [x] 4b.4 Test: unntatt fagmodell får ikke advarselsklassen
- [x] 4b.5 Test: uteglemt fagmodell får den fortsatt
- [x] 4b.6 Test: fargen finnes i begge paletter

## 5. Prøvd der det brukes

- [x] 5.1 Kjør demomappa med `--config tidligfase.toml` — fella selv. Meldingen
      skal si at tabellene mangler, ikke bare at kontrollene hoppet over
- [x] 5.2 Kjør uten tabeller i det hele tatt og les konsollen
- [x] 5.3 Kjør med en kontroll slått av i oppsettet og se at grunnen skiller seg
- [x] 5.4 Åpnet av brukeren 2026-08-26. Avdekket at dekningstabellen motsa
      konsollen — se 4b. Rettet, og rapporten kjørt på nytt
