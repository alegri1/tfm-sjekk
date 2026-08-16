"""K6 — Unikhet.

«Ingen duplikate komponentforekomst-IDer i modellen. Ved federering på tvers
av fagmodeller: sjekk på tvers av alle filene som sendes inn.» (§4)

Første relasjonelle kontroll — den som gjør at hele verktøyet ikke kunne
vært en IDS-fil (§2).
"""

from __future__ import annotations

from collections import defaultdict

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K6Unikhet(Kontroll):
    id = "K6"
    tittel = "Komponentforekomster er unike i modellen"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        etter_id: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for objekt, tfm in k.med_tfm():
            etter_id[tfm.global_forekomst].append((objekt.global_id, objekt.kildefil))

        funn = []
        for forekomst, treff in etter_id.items():
            if len(treff) < 2:
                continue
            filer = sorted({fil for _, fil in treff})
            hvor = (
                f"på tvers av {len(filer)} filer ({', '.join(filer)})"
                if len(filer) > 1
                else f"i {filer[0]}"
            )
            for global_id, _kildefil in treff:
                objekt = k.objekt(global_id)
                if objekt is None:
                    continue
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Komponentforekomsten «{forekomst}» er brukt på "
                        f"{len(treff)} objekter {hvor}. Den skal være unik.",
                        objekt,
                    )
                )
        return funn
