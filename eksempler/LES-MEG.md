# Eksempeltabeller — IKKE NORMATIVE

Filene i denne mappa er **oppdiktede**. De inneholder ikke innhold fra
NS 3451 eller NS 3457-serien, og de kan ikke brukes til å validere et
virkelig prosjekt.

NS 3451 og NS 3457-serien er betalte standarder fra Standard Norge.
Kodetabellene deres kan ikke ligge i et offentlig repo. For reell bruk må du
ha gyldig tilgang til standardene og lage dine egne CSV-filer:

```
kode;beskrivelse
2310;<beskrivelse fra standarden>
```

Kjør så med dine egne tabeller:

```
tfm-sjekk modell.ifc --systemtabell min-ns3451.csv --komponenttabell min-ns3457-8.csv
```

Se §8 i spesifikasjonen.

## FIKTIV-tfm-master.csv

Denne er også oppdiktet, men av en annen grunn: TFM-mastera er *prosjektets egen*,
ikke Standard Norges. Den er ikke opphavsrettslig beskyttet materiale — den ligger
her bare fordi demokjøringen trenger noe å sjekke K7 mot.

Fila dekker systemene demomodellene bruker, med tre bevisste unntak som viser
begge retningene K7 går i:

- `9999.001.12` er utelatt, så det ene objektet med ugyldig systemkode gir feil
  i retningen modell → master.
- `3600.002.04` og komponenttypen `QLF.001.001` står i mastera uten å være
  modellert, og gir info i retningen master → modell.

Resten er med med vilje. Uten dem ville K7 slått ut på nesten hvert
elektroobjekt, og støyen ville skjult de tre tilfellene fila skal demonstrere.
