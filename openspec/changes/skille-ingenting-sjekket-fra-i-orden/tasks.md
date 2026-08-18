## 1. Dekningen som data

- [x] 1.1 La `Kontekst` kunne oppgi antall leste objekter og antall i omfanget
      per fagmodell. Tallene finnes allerede i `relevante_objekter()`; det som
      mangler er grupperingen på `kildefil`.
- [x] 1.2 Test at en federering av tre filer gir riktige tall per fil, også når én
      av dem har null i omfanget.

## 2. Kontrollen

- [x] 2.1 Legg til en kontroll som melder tomt omfang per fagmodell, med grad
      advarsel. Den kontrollerer kjøringen, ikke modellen — navngi den så det
      synes, og hold den utenfor nummerserien K1–K9 i §4.
- [x] 2.2 La meldingen navngi innstillingen som styrer omfanget og hvilke
      IFC-klasser fagmodellen faktisk inneholder, så rapporten er nok til å rette
      konfigurasjonen.
- [x] 2.3 Test at en fil med bare `IfcWall` og `IfcSlab` gir ett funn, at
      meldingen nevner begge klassene, og at en fil uten objekter i det hele tatt
      behandles likt.
- [x] 2.4 Test at én tom fagmodell blant tre gir nøyaktig ett funn, og at de to
      andre ikke gir noe.
- [x] 2.5 Test at kontrollen kan slås av og få endret grad fra `tfm-sjekk.toml`,
      som enhver annen kontroll.

## 3. Exit-koden

- [x] 3.1 Test at en kjøring med bare dette funnet gir exit 0.
- [x] 3.2 Test at exit-koden fortsatt er 1 når en annen fagmodell har en ekte feil.

## 4. Rapportene

- [x] 4.1 Skill antall leste objekter fra antall i omfanget i HTML-rapporten.
      Dagens «objekter kontrollert» er antall leste, og den etiketten er
      misvisende.
- [x] 4.2 Vis dekningen per fagmodell i HTML-rapporten, også når det ikke er noe
      å melde — det er den rene rapporten en leser trenger å kunne stole på.
- [x] 4.3 Skriv dekningen i CLI-utskriften ved siden av objekttallet.
- [x] 4.4 Test at dekningen vises i HTML-en ved en kjøring helt uten funn.

## 5. Regresjon

- [x] 5.1 Oppdater demomodellene og forventningene i testene som teller funn.
      Elektro- og visningsmodellene har objekter i omfanget, så de skal ikke få
      det nye funnet; sjekk at de ikke gjør det.
- [x] 5.2 Kjør demoen ende til ende og bekreft at BCF-fila fortsatt validerer mot
      skjemaet, og at determinismen med fast `--opprettet` holder.

## 6. Dokumentasjon

- [x] 6.1 Beskriv i README hva dekningstallet betyr, og at et tomt omfang som
      regel skyldes `ifc_klasser`.

## 7. Prøving der det skal brukes

- [x] 7.1 Kjør verktøyet på en modell uten tekniske fag — buildingSMARTs
      `Building-Architecture.ifc` ligger offentlig — og bekreft at advarselen
      kommer, at exit-koden er 0, og at meldingen er nok til å forstå hvorfor.
