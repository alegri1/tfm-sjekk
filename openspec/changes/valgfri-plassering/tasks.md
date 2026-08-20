## 1. Konfigurasjonen

- [x] 1.1 `Grammatikk.krev_plassering: bool = True` i `config.py`, med samme form
      og begrunnelse som `krev_komponenttype`
- [x] 1.2 Kommentar i `tfm-sjekk.toml` som forklarer tidligfasetilfellet, ved
      siden av de øvrige grammatikkverdiene

## 2. Parseren

- [x] 2.1 `bygg_monster` pakker `++`-delen i `(?:...)?` når `krev_plassering` er
      usann — samme grep som allerede brukes for komponenttypen
- [x] 2.2 `parse` tåler at gruppa `plassering` er `None`
- [x] 2.3 `_forste_avvik` hopper over deler som ikke kreves, slik at meldingen
      ikke etterlyser noe grammatikken har gjort valgfritt
- [x] 2.4 Test: gyldig uten plassering når den er valgfri, avvist når den er
      påkrevd, og feil sifferantall avvist i begge tilfeller
- [x] 2.5 Test: `ligner_tfm_id` godtar `=3600.001.04-JVZ001` og avviser
      `Systemair` — gjenkjenningen og formkravet skal ikke gli fra hverandre

## 3. Datamodellen og identiteten

- [x] 3.1 `TfmId.plassering: str | None` i `modell.py`
- [x] 3.2 `global_forekomst` utelater `++`-leddet når plasseringen mangler
- [x] 3.3 Test på identiteten: med og uten plassering gir ulike nøkler, to bygg
      gir ulike nøkler, to like uten plassering gir samme nøkkel

## 4. Kontrollene

- [x] 4.1 Gå gjennom hver kontroll for bruk av `plassering` og `global_forekomst`,
      og slå fast at ingen andre enn K6 rører dem
- [x] 4.2 Test: K6 finner duplikat uten plassering på tvers av to fagmodeller, og
      melder ikke duplikat for to ulike bygg
- [x] 4.3 Test: hele kontrollsettet kjører uten feil på en modell der ingen
      objekter har plassering — ingen kontroll skal kaste på `None`

## 5. Standardoppførselen skal være urørt

- [x] 5.1 Kjør hele testsuiten og slå fast at ingen eksisterende test måtte
      endres. Måtte den det, er standardverdien ikke nøytral, og det er en feil
- [x] 5.2 Test som eksplisitt låser at standardoppsettet avviser
      `=3600.001.04-JVZ001`

## 6. Demo og prøving hos konsumenten

- [x] 6.1 Fikstur og demomodell `tidligfase.ifc`: samme innhold som en
      fagmodell, men uten `++`-delen i merkingen
- [x] 6.2 Kjør den med standardoppsettet og se at hvert objekt får et
      syntaksfunn — det er tilstanden RIE-en beskrev
- [x] 6.3 Kjør den med `krev_plassering = false` og se at funnene forsvinner.
      Forskjellen skal være noe man kan se, ikke bare lese om
- [x] 6.4 `eksempler/tidligfase.toml` med oppsettet, så demoen kan kjøres uten å
      skrive en fil først
- [x] 6.5 README: kort avsnitt under «Bruk» om faser, med begge kjøringene
- [x] 6.6 `.gitignore` for den nye demomodellen, og docstringen i
      `lag_demomodell.py` oppdatert med filen og jobben dens
