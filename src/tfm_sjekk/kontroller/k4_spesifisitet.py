"""K4 — Spesifisitetsregel.

PA 0805: systemkoder skal angis mest mulig spesifikt, og overordnede koder
skal ikke brukes der underkoder finnes. Standardens eget eksempel er at
«2300 Ytterveggsystemer» ikke skal brukes når 2310, 2320 eller 2330 er
tilgjengelige.

Implementert som spesifisert i §4: har koden barn i kodetabellen, gi
advarsel — ikke feil. Det er en anbefaling, ikke et absolutt krav, og et
prosjekt kan ha gode grunner til å ligge på et grovere nivå.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K4Spesifisitet(Kontroll):
    id = "K4"
    tittel = "Systemkoden er angitt så spesifikt som kodetabellen tillater"
    standard_alvorlighet = Alvorlighet.ADVARSEL
    krever_kodetabell = True

    def kjor(self, k: Kontekst) -> list[Funn]:
        if k.systemtabell is None:
            return []
        funn = []
        for objekt, tfm in k.med_tfm():
            barn = k.systemtabell.barn(tfm.systemkode)
            if not barn:
                continue
            eksempler = ", ".join(barn[:3])
            mer = " m.fl." if len(barn) > 3 else ""
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"Systemkoden «{tfm.systemkode}» er overordnet. Mer spesifikke "
                    f"koder finnes: {eksempler}{mer}. PA 0805 krever mest mulig "
                    f"spesifikk kode.",
                    objekt,
                )
            )
        return funn
