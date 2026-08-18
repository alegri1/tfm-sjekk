"""Kontekst — hele modellen, ferdig parset, på ett sted.

Dette er den bærende arkitekturbeslutningen. K1–K5 er per objekt og ville
klart seg med en løkke, men K6 (unikhet), K7 (master) og K8 (elektro) må se
alle objektene samtidig, på tvers av alle fagmodellene som federeres. Derfor
bygges konteksten én gang, og hver kontroll er en ren funksjon
``Kontekst -> list[Funn]``.
"""

from __future__ import annotations

from collections import defaultdict, deque
from functools import cached_property

from pydantic import BaseModel, Field

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

    fordelinger: dict[str, list[str]] = Field(
        default_factory=dict,
        description=(
            "GlobalId til en fordeling → GlobalId-ene som henger på den. "
            "Bygget én gang av `bygg`; K8b og K8c leser den."
        ),
    )

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
            fordelinger=_bygg_fordelinger(objekter, config),
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

    def dekning(self) -> dict[str, tuple[int, int]]:
        """Per fagmodell: (objekter i omfanget, objekter lest).

        To tall, ikke ett. Ett tall kan ikke skille «412 objekter, ingen
        relevante» fra «412 objekter, alle kontrollert», og det er nettopp den
        forskjellen som avgjør om en ren rapport betyr noe.

        Grupperingen går på fil, ikke på kjøringen samlet: i en federering av
        RIE, RIV og ARK er det ARK-fila som skal si fra, selv om kjøringen har
        objekter nok til sammen.
        """
        lest: dict[str, int] = defaultdict(int)
        for objekt in self.objekter:
            lest[objekt.kildefil] += 1

        i_omfang: dict[str, int] = defaultdict(int)
        for objekt in self.relevante_objekter():
            i_omfang[objekt.kildefil] += 1

        return {fil: (i_omfang[fil], antall) for fil, antall in sorted(lest.items())}

    def klasser_i(self, kildefil: str) -> list[str]:
        """IFC-klassene som faktisk finnes i én fagmodell.

        Uten dem er «ingenting ble sjekket» en beskjed uten anvisning.
        """
        return sorted({o.ifc_klasse for o in self.objekter if o.kildefil == kildefil})

    def objekt(self, global_id: str) -> IfcObjekt | None:
        return self._etter_id.get(global_id)

    @cached_property
    def _etter_id(self) -> dict[str, IfcObjekt]:
        return {o.global_id: o for o in self.objekter}

    def er_fordeling(self, objekt: IfcObjekt) -> bool:
        return any(objekt.er_av_type(k) for k in self.config.elektro.fordeling_klasser)


def _bygg_fordelinger(objekter: list[IfcObjekt], config: Konfigurasjon) -> dict[str, list[str]]:
    """Finner hvilke objekter som henger på hvilken fordeling.

    Koblingsgrafen er udelt: en lampe er koblet til en kabel som er koblet til
    en fordeling. Derfor søkes det i bredden ut fra hver fordeling, og søket
    stopper i neste fordeling. Det er den regelen som gjør en underfordeling
    til sin egen rot i stedet for å bli slukt av hovedfordelingen — og som
    hindrer at hele bygget havner under den første tavla i fila.

    Objekter uten kobling til noen fordeling havner ikke i noen liste. K8b og
    K8c er da stille om dem; det er K1–K5 sitt bord om merkingen er feil.
    """
    etter_id = {o.global_id: o for o in objekter}
    fordelinger = [
        o for o in objekter if any(o.er_av_type(k) for k in config.elektro.fordeling_klasser)
    ]
    er_fordeling = {o.global_id for o in fordelinger}

    ut: dict[str, list[str]] = {}
    for tavle in fordelinger:
        sett: set[str] = {tavle.global_id}
        ko = deque(tavle.tilkoblet)
        medlemmer: set[str] = set()
        while ko:
            gid = ko.popleft()
            if gid in sett or gid not in etter_id:
                continue
            sett.add(gid)
            if gid in er_fordeling:
                continue  # nabotavla er sin egen rot
            medlemmer.add(gid)
            ko.extend(etter_id[gid].tilkoblet)
        ut[tavle.global_id] = sorted(medlemmer)
    return ut
