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
from tfm_sjekk.tabeller import Kodetabell, TfmMaster, normaliser


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

        Omfanget slås opp per fagmodell. En federering blander filer med ulikt
        ansvar — arkitekten tegner armaturer for å vise rommet — og uten dette
        måles de mot RIE-ens krav.
        """
        return [
            o
            for o in self.objekter
            if any(o.er_av_type(k) for k in self.config.omfang_for(o.kildefil))
        ]

    def med_tfm(self) -> list[tuple[IfcObjekt, TfmId]]:
        """Objekter som har en TFM-ID som faktisk parset."""
        return [
            (o, self.parsede[o.global_id]) for o in self.objekter if o.global_id in self.parsede
        ]

    def komponenttype_kilder(self, objekt: IfcObjekt) -> tuple[str | None, str | None]:
        """Komponenttypen slik den står i TFM-ID-en og i typefeltet.

        Samme opplysning kan stå to steder, og det er nettopp der en modell går
        ut av synk med seg selv.
        """
        tfm = self.parsede.get(objekt.global_id)
        return (tfm.komponenttype if tfm else None), objekt.tfm_type

    def komponenttype_for(self, objekt: IfcObjekt) -> str | None:
        """Objektets komponenttype, med `%`-delen først.

        `%`-delen er en del av selve TFM-ID-en, som er det merkingen egentlig
        er; typefeltet er en gjentakelse ved siden av. Mangler `%`-delen —
        vanlig, siden `krev_komponenttype` er false som standard — gjelder
        typefeltet, og uten den ville K7 hoppet over objektet.
        """
        fra_id, fra_felt = self.komponenttype_kilder(objekt)
        return fra_id or fra_felt or None

    def komponenttype_spriker(self, objekt: IfcObjekt) -> tuple[str, str] | None:
        """(verdien i TFM-ID-en, verdien i typefeltet) når de to er uenige.

        Sammenligningen går gjennom samme normalisering som mastera bruker, så
        «samme komponenttype» har én definisjon i verktøyet. Mellomrom og små
        bokstaver skiller ikke to like verdier.
        """
        fra_id, fra_felt = self.komponenttype_kilder(objekt)
        if not fra_id or not fra_felt:
            return None
        if normaliser(fra_id) == normaliser(fra_felt):
            return None
        return fra_id, fra_felt

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

    def uleselige(self) -> dict[str, int]:
        """Per fagmodell: objekter i omfanget med en TFM som ikke lot seg tolke.

        `med_tfm()` returnerer bare det som parset, og sju kontroller leser den.
        Et objekt i `parsefeil` er dermed lest, i omfanget, og likevel usynlig
        for K3 til K9 — uten at noe sier det.

        Bare objekter i omfanget telles. Et objekt utenfor `ifc_klasser` er ikke
        ukontrollert av denne grunnen; det er ikke kontrollert i det hele tatt,
        og det er dekningen som svarer for det.

        Tallet regnes ikke ut på nytt: `parsefeil` er fylt i `bygg` og bæres med.
        """
        ut: dict[str, int] = defaultdict(int)
        for objekt in self.relevante_objekter():
            if objekt.global_id in self.parsefeil:
                ut[objekt.kildefil] += 1
        return dict(ut)

    def med_tfm_verdi(self) -> dict[str, int]:
        """Per fagmodell: objekter i omfanget som HAR en TFM-verdi.

        Skiller «ingen tolkbar TFM» fra «ingen TFM i det hele tatt». Det siste
        er K1s jobb, og en umerket modell skal ikke i tillegg få en advarsel om
        grammatikken.
        """
        ut: dict[str, int] = defaultdict(int)
        for objekt in self.relevante_objekter():
            if objekt.tfm_forekomst:
                ut[objekt.kildefil] += 1
        return dict(ut)

    def unntatte_filer(self) -> list[str]:
        """Fagmodellene oppsettet unntar med vilje.

        Skilles fra de som endte med tomt omfang ved et uhell: bare oppsettet
        vet hvilken av de to det er, og D1 og utskriften trenger begge svar.
        """
        return sorted(f for f in self.kildefiler if self.config.er_unntatt(f))

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

    def er_foringsvei(self, objekt: IfcObjekt, tfm: TfmId | None = None) -> bool:
        """Bærer objektet kurser framfor å ligge på en?

        To uavhengige kjennetegn, og det holder at ett av dem slår til.
        IFC-klassen sier hva eksporten fikk til. Systemkoden sier hva prosjektet
        har bestemt at objektet er — og når de to er uenige, er det prosjektet
        som har svart. En koblingsboks som kom ut som IfcBuildingElementProxy er
        fortsatt en koblingsboks.

        Egen metode, ikke slått sammen med `er_fordeling` til én
        `ligger_pa_kurs`. Kortere hadde det blitt, men når et objekt ikke
        flagges er spørsmålet alltid hvilket av de to unntakene som slo til.
        """
        elektro = self.config.elektro
        if any(objekt.er_av_type(k) for k in elektro.foring_klasser):
            return True
        return tfm is not None and tfm.systemkode in elektro.foring_systemkoder


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
