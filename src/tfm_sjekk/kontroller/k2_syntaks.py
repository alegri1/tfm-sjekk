"""K2 — Syntaks.

«Strengen parser mot grammatikken i §1 (...). Dette er den kontrollen som
fanger flest feil i praksis.» (§4)

Selve parsingen er allerede gjort i `Kontekst.bygg`; K2 rapporterer bare
det som havnet i `parsefeil`.
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
            funn.append(Funn.for_objekt(self.id, self.alvorlighet(k), feilmelding, objekt))
        return funn
