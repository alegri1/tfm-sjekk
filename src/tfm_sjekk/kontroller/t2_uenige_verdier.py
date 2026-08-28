"""T2 — To verdier som ikke er enige.

Ved siden av T1, og av samme grunn: begge handler om at modellen sier to ting
om samme objekt som ikke kan være sanne samtidig. T1 sammenligner
komponenttypen i TFM-ID-en med den i typefeltet; T2 sammenligner to verdier
funnet i to ulike egenskapssett.

DERFOR IKKE BLANT D-ENE. D1, D2 og D3 handler om hva verktøyet fikk gjort — om
noe var i omfanget, om det var lesbart, om resultatet er til å stole på. Dette
handler om hva som står i fila, og det er noe den som merket modellen skal
rette. Grad feil, som T1.

Verktøyet velger likevel én verdi og kontrollerer den. «Vi vet ikke» ville vært
et dårligere svar enn «vi valgte denne, og her er den andre» — uten en valgt
verdi kan ingen kontroll kjøre.

Bakgrunnen er konkret. `_finn` returnerte før på første treff, og steg 2
itererte egenskapssettene i den rekkefølgen de tilfeldigvis fikk ved eksport.
To identiske modeller med ombyttet rekkefølge ga da ulik TFM-verdi — og
ingenting sa at det fantes to. En modell som har vært gjennom Revit bærer
gjerne både `TFM11_Forekomst.TFM` fra kartleggingsfila og `Pset_Revit_Data.TFM`
fra runden.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn

FELTNAVN = {
    "forekomst": "TFM-forekomsten",
    "type": "TFM-typen",
    "mmi": "MMI-verdien",
}


@registrer
class T2UenigeVerdier(Kontroll):
    id = "T2"
    tittel = "Én verdi per felt, ikke to som er uenige"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        funn = []
        for objekt in k.objekter:
            for felt, kilde in sorted(objekt.kilder.items()):
                if not kilde.uenige:
                    continue

                valgt = _valgt_verdi(objekt, felt)
                andre = ", ".join(f"«{verdi}» i [{pset}]" for pset, verdi in kilde.uenige)
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"{FELTNAVN.get(felt, felt)} står flere steder med ulik verdi. "
                        f"Kontrollene er kjørt på «{valgt}» fra [{kilde.pset}]; "
                        f"i tillegg står {andre}. "
                        f"Hvilken som er den rette, vet bare den som merket modellen — "
                        f"og den andre blir stående i fila.",
                        objekt,
                    )
                )
        return funn


def _valgt_verdi(objekt, felt: str) -> str:
    """Verdien kontrollene faktisk arbeider på, for det feltet."""
    return {
        "forekomst": objekt.tfm_forekomst,
        "type": objekt.tfm_type,
        "mmi": objekt.mmi,
    }.get(felt) or "?"
