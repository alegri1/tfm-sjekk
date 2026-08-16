"""Kontekst — hele modellen, ferdig parset, på ett sted.

Dette er den bærende arkitekturbeslutningen. K1–K5 er per objekt og ville
klart seg med en løkke, men K6 (unikhet), K7 (master) og K8 (elektro) må se
alle objektene samtidig, på tvers av alle fagmodellene som federeres. Derfor
bygges konteksten én gang, og hver kontroll er en ren funksjon
``Kontekst -> list[Funn]``.
"""

from __future__ import annotations

from pydantic import BaseModel

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.modell import IfcObjekt, TfmId
from tfm_sjekk.parser import ParseFeil, parse
from tfm_sjekk.tabeller import Kodetabell, TfmMaster


class Kontekst(BaseModel):
    """Alt kontrollene har lov til å se."""

    objekter: list[IfcObjekt] = []
    parsede: dict[str, TfmId] = {}
    parsefeil: dict[str, str] = {}

    systemtabell: Kodetabell | None = None
    komponenttabell: Kodetabell | None = None
    master: TfmMaster | None = None

    config: Konfigurasjon = Konfigurasjon()
    kildefiler: list[str] = []

    @classmethod
    def bygg(
        cls,
        objekter: list[IfcObjekt],
        config: Konfigurasjon,
        systemtabell: Kodetabell | None = None,
        komponenttabell: Kodetabell | None = None,
        master: TfmMaster | None = None,
    ) -> Kontekst:
        """Parser alle TFM-verdier én gang. Kontrollene parser aldri selv."""
        parsede: dict[str, TfmId] = {}
        parsefeil: dict[str, str] = {}

        for obj in objekter:
            if not obj.tfm_forekomst:
                continue
            try:
                parsede[obj.global_id] = parse(obj.tfm_forekomst, config.grammatikk)
            except ParseFeil as e:
                parsefeil[obj.global_id] = str(e)

        return cls(
            objekter=objekter,
            parsede=parsede,
            parsefeil=parsefeil,
            systemtabell=systemtabell,
            komponenttabell=komponenttabell,
            master=master,
            config=config,
            kildefiler=sorted({o.kildefil for o in objekter}),
        )

    def relevante_objekter(self) -> list[IfcObjekt]:
        """Objekter i klassene K1 krever TFM på.

        Matcher på arvekjeden, ikke eksakt klassenavn: konfigurerer du
        `IfcFlowTerminal`, treffer du også `IfcAirTerminal` og de andre
        IFC4-subklassene. Ellers måtte konfigurasjonen liste hundrevis av
        klassenavn.
        """
        klasser = self.config.ifc_klasser
        return [o for o in self.objekter if any(o.er_av_type(k) for k in klasser)]

    def med_tfm(self) -> list[tuple[IfcObjekt, TfmId]]:
        """Objekter som har en TFM-ID som faktisk parset."""
        return [
            (o, self.parsede[o.global_id]) for o in self.objekter if o.global_id in self.parsede
        ]

    def objekt(self, global_id: str) -> IfcObjekt | None:
        return next((o for o in self.objekter if o.global_id == global_id), None)
