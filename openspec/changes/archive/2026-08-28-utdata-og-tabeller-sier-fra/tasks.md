## 1. Tabellene sier fra

- [x] 1.1 La `les_kodetabell` reise `ModellFeil` framfor `IndexError` på en tom
      fil og `ValueError` på en manglende kolonne. Meldingen som allerede står
      i `ValueError`-en er god — den skal bare nå fram.
- [x] 1.2 La `les_master` reise `ModellFeil` når fila ikke lar seg åpne som
      regneark eller CSV. `BadZipFile` fra openpyxl er ikke en melding.
- [x] 1.3 Meldingen navngir fila og sier hva som er galt, som for modellfiler.

## 2. Tabellene leses først

- [x] 2.1 Flytt lesingen av systemtabell, komponenttabell og master opp foran
      `les_modeller` i `cli.py`, dit tidsstempelet allerede valideres.
- [x] 2.2 Sjekk at rekkefølgen på utskriften fortsatt gir mening — «Leser N
      modell(er)…» skal ikke komme før en tabellfeil.

## 3. Utmappa er enten helt ny eller helt urørt

- [x] 3.1 Skriv de fire rapportene til en midlertidig mappe ved siden av
      utmappa, ikke i systemets temp — `Path.replace` er bare atomisk innenfor
      samme filsystem, og temp ligger ofte på en annen stasjon på Windows.
- [x] 3.2 Flytt filene på plass først når alle fire er skrevet, i rekkefølgen
      xlsx, bcfzip, csv, html — mest sannsynlig låst først, så vinduet der en
      halv flytting kan skje blir minst mulig.
- [x] 3.3 Rydd den midlertidige mappa i en `finally`, og gi den et navn som sier
      hva den er, for tilfellet der prosessen drepes.
- [x] 3.4 En feil under skriving eller flytting blir `ModellFeil` med filnavnet
      og setningen om at ingen rapportfil er endret.
- [x] 3.5 Feiler flyttingen MIDT i, sier meldingen at mappa nå kan inneholde
      filer fra to runder. Det ene tilfellet der løftet ikke holder, skal ikke
      være taust.
- [x] 3.6 `--ut` som peker på noe som ikke er en mappe gir en melding, ikke
      `FileExistsError`.

## 4. Prøv tabellene

- [x] 4.1 Test: tom kodetabell gir exit 2 og en melding som navngir fila.
- [x] 4.2 Test: kodetabell uten kolonnen «kode» sier hvilken kolonne som mangler.
- [x] 4.3 Test: en fil med endelsen .xlsx som ikke er et regneark gir exit 2 og
      en melding, ikke `BadZipFile`.
- [x] 4.4 Test: ingen traceback i noen av dem.
- [x] 4.5 Test: en ubrukelig tabell stopper kjøringen FØR modellene leses.
- [x] 4.6 Test: gyldige tabeller leses som før, og demoen gir 17 funn.

## 5. Prøv skrivingen

- [x] 5.1 Test: med `funn.xlsx` låst er ingen av de fire filene endret etter en
      ny kjøring. Sammenlign byte for byte mot forrige runde — det var nettopp
      en byte-sammenligning som viste at BCF-en sto igjen.
- [x] 5.2 Test: exit 2, og meldingen navngir `funn.xlsx` og nevner at fila kan
      være åpen i et annet program.
- [x] 5.3 Test: ingen traceback.
- [x] 5.4 Test: en vellykket kjøring etterlater fire filer fra denne runden, og
      ingen midlertidig mappe.
- [x] 5.5 Test: `--ut` som peker på en fil gir exit 2 og en melding.
- [x] 5.6 Test på Windows OG i CI. Fillåsing oppfører seg ulikt på Linux og
      macOS, der en åpen fil kan overskrives. Testen må hoppes over der framfor
      å late som den prøvde noe.

## 6. Se på det

- [ ] 6.1 Lås `funn.xlsx` med et ekte program — åpne rapporten i Excel — og kjør
      runden på nytt. Les det som kommer ut. Krever prosjekteieren.
      IKKE GJORT. Låsen er prøvd med `msvcrt.locking` — samme mekanisme Excel
      bruker, og utfallet er verifisert: exit 2, melding, fire uendrede filer.
      Men Excel låser på sin egen måte, og det er den låsen som betyr noe.
      Prosjekteieren valgte å arkivere uten den.
- [x] 6.2 Kjør i cp1252-konsoll. De nye meldingene har æøå og anførselstegn.
- [x] 6.3 Kjør demoen og se at 17 funn og exit 1 er uendret.
- [x] 6.4 Oppdater README: exit-kodetabellen fra 0.9.3 nevner ikke tabeller
      eller skriving.
