"""K5 — Gyldig komponentkode. «3-bokstavskoden finnes i NS 3457-8.» (§4)"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K5Komponentkode(Kontroll):
    id = "K5"
    tittel = "Komponentkoden finnes i NS 3457-8"
    standard_alvorlighet = Alvorlighet.FEIL
    krever_kodetabell = True

    def kjor(self, k: Kontekst) -> list[Funn]:
        if k.komponenttabell is None:
            return []
        funn = []
        for objekt, tfm in k.med_tfm():
            if k.komponenttabell.finnes(tfm.komponentkode):
                continue
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"Komponentkoden «{tfm.komponentkode}» finnes ikke i kodetabellen "
                    f"«{k.komponenttabell.navn}».",
                    objekt,
                )
            )
        return funn
