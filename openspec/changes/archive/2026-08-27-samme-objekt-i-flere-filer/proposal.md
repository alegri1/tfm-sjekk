## Why

`Kontekst` slår opp objekter i en dict nøklet på `global_id`:

```python
@cached_property
def _etter_id(self) -> dict[str, IfcObjekt]:
    return {o.global_id: o for o in self.objekter}
```

Dukker samme GlobalId opp i to fagmodeller, **kollapser de i stillhet** — den
siste vinner. Det samme gjelder `parsede` og `parsefeil`, som er nøklet likt.

Prøvd med samme demomodell under to filnavn:

    12 objekter lest
     6 unike GlobalId
    _etter_id          6 oppføringer for 12 objekter
    parsede+parsefeil  5 resultater for 12 objekter

    13 funn, fordelt 11 på den ene fila og 2 på den andre — enda filene
    er identiske

Følgene er tre, og alle er stille:

- **K2, K6 og K8 slår opp objektet på GlobalId** for å feste funnet til en fil.
  Med kollisjon peker funnet på en vilkårlig av dem
- **Parseresultatet deles.** Ett objekt kan ikke ha en annen TFM enn sin tvilling,
  selv om fila sier noe annet
- **K6 melder duplikat** på noe som er det samme objektet telt to ganger

**Det skjer i ekte eksporter.** Den federerte Snowdon-kjøringen har 24 456
objekter og 24 452 unike: to `IfcGrid` «Default Grid» ligger i Electrical, HVAC
og Plumbing. Der er de utenfor omfanget og gjør ingen skade — men det viser at
Revit eksporterer delte objekter inn i hver lenke.

Farlig blir det når kollisjonen treffer objekter **i** omfanget. Det skjer når
noen federerer to eksporter av samme modell — før og etter en retting, eller
fordi et mønster fanget en gammel eksport ved siden av en ny. Da blir hele
rapporten misvisende, og ingenting sier fra.

## What Changes

- Verktøyet melder når objekter **i omfanget** har samme GlobalId i mer enn én
  fagmodell, med grad advarsel — som D1 og D2.
- Meldingen sier hvilke filer det gjelder og hvor mange objekter, og at
  fil-tilhørigheten i de øvrige funnene er upålitelig for dem.
- **Objekter utenfor omfanget meldes ikke.** Delte rutenett og romlig struktur er
  normalt i lenkede eksporter og har ingen følger.
- Ingen automatisk sammenslåing eller forkasting. Verktøyet skal si fra, ikke
  gjette hvilken av to like objekter som er den rette.

## Capabilities

### Modified Capabilities
- `dekning`: evnen svarer på hva som ble undersøkt og hvorfor noe ikke ble det.
  Den utvides med et tilfelle der undersøkelsen er gjort, men **resultatet ikke
  er til å stole på** — funnene peker på vilkårlige filer.

## Impact

- `src/tfm_sjekk/kontekst.py`: en metode som finner GlobalId-er i flere filer.
- Ny kontroll `D3`, ved siden av D1 og D2.
- `tests/test_dekning.py`.

**Prøves hos konsumenten:** kjør to kopier av samme demomodell under ulike navn.
Uten endringen gir det tretten funn fordelt vilkårlig; med den skal advarselen
forklare hvorfor. Og kjør den federerte Snowdon-kjøringen — der SKAL det ikke
komme noe funn, fordi de to delte objektene er `IfcGrid` utenfor omfanget.
