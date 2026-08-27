"""K2 — Syntaks.

«Strengen parser mot grammatikken i §1 (...). Dette er den kontrollen som
fanger flest feil i praksis.» (§4)

Selve parsingen er allerede gjort i `Kontekst.bygg`; K2 rapporterer bare
det som havnet i `parsefeil`.

Meldingen sier også hva funnet KOSTER. `med_tfm()` returnerer bare det som
parset, og sju kontroller leser den — et objekt her er samtidig uundersøkt for
ukjent systemkode, duplisert forekomst, master-avvik, kursnummer og MMI. Uten
den setningen ser et syntaksfunn ut som en detalj, mens det skjuler sju andre.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K2Syntaks(Kontroll):
    id = "K2"
    tittel = "TFM-ID følger grammatikken"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        funn = []
        for global_id, feilmelding in k.parsefeil.items():
            objekt = k.objekt(global_id)
            if objekt is None:
                continue
            # Setningen om konsekvensen, ikke en oppramsing av kontrollnumre.
            # Numrene ville tatt plassen fra selve feilen, og de endrer seg om
            # en kontroll kommer til.
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"{feilmelding} Objektet er derfor ikke kontrollert av de "
                    f"øvrige kontrollene, som krever en tolket TFM-ID.",
                    objekt,
                )
            )
        return funn
