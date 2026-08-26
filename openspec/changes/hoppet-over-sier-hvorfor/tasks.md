## 1. Årsaken overlever

- [ ] 1.1 En navngitt grunn per hoppetilfelle: slått av, mangler kodetabell,
      mangler master, ikke implementert
- [ ] 1.2 `kjor_alle` returnerer grunnen sammen med kontrollen
- [ ] 1.3 Rekkefølgen i `kjor_alle` er betydningen — en kontroll som både er
      slått av og mangler tabell skal melde at den er slått av. Skriv det i koden
- [ ] 1.4 Test: hver av de fire grunnene gir riktig verdi
- [ ] 1.5 Test: slått av OG manglende tabell gir «slått av»

## 2. Meldingen sier hva som skal til

- [ ] 2.1 Grunnen formuleres ett sted, ikke i både CLI og HTML
- [ ] 2.2 Manglende data navngir flagget og oppsettnøkkelen
- [ ] 2.3 `cli.py` skriver grunnen etter kontroll-ID-en
- [ ] 2.4 Test: meldingen for manglende systemtabell nevner `--systemtabell` og
      `systemtabell`
- [ ] 2.5 Test: meldingen for manglende master nevner `--master` og `tfm_master`

## 3. Rapporten

- [ ] 3.1 `skriv_html` tar grunnene, ikke bare ID-ene
- [ ] 3.2 «Hoppet over» viser én linje per kontroll med grunn
- [ ] 3.3 Test i `tests/test_html.py`: grunnen står i HTML-en
- [ ] 3.4 Sjekk at ingen ny farge er innført uten at den finnes i begge paletter

## 4. Kallerne

- [ ] 4.1 Alle kallere av `kjor_alle` i `src/`, `tests/` og `verktoy/` oppdatert
- [ ] 4.2 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene

## 5. Prøvd der det brukes

- [ ] 5.1 Kjør demomappa med `--config tidligfase.toml` — fella selv. Meldingen
      skal si at tabellene mangler, ikke bare at kontrollene hoppet over
- [ ] 5.2 Kjør uten tabeller i det hele tatt og les konsollen
- [ ] 5.3 Kjør med en kontroll slått av i oppsettet og se at grunnen skiller seg
- [ ] 5.4 **Åpne HTML-rapporten**, i lys OG mørk modus. Linja er lengre nå enn
      den er tegnet for
