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
