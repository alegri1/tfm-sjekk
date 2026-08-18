## 1. Den løse regexen

- [ ] 1.1 Bygg en løs variant av TFM-mønsteret fra samme `Grammatikk`-objekt som
      det strenge: samme form og samme deler, men uten krav til antall tegn.
- [ ] 1.2 Test at den matcher alle de ni innholdsfeilene fra forslaget, og at den
      ikke matcher verdier som ikke ligner en TFM-ID.
- [ ] 1.3 Test at de to mønstrene beskriver samme form: en verdi som matcher det
      strenge, matcher også det løse.

## 2. Meldingen

- [ ] 2.1 Sammenlign hver fanget del mot grammatikken, i lesretning, og meld det
      første avviket med delens navn, det forventede og det som faktisk står der.
- [ ] 2.2 Legg de norske navnene på delene ett sted, ved siden av grammatikken.
- [ ] 2.3 La komponentkoden gi en egen melding når bokstavene er små, framfor å
      beskrives som feil antall tegn.
- [ ] 2.4 Behold den generiske formmalen som siste utvei, når heller ikke den løse
      regexen matcher.

## 3. Tester

- [ ] 3.1 Test at feil sifferantall i plasseringen gir en melding som navngir
      plasseringen og oppgir både forventet og funnet antall.
- [ ] 3.2 Test at hver del — systemkode, systemløpenummer, undernummer,
      komponentkode, komponentløpenummer og komponenttype — kan navngis, og at
      avvik i ulike deler gir ulike meldinger.
- [ ] 3.3 Test at små bokstaver i komponentkoden gir meldingen om store bokstaver.
- [ ] 3.4 Test at en verdi med avvik i både plasseringen og komponentkoden bare
      omtaler plasseringen.
- [ ] 3.5 Test at en ikke-standard grammatikk gir det konfigurerte antallet i
      meldingen, ikke standardverdien.
- [ ] 3.6 Test at de to første trinnene i stigen er uendret: `Systemair` beskrives
      fortsatt som fremmed, og `++115080-3600.001.04` navngir den manglende delen.

## 4. Regresjon

- [ ] 4.1 Kjør demoen og les K2-meldingen. Den skal nå si hva som er galt med
      `++11508=4310.001.12-QLF005`, ikke bare vise formmalen.
- [ ] 4.2 Bekreft at BCF-fila fortsatt validerer og at determinismen med fast
      `--opprettet` holder.
