"""K7 — Referanseintegritet mot TFM-master.

«K7 sjekker at hvert system og hver komponenttype modellen bruker faktisk
står i mastera — og motsatt, hvilke oppføringer i mastera som ennå ikke er
modellert.» (§4)

STATUS: ikke implementert. Planlagt uke 5 (§9). Er du bak skjema i uke 6:
kutt K7 før du kutter K8 — det er beskjeden i §9.

Skjelettet under viser formen; det som mangler er `les_master`.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K7Master(Kontroll):
    id = "K7"
    tittel = "Systemer og komponenttyper finnes i prosjektets TFM-master"
    standard_alvorlighet = Alvorlighet.FEIL
    implementert = False
    krever_master = True

    def kjor(self, k: Kontekst) -> list[Funn]:
        if k.master is None:
            return []

        funn = []
        for objekt, tfm in k.med_tfm():
            if not k.master.kjenner_system(tfm.systemforekomst):
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Systemforekomsten «{tfm.systemforekomst}» står ikke i "
                        f"TFM-mastera ({k.master.kilde}).",
                        objekt,
                    )
                )
        # TODO uke 5: motsatt retning — oppføringer i mastera som ikke er
        # modellert. Krever at vi skiller «ikke modellert ennå» fra «utgått»,
        # og det avhenger av MMI/prosesstatus. Avklar med en RIE først.
        return funn
