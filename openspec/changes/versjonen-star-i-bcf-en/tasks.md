## 1. Fest prøven

- [x] 1.1 Skriv en test på at emnet bærer versjonen, lest ut av `markup.bcf`.
      Den skal feile nå.
- [x] 1.2 Skriv en test på at `bcf.version` fortsatt sier `2.1` — den skal
      passere både før og etter.

## 2. Versjonen

- [x] 2.1 Utled `FORFATTER` av `importlib.metadata.version`, med navnet alene
      som reserve om pakken ikke er installert.
- [x] 2.2 Test reserven ved å simulere at oppslaget feiler.

## 3. Prøv det

- [x] 3.1 Kjør demoen og les `CreationAuthor` ut av et emne.
- [x] 3.2 Bekreft at BCF-en fortsatt er byte-identisk over to kjøringer med
      samme `--opprettet`.
- [x] 3.3 Kjør hele testsuiten, `ruff check` og `ruff format --check`.

## 4. Demomappa

- [ ] 4.1 Regenerer de tre BCF-filene der, så de bærer versjonen.
- [ ] 4.2 Nevn i LES-MEG.txt hvordan man ser hvilken utgave en BCF er laget av.
