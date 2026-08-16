"""K8 — Elektro-spesifikk konsistens.

«Din faglige signatur. (...) Dette er kontrollen ingen andre kommer til å
skrive, fordi den krever at man forstår både IFC og et kursopplegg.» (§4)

STATUS: delvis. K8a (undernummer utfylt for elektro) er implementert fordi
den bare trenger den parsede TFM-ID-en. K8b/K8c trenger tilkoblingsgrafen
fra IFC — `IfcRelConnectsPorts` / `IfcDistributionPort` / systemtilhørighet
via `IfcRelAssignsToGroup` — og den er ikke uttrukket i `IfcObjekt` ennå.

Uke 6 (§9): «Ta deg tid her; dette er differensiatoren.» Rekkefølge:
  1. Utvid `IfcObjekt` med `tilkoblet_system` og `porter` i loaderen.
     Husk at feltene må forbli picklebare — se `modell`-docstringen.
  2. K8b: objekter tilkoblet samme fordeling skal ha konsistent
     systemforekomst.
  3. K8c: flagg kursnumre som gjentas innenfor samme fordeling.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class K8Elektro(Kontroll):
    id = "K8"
    tittel = "Elektro: kurs-/sløyfenummer er utfylt og konsistent"
    standard_alvorlighet = Alvorlighet.FEIL

    def kjor(self, k: Kontekst) -> list[Funn]:
        funn = []
        for objekt, tfm in k.med_tfm():
            if not tfm.er_elektro:
                continue
            # For elektro tolkes undernummeret som kurs-/sløyfenummer, og
            # «000» betyr i praksis at det ikke er satt.
            if tfm.undernummer.strip("0") == "":
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Elektroobjekt i system {tfm.systemkode} mangler "
                        f"kurs-/sløyfenummer (undernummeret er «{tfm.undernummer}»). "
                        f"For NS 3451 kapittel 4 og 5 skal undernummeret være utfylt.",
                        objekt,
                    )
                )
        return funn
