## 1. Feilen får et navn

- [ ] 1.1 Legg `ModellFeil(Exception)` i `ifc/loader.py`, ved siden av der
      grensen mot ifcopenshell går. Den bærer stien og en kort forklaring, og
      må være picklebar — bare strenger.
- [ ] 1.2 La `les_modell` fange det ifcopenshell kaster når fila ikke lar seg
      åpne eller tolke, og reise `ModellFeil` i stedet.
- [ ] 1.3 Legg til sjekken av avslutningsmarkøren `END-ISO-10303-21;` før fila
      åpnes. Les slutten av fila, ikke hele.
- [ ] 1.4 Tre meldinger, fordi de krever tre ulike handlinger: kan ikke åpnes,
      ikke IFC, avkuttet.

## 2. Feilen overlever prosessgrensen

- [ ] 2.1 La `_les_en` i `ifc/federering.py` fange og reise `ModellFeil` med
      stien i seg, slik at filnavnet ikke må utledes av rekkefølgen.
- [ ] 2.2 Eksporter `ModellFeil` fra `tfm_sjekk.ifc`.

## 3. Kommandolinja svarer som på et oppsett som ikke kan leses

- [ ] 3.1 Fang `ModellFeil` i `cli.py` og gjør den til `typer.BadParameter` med
      `param_hint="modeller"` — samme utgang som `OppsettFeil`: exit 2, melding,
      ingen rapport.
- [ ] 3.2 Sjekk at feilen kommer FØR noe skrives til utmappa.

## 4. Prøv de tre utfallene

- [ ] 4.1 Test: en tom fil gir exit 2 og en melding som navngir fila.
- [ ] 4.2 Test: en fil som ikke er IFC gir exit 2 og sier at den ikke kunne
      leses som IFC.
- [ ] 4.3 Test: en avkuttet fil — en ekte demomodell uten de siste bytene — gir
      exit 2 og sier at fila ser avkuttet ut.
- [ ] 4.4 Test: en hel fil leses fortsatt som før.
- [ ] 4.5 Test: ingen av de tre etterlater en rapportfil i utmappa.
- [ ] 4.6 Test: exit-koden er den samme for alle tre, og den er ikke 1.

## 5. Prøv den federerte veien

- [ ] 5.1 Test: tre filer der den andre er ødelagt gir en melding som navngir
      NETTOPP den fila. Tre og ikke to, slik at prosesspoolen faktisk brukes —
      `les_modeller` går sekvensielt under to filer, og en test med én ville
      aldri nådd den veien feilen skal overleve.
- [ ] 5.2 Test: `ModellFeil` kan pickles. Det er den slags som virker
      sekvensielt og ryker i pool-en.
- [ ] 5.3 Test: ingen rapport skrives for de filene som gikk bra.

## 6. Se på det

- [ ] 6.1 Kjør de tre ødelagte filene fra kommandolinja og les det som kommer
      ut. Ingen traceback, og meldingen skal si hva man gjør nå.
- [ ] 6.2 Kjør i cp1252-konsoll. De nye meldingene har æøå og anførselstegn, og
      det er nettopp den avsluttende utskriften som har ryket der før.
- [ ] 6.3 Oppdater README: §5-avsnittet om exit-koder nevner i dag bare 0 og 1.
- [ ] 6.4 Kjør demoen og se at 17 funn og exit 1 er uendret.
