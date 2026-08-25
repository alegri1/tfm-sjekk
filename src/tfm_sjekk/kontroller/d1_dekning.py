"""D1 — Dekning: ble det i det hele tatt sett på noe?

Denne kontrollerer *kjøringen*, ikke modellen, og står derfor utenfor
nummerserien K1–K9 i §4. Den svarer på et spørsmål ingen av dem kan: null
funn kan bety at alt er i orden, eller at ingen kontroll hadde noe å se på.

Omfanget bestemmes av `ifc_klasser`. Treffer ikke lista klassene i
fagmodellen, er omfanget tomt — og da har K1 ingen objekter å savne TFM på,
mens de øvrige itererer over en tom liste. Resultatet er grønt lys på en fil
ingen har undersøkt.

Graden er advarsel, ikke feil. Verktøyet står som port i en leveranseprosess
(§5), og et legitimt kjør på en arkitektmodell skal ikke begynne å feile av en
oppgradering. Advarsler teller ikke mot exit-koden, og det er nettopp derfor
graden er den riktige her: funnet er synlig uten å stenge døra.

Vurderingen gjøres per fagmodell, som K9 gjør for MMI. I en federering av RIE,
RIV og ARK er det ARK-fila som skal si fra, selv om kjøringen samlet har
objekter nok — samlet vurdering ville latt nettopp det tilfellet gå stille
forbi.

En fagmodell som er unntatt i oppsettet melder ikke. Tallene kan ikke skille et
bevisst unntak fra en forglemmelse — begge gir null i omfanget — så kontrollen
må spørre konfigurasjonen. Uten det ville et prosjekt som med vilje federerer
inn ARK og RIB for kontrollene på tvers, fått en advarsel per fil hver eneste
kjøring. En advarsel som alltid står der, leses ikke.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn

MAKS_KLASSER_I_MELDING = 8


@registrer
class D1Dekning(Kontroll):
    id = "D1"
    tittel = "Noe ble faktisk kontrollert i hver fagmodell"
    standard_alvorlighet = Alvorlighet.ADVARSEL

    def kjor(self, k: Kontekst) -> list[Funn]:
        funn = []
        unntatt = set(k.unntatte_filer())
        for fil, (i_omfang, lest) in k.dekning().items():
            if i_omfang or fil in unntatt:
                continue

            klasser = k.klasser_i(fil)
            vist = ", ".join(klasser[:MAKS_KLASSER_I_MELDING])
            resten = len(klasser) - MAKS_KLASSER_I_MELDING
            if resten > 0:
                vist += f" … og {resten} til"

            hva = (
                f"{lest} objekter, ingen av dem i klassene som kontrolleres ({vist})"
                if klasser
                else "ingen objekter i det hele tatt"
            )
            funn.append(
                Funn(
                    kontroll=self.id,
                    alvorlighet=self.alvorlighet(k),
                    melding=(
                        f"Ingenting ble kontrollert i {fil}: {hva}. "
                        f"Fravær av funn betyr her ikke at merkingen er i orden. "
                        f"Er dette en fagmodell som skal sjekkes, utvid «ifc_klasser» "
                        f"i tfm-sjekk.toml."
                    ),
                    kildefil=fil,
                )
            )
        return funn
