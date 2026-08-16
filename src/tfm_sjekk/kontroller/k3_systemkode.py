"""K3 — Gyldig systemkode. «4-sifferkoden finnes i NS 3451 tabell 8.» (§4)"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K3Systemkode(Kontroll):
    id = "K3"
    tittel = "Systemkoden finnes i NS 3451 tabell 8"
    standard_alvorlighet = Alvorlighet.FEIL
    krever_kodetabell = True

    def kjor(self, k: Kontekst) -> list[Funn]:
        if k.systemtabell is None:
            return []
        funn = []
        for objekt, tfm in k.med_tfm():
            if k.systemtabell.finnes(tfm.systemkode):
                continue
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"Systemkoden «{tfm.systemkode}» finnes ikke i kodetabellen "
                    f"«{k.systemtabell.navn}».",
                    objekt,
                )
            )
        return funn
