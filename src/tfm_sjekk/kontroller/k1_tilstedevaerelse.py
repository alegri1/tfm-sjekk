"""K1 — Tilstedeværelse.

«Alle objekter i konfigurerte IFC-klasser har en TFM-verdi. Uten dette blir
resten meningsløst.» (§4)
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K1Tilstedevaerelse(Kontroll):
    id = "K1"
    tittel = "Tilstedeværelse av TFM-verdi"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        funn = []
        for objekt in k.relevante_objekter():
            if objekt.tfm_forekomst:
                continue
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"Objektet mangler TFM-verdi. Forventet i egenskapssettet "
                    f"{' eller '.join(k.config.pset.forekomst)}.",
                    objekt,
                )
            )
        return funn
