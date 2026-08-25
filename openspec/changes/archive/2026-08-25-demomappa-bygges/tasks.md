## 1. Malen

- [x] 1.1 `verktoy/demomappe-LES-MEG.mal.txt` — dagens `LES-MEG.txt` med hvert
      kjøringstall byttet mot en navngitt plassholder
- [x] 1.2 Skriv ned i malen hvorfor tabellene står i `kjor.cmd` og ikke i
      `tfm-sjekk.toml`. Står det bare i mappa, forsvinner det ved neste rydding

## 2. Byggingen: det som kopieres

- [x] 2.1 `verktoy/lag_demomappe.py` med `--mappe` og `--versjon`. Ingen
      standardsti hjem til mitt skrivebord
- [x] 2.2 Kall `eksempler/lag_demomodell.py`, og kopier modellene den lagde
- [x] 2.3 Kopier FIKTIV-tabellene, `dynamo/*.dyn` og oppsettfragmentene
- [x] 2.4 En kilde som ikke finnes stopper byggingen og navngis
- [x] 2.5 De fire Revit-avledede filene: stopp om en mangler, rør dem ikke
- [x] 2.6 Filer i mappa byggingen ikke kjenner: si fra, ikke slett
- [x] 2.7 Skriv `tfm-sjekk.toml` (ruten, uten tabellene) og `kjor.cmd`

## 3. Binæren

- [x] 3.1 `gh release download` av `tfm-sjekk-windows.exe` for oppgitt versjon
- [x] 3.2 Stopp med det som mangler om `gh` ikke finnes eller utgivelsen ikke har fila
- [x] 3.3 Kjør den nedlastede binæren og les versjonen ut av den. Er den en annen
      enn `--versjon`, stopp — da er det ikke den utgivelsen mappa sier den er

## 4. Tallene måles

- [x] 4.1 Kjør hver dokumenterte kommando med binæren i mappa, og les `funn.csv`
- [x] 4.2 Fyll malen med `str.format` og navngitte felt
- [x] 4.3 En plassholder igjen etter utfylling stopper byggingen og navngis.
      `LES-MEG.txt` skrives ikke
- [x] 4.4 En kommando som feiler uventet stopper byggingen. Merk at `sjekk` gir
      exit 1 når den finner feil — det er ventet, og ikke en feilet kommando
- [x] 4.5 Skriv `LES-MEG.txt` med BOM, CRLF og ingen tabulator

## 5. Tester

- [x] 5.1 Bygg mot en `tmp_path` og sammenlign hver kopiert fil med kilden
- [x] 5.2 En redigert kopi i mappa overskrives ved ny bygging
- [x] 5.3 En manglende kilde gir feil som navngir fila
- [x] 5.4 En manglende Revit-fil gir feil, og de som finnes er urørt etterpå
- [x] 5.5 En plassholder uten verdi gir feil, og `LES-MEG.txt` finnes ikke
- [x] 5.6 Malen inneholder ingen kjøringstall — bare plassholdere
- [x] 5.7 Den skrevne `LES-MEG.txt` har BOM, CRLF og ingen tabulator

## 6. Prøvd der det brukes

- [x] 6.1 `uv run pytest` grønn, `ruff check` og `ruff format --check` rene
- [x] 6.2 Bygg den ekte mappa fra v0.7.0, og sammenlign fil for fil med den som
      ligger der nå. Alt som avviker skal kunne forklares
- [x] 6.3 Kjør hver kommando i den nye `LES-MEG.txt` og sammenlign med tallet
      den lover — den prøven som fant de tre driftene
- [ ] 6.4 **Til brukeren:** åpne `LES-MEG.txt` i Notisblokk, dobbeltklikk
      `kjor.cmd`, og importer BCF-en i en viewer. En mappe som ble bygget uten
      feilmelding er ikke det samme som en mappe som virker
