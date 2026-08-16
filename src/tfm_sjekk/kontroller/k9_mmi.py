"""K9 (valgfri) — Prosesstatus/MMI.

«Er MMI-verdien satt, og er den konsistent innenfor et system? SIMBA stiller
krav til prosesstatuskode.» (§4)

STATUS: ikke implementert, og bevisst nedprioritert — §4 merker den som
valgfri, «hvis tid». MMI-verdien hentes allerede i loaderen, så selve
kontrollen er kort når den tid kommer.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K9Mmi(Kontroll):
    id = "K9"
    tittel = "MMI/prosesstatus er satt og konsistent innenfor systemet"
    standard_alvorlighet = Alvorlighet.INFO
    implementert = False

    def kjor(self, k: Kontekst) -> list[Funn]:
        # TODO: gruppér på tfm.systemforekomst, flagg systemer der objektene
        # har sprikende MMI. Krev først en avklaring på hvilken MMI-skala
        # prosjektet bruker — de varierer.
        return []
