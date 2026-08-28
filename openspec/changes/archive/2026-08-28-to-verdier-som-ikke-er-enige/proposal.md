## Why

`_finn` returnerer på **første treff** og ser aldri videre. Har et objekt to
TFM-verdier i to egenskapssett, leses den ene, og den andre nevnes ingen steder.

Prøvd med to identiske modeller der bare **rekkefølgen** på egenskapssettene i
IFC-fila er byttet om:

    Pset_Gammel      ++115080=4310.001.11-QLF111
    Pset_Revit_Data  ++115080=4310.001.99-QLF999

    rekkefølge A,B  ->  ++115080=4310.001.11-QLF111
    rekkefølge B,A  ->  ++115080=4310.001.99-QLF999

Samme modell, samme oppsett, ulikt svar. Og ingenting sier at det fantes to.

Steg 2 i `_finn` — «et konfigurert feltnavn i et hvilket som helst egenskapssett»
— itererer `egenskaper.items()`, altså rekkefølgen egenskapene tilfeldigvis fikk
ved eksport. Docstringen advarer selv mot nettopp dette for steg 3:

> «Steg 3 leser alle feltene, ikke bare det første. Ellers ville utfallet
> avgjøres av rekkefølgen egenskapene tilfeldigvis har i IFC-fila.»

Resonnementet ble gjort for felter innen ett sett. Det samme gjelder på tvers av
sett, og der er det ikke gjort.

**Det er ikke konstruert.** En modell som har vært gjennom Revit bærer gjerne
både `TFM11_Forekomst.TFM` fra kartleggingsfila og `Pset_Revit_Data.TFM` fra
runden. To merkekjøringer kan legge igjen hver sin verdi. Da validerer rapporten
den ene mens den andre blir stående i modellen, og et nedstrøms verktøy kan lese
den andre.

Evnen sier det selv: *«en verdi som leses feil her blir til et funn som er
presist og usant lenger ute.»*

## What Changes

- **Utvalget blir uavhengig av rekkefølgen i fila.** Finnes flere kandidater på
  samme styrkenivå, avgjøres valget av noe stabilt — ikke av hvor eksportøren
  tilfeldigvis plasserte egenskapssettet.
- **Uenige verdier meldes.** Har et objekt to kandidater som ikke er like, sier
  verktøyet fra, med begge verdiene og hvor de sto.
- **Like verdier meldes ikke.** Den samme TFM-en i to sett er ikke et avvik; det
  er normalt etter en runde gjennom Revit, og en melding om det ville stått i
  hver eneste kjøring på en slik modell.

## Capabilities

### Modified Capabilities
- `verdiuttrekk`: evnen beskriver hvor sikkert verktøyet kan vite at det fant
  riktig verdi. Den svarer ikke på hva som skjer når det finnes **flere** verdier
  som ikke er enige — i dag velges én i stillhet, og valget kan avhenge av
  filrekkefølge.

## Impact

- `src/tfm_sjekk/ifc/loader.py`: `_finn` må se alle kandidater på et nivå framfor
  å returnere på det første, og bære med seg at det var flere.
- `src/tfm_sjekk/modell.py`: `Verdikilde` må kunne bære den forkastede
  kandidaten, som den allerede gjør for `FORKASTET`.
- Ny kontroll, eller utvidelse av en eksisterende. Se design.md.
- `tests/test_verdiuttrekk.py`.

**Prøves hos konsumenten:** to modeller som er like bortsett fra rekkefølgen på
egenskapssettene skal gi samme resultat. Det er den prøven som avdekket
problemet, og den er den eneste som viser at det er borte.
