"""Kontrollrammeverket.

Hver kontroll er en ren funksjon `Kontekst -> list[Funn]`. Ingen kontroll
leser filer, parser TFM-strenger eller kjenner til rapportformatene — alt
det er gjort før den kalles.

Kontrollene kjøres sekvensielt i registreringsrekkefølge. Det er et bevisst
valg: de er raske nok til at parallellitet ikke lønner seg, og deterministisk
rekkefølge er en forutsetning for golden files (§7).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.modell import Alvorlighet, Funn


class Kontroll(ABC):
    """Basis for K1–K9."""

    id: str
    tittel: str
    standard_alvorlighet: Alvorlighet = Alvorlighet.FEIL
    implementert: bool = True
    krever_kodetabell: bool = False
    krever_master: bool = False

    @abstractmethod
    def kjor(self, k: Kontekst) -> list[Funn]:
        """Returnerer funn. Tom liste = alt i orden."""

    def alvorlighet(self, k: Kontekst) -> Alvorlighet:
        """Konfigurasjonen kan overstyre standardgraden (§4)."""
        return k.config.oppsett_for(self.id).alvorlighet or self.standard_alvorlighet

    def aktiv(self, k: Kontekst) -> bool:
        return k.config.oppsett_for(self.id).aktiv and self.implementert

    def funn(self, k: Kontekst, melding: str, **kwargs) -> Funn:
        return Funn(kontroll=self.id, alvorlighet=self.alvorlighet(k), melding=melding, **kwargs)


_REGISTER: list[Kontroll] = []


def registrer(klasse: type[Kontroll]) -> type[Kontroll]:
    """Dekorator. Registreringsrekkefølgen er kjørerekkefølgen."""
    _REGISTER.append(klasse())
    return klasse


def alle_kontroller() -> list[Kontroll]:
    return list(_REGISTER)


class Hoppgrunn(Enum):
    """Hvorfor en kontroll ikke kjørte.

    To deler: en kort grunn, og hva som skal til. Delt fordi de leses ulikt —
    grunnen skal kunne stå på samme linje som kontroll-ID-en, og rådet under.
    Slått sammen ble linja 140 tegn med to tankestreker i, og tre kontroller
    gjentok den samme setningen. Det så man først ved å kjøre.

    Teksten står her og ingen andre steder. Både konsollen og HTML-rapporten
    leser den herfra — sto den to steder, ville de før eller siden blitt
    uenige, og det mønsteret har bitt i dette prosjektet flere ganger.

    Rådet navngir både flagget og oppsettnøkkelen. Meldingene leses av en
    BIM-koordinator, ikke av en utvikler, og forskjellen mellom «mangler
    kodetabell» og «oppgi --systemtabell» er forskjellen mellom å lete i
    dokumentasjonen og å rette én linje.
    """

    IKKE_IMPLEMENTERT = ("ikke implementert ennå", "")
    SLATT_AV = ("slått av i tfm-sjekk.toml", "")
    MANGLER_KODETABELL = (
        "ingen kodetabell",
        "Oppgi --systemtabell eller --komponenttabell, eller sett dem i tfm-sjekk.toml.",
    )
    MANGLER_MASTER = (
        "ingen TFM-master",
        "Oppgi --master, eller sett «tfm_master» i tfm-sjekk.toml.",
    )

    def __init__(self, tekst: str, raad: str) -> None:
        self.tekst = tekst
        self.raad = raad

    def __str__(self) -> str:
        return self.tekst


def _hoppgrunn(kontroll: Kontroll, k: Kontekst) -> Hoppgrunn | None:
    """Grunnen til at kontrollen ikke skal kjøre, eller None.

    REKKEFØLGEN ER BETYDNINGEN. En kontroll som både er slått av og mangler
    tabell skal melde at den er slått av: det er valget brukeren tok, og det
    er den opplysningen hun kan handle på. Snus rekkefølgen, får hun beskjed
    om å skaffe data hun bevisst har valgt bort.
    """
    if not kontroll.implementert:
        return Hoppgrunn.IKKE_IMPLEMENTERT
    if not kontroll.aktiv(k):
        return Hoppgrunn.SLATT_AV
    if kontroll.krever_kodetabell and k.systemtabell is None and k.komponenttabell is None:
        return Hoppgrunn.MANGLER_KODETABELL
    if kontroll.krever_master and k.master is None:
        return Hoppgrunn.MANGLER_MASTER
    return None


def kjor_alle(k: Kontekst) -> tuple[list[Funn], list[tuple[Kontroll, Hoppgrunn]]]:
    """Kjører alle aktive kontroller.

    Returnerer (funn, hoppet_over), der hoppet_over bærer GRUNNEN sammen med
    kontrollen. Tre helt ulike årsaker fantes her fra før, og de falt sammen
    til ett ord på vei ut — for den som leser er de motsatte handlinger: la det
    være, skaff dataene, vent på en senere utgave.

    Grunnen følger med herfra framfor å regnes ut på nytt av den som skriver
    meldingen. Regnet ut to steder ville betingelsene kunnet bli uenige.
    """
    funn: list[Funn] = []
    hoppet_over: list[tuple[Kontroll, Hoppgrunn]] = []

    for kontroll in _REGISTER:
        grunn = _hoppgrunn(kontroll, k)
        if grunn is not None:
            hoppet_over.append((kontroll, grunn))
            continue
        funn.extend(kontroll.kjor(k))

    funn.sort(key=Funn.sorteringsnokkel)
    return funn, hoppet_over
