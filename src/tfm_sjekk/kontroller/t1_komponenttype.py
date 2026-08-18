"""T1 — Komponenttypen skal være den samme i begge feltene.

Komponenttypen står to steder i en modell: i `%`-delen av TFM-ID-en, og i et
eget egenskapssett (`TFM11_Type` i de vanlige norske Revit-malene, §3).

    TFM11_Forekomst:  ++115080=3600.001.04-JVZ001%JVZ.001.008
    TFM11_Type:                                   JVZ.001.008

To felt med samme opplysning er nettopp der en modell går ut av synk med seg
selv — noen retter TFM-ID-en uten å rette typefeltet, eller motsatt. Det er
samme slags relasjonelle sjekk som K6 og K8, og ingen andre verktøy gjør den.

Graden er feil: et sprik er en selvmotsigelse i merkingen, og verdien lar seg
ikke avgjøre uten å rette modellen.

Kontrollen står utenfor nummerserien K1–K9, som D1. §4 definerer serien, og
`specification/` er fasit for §-numrene og vokser ikke per endring — et «K10»
ville vært et nummer uten paragraf bak seg. At kontrollen ikke er i §4 betyr
ikke at den er mindre viktig, bare at spesifikasjonen ble skrevet før noen så
at den samme opplysningen står to steder.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class T1Komponenttype(Kontroll):
    id = "T1"
    tittel = "Komponenttypen er den samme i TFM-ID-en og i typefeltet"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        funn = []
        for objekt in k.objekter:
            sprik = k.komponenttype_spriker(objekt)
            if sprik is None:
                continue
            fra_id, fra_felt = sprik
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"Komponenttypen i typefeltet «{fra_felt}» er ikke den samme "
                    f"som i TFM-ID-en «{fra_id}». De to skal beskrive samme type, "
                    f"og hvilken som gjelder lar seg ikke avgjøre herfra.",
                    objekt,
                )
            )
        return funn
