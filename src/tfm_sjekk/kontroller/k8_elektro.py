"""K8 — Elektro-spesifikk konsistens.

«Din faglige signatur. (...) Dette er kontrollen ingen andre kommer til å
skrive, fordi den krever at man forstår både IFC og et kursopplegg.» (§4)

Tre deler, som bygger på hverandre:

**K8a — kursnummer er utfylt.** For NS 3451 kapittel 4 og 5 tolkes
undernummeret som kurs-/sløyfenummer, og det skal være satt. Trenger bare
den parsede TFM-ID-en.

**K8b — samme fordeling, samme system.** Alt som mates fra en fordeling
tilhører fordelingens system. Undernummeret skal variere — det er nettopp
kursnummeret — så sammenligningen går på `system` (``4310.001``), ikke på
`systemforekomst` (``4310.001.12``). Fordelinger uten egen TFM-merking
hoppes over: da er det K1 som har jobben, og å gjette systemet ut fra
flertallet av det som henger på tavla ville gjort en modelleringsfeil til
fasit.

**K8c — samme kursnummer, to ulike kurser.** At mange objekter deler
kursnummer er normalt: ti armaturer på kurs 12 skal alle ha ``.12``. Feilen
er når *ulike kurser* på samme fordeling har fått samme nummer. Det krever
at kursene faktisk er gruppert i modellen (`IfcDistributionCircuit` i IFC4,
`IfcElectricalCircuit` i 2x3). Uten kursgrupper kan ikke K8c konkludere, og
da sier den fra om det én gang i stedet for å gjette.

Grafen kontrollen leser er bygget i `Kontekst` fra `IfcObjekt.tilkoblet`.
Portene i IFC er kanter mellom objekter og finnes ikke som objekter her —
se `tfm_sjekk.ifc.loader`.
"""

from __future__ import annotations

from collections import defaultdict

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn, IfcObjekt, TfmId


@registrer
class K8Elektro(Kontroll):
    id = "K8"
    tittel = "Elektro: kurs-/sløyfenummer er utfylt og konsistent"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        return (
            self._a_kursnummer_utfylt(k) + self._b_konsistent_system(k) + self._c_kurskollisjon(k)
        )

    def _a_kursnummer_utfylt(self, k: Kontekst) -> list[Funn]:
        funn = []
        for objekt, tfm in k.med_tfm():
            if not tfm.er_elektro:
                continue
            if k.er_fordeling(objekt):
                # Fordelingen er roten kursene går ut fra, ikke noe som selv
                # ligger på en kurs. «=4310.001.00» er riktig merking av en
                # tavle, og K8b bruker nettopp systemdelen av den.
                continue
            if k.er_foringsvei(objekt, tfm):
                # Samme argument, andre enden: et kabelrør bærer kurser og
                # ligger ikke på en. Uten dette unntaket ga en ekte modell med
                # 2439 objekter 1018 funn om rør og bend, og 11 om ekte feil.
                #
                # TFM-en sendes med fordi IFC-klassen ikke alltid sier hva
                # objektet er: seksten koblingsbokser kom ut av Revit som
                # IfcBuildingElementProxy, med føringsvei-kode i TFM-en.
                continue
            # For elektro tolkes undernummeret som kurs-/sløyfenummer, og
            # «000» betyr i praksis at det ikke er satt.
            if tfm.kurs.strip("0") == "":
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Elektroobjekt i system {tfm.systemkode} mangler "
                        f"kurs-/sløyfenummer (undernummeret er «{tfm.kurs}»). "
                        f"For NS 3451 kapittel 4 og 5 skal undernummeret være utfylt.",
                        objekt,
                    )
                )
        return funn

    def _b_konsistent_system(self, k: Kontekst) -> list[Funn]:
        funn = []
        for tavle_id, medlemmer in k.fordelinger.items():
            tavle = k.objekt(tavle_id)
            tavle_tfm = k.parsede.get(tavle_id)
            if tavle is None or tavle_tfm is None or not tavle_tfm.er_elektro:
                continue

            for objekt, tfm in _medlemmer_med_tfm(k, medlemmer):
                if not tfm.er_elektro or tfm.system == tavle_tfm.system:
                    continue
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Objektet er tilkoblet fordelingen {_navn(tavle)} med systemet "
                        f"{tavle_tfm.system}, men er merket med systemet "
                        f"{tfm.system}. Alt som mates fra samme fordeling skal "
                        f"tilhøre samme system; det er kursnummeret som skal variere.",
                        objekt,
                    )
                )
        return funn

    def _c_kurskollisjon(self, k: Kontekst) -> list[Funn]:
        if not k.fordelinger:
            return []

        funn = []
        sett_kretser = False
        for tavle_id, medlemmer in k.fordelinger.items():
            tavle = k.objekt(tavle_id)
            if tavle is None:
                continue

            # Kurs → hvilke kursgrupper som bruker det nummeret.
            per_kurs: dict[str, dict[frozenset[str], list[IfcObjekt]]] = defaultdict(
                lambda: defaultdict(list)
            )
            for objekt, tfm in _medlemmer_med_tfm(k, medlemmer):
                if not tfm.er_elektro or not objekt.kretser:
                    continue
                sett_kretser = True
                identitet = frozenset(krets.global_id for krets in objekt.kretser)
                per_kurs[tfm.kurs][identitet].append(objekt)

            for kurs, per_krets in sorted(per_kurs.items()):
                if len(per_krets) < 2:
                    continue
                navn = sorted(
                    {str(krets) for gruppe in per_krets.values() for krets in gruppe[0].kretser}
                )
                for gruppe in per_krets.values():
                    for objekt in gruppe:
                        funn.append(
                            Funn.for_objekt(
                                self.id,
                                self.alvorlighet(k),
                                f"Kursnummer «{kurs}» er brukt av {len(per_krets)} ulike "
                                f"kurser på fordelingen {_navn(tavle)} ({', '.join(navn)}). "
                                f"Kursnumre skal være unike innenfor én fordeling.",
                                objekt,
                            )
                        )

        if not sett_kretser:
            funn.append(
                Funn(
                    kontroll=self.id,
                    alvorlighet=Alvorlighet.INFO,
                    melding=(
                        f"Fant {len(k.fordelinger)} fordeling(er), men ingen kursgrupper "
                        f"(IfcDistributionCircuit / IfcElectricalCircuit) i modellen. "
                        f"K8c kan ikke se om to kurser deler kursnummer uten dem — "
                        f"eksporter kursene fra fagmodellen for å få den kontrollen."
                    ),
                )
            )
        return funn


def _navn(objekt: IfcObjekt) -> str:
    """Kort, gjenkjennelig referanse i meldingsteksten — RIE-en leter etter
    tavlenavnet, ikke etter en GUID."""
    return f"«{objekt.navn}»" if objekt.navn else objekt.global_id


def _medlemmer_med_tfm(k: Kontekst, medlemmer: list[str]) -> list[tuple[IfcObjekt, TfmId]]:
    par = []
    for gid in medlemmer:
        objekt = k.objekt(gid)
        tfm = k.parsede.get(gid)
        if objekt is not None and tfm is not None:
            par.append((objekt, tfm))
    return par
