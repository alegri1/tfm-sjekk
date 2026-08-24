## Context

Se proposal.md — Why.

Posisjonen går én vei og leses av én ting:

    loader._posisjon(produkt)  ->  IfcObjekt.posisjon
                               ->  Funn.posisjon  (satt av Funn.for_objekt)
                               ->  bcf._kamera(viewpoint, mål)

`_posisjon` henter siste kolonne av plasseringsmatrisen fra
`ifcopenshell.util.placement.get_local_placement`. Den matrisen er i modellens
egen lengdeenhet — ifcopenshell regner ikke om noe.

Ingen kontroll leser `posisjon`. Feltet finnes utelukkende for kameraet.

## Goals / Non-Goals

**Goals:**

- Kameraet skal peke på objektet i en modell som ikke er i meter.
- `posisjon` skal bety det samme uansett hvilken fil den kom fra.

**Non-Goals:**

- Å regne om noe annet enn posisjon. Toleranser og lengder finnes ikke i
  verktøyet — TFM er tekst, ikke geometri.
- Å håndtere georeferering (`IfcMapConversion`). Snowdon har store koordinater
  fordi Revit eksporterte med delte koordinater, ikke fordi fila er
  georeferert. Kameraet står i modellens eget system, og der hører det hjemme.
- Å utlede enheten av tallenes størrelse. En modell kan stå tusenvis av meter
  fra origo helt lovlig, og en gjetning som treffer ni av ti ganger er verre
  enn ingen.

## Decisions

### Omregningen skjer i loaderen, ikke i BCF-skriveren

Enheten står i `IfcUnitAssignment` på `IfcProject`. Å lese den i `bcf.py` ville
betydd at rapportmodulen måtte kjenne IFC — og den arkitektoniske regelen i
dette prosjektet er at `tfm_sjekk.ifc` er eneste modul som importerer
ifcopenshell, og at den returnerer ren, picklebar pydantic-data.

Da blir `posisjon` meter for alle som leser den, og BCF-skriveren slipper å vite
hvor tallet kom fra. Skulle et annet format trenge posisjonen senere, arver det
den samme garantien uten å gjøre noe.

Alternativet — å sende enheten med som et felt på `IfcObjekt` og regne om i
BCF — ble valgt bort. Det ville flyttet en IFC-detalj ut i alle konsumentene, og
gjort feilen mulig å gjenta i det neste formatet.

### Faktoren leses én gang per fil

`_posisjon` kalles per objekt; enheten er en egenskap ved fila. Å slå den opp
2439 ganger for Snowdon ville vært 2439 like svar.

Faktoren finnes ved å gå `IfcUnitAssignment` → `LENGTHUNIT`. En `IfcSIUnit`
med `Prefix` (millimeter) har sin egen faktor; en `IfcConversionBasedUnit` har
`ConversionFactor` med både verdi og enhet. Begge må dekkes: norske modeller er
ofte i millimeter, amerikanske i fot.

### Meter når enheten mangler

`demo-elektro.ifc` har ingen `IfcUnitAssignment` i det hele tatt. Den er
syntetisk, og IFC krever egentlig enheter på `IfcProject` — men verktøyet skal
lese det det får.

Meter er den eneste antakelsen som ikke gjør noe verre: med faktor 1.0 er
oppførselen nøyaktig som i dag, og en fil uten enhet er allerede en fil vi ikke
kan vite noe sikkert om.

### `KAMERAAVSTAND` slutter å ta forbehold

Konstantene endrer ikke verdi, bare betydning: fra «modellens enhet (normalt
meter)» til meter. Kommentaren som beskrev antakelsen blir en kommentar som
beskriver hvorfor antakelsen ikke lenger finnes.

## Risks / Trade-offs

**Modeller i millimeter får kameraet flyttet mye** → En norsk Revit-modell er
gjerne i millimeter, og der er dagens kamera 8 mm fra objektet — praktisk talt
inni det. Etter omregningen står det 8 meter unna. Det er en stor endring for
de brukerne, og det er den riktige: 8 mm var aldri ment.

**Emner blir ikke byte-identiske med tidligere kjøringer** → BCF-en skal være
reproduserbar for samme funn og samme `--opprettet`, og den blir det fortsatt.
Men en fil laget før denne endringen og en laget etter vil skille seg for en
modell som ikke er i meter. Det er hele poenget, og det er verdt en linje i
utgivelsesteksten.

**Enheten kan være noe vi ikke har tenkt på** → `IfcUnitAssignment` tillater
mer enn meter, millimeter og fot. Klarer vi ikke å tolke den, skal
omregningen falle tilbake på 1.0 og kjøringen fortsette — et kamera på feil
sted er en dårligere rapport, ikke en mislykket kjøring. Det er samme
avveining `_posisjon` allerede gjør når plasseringen ikke lar seg lese.
