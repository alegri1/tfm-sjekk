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


def kjor_alle(k: Kontekst) -> tuple[list[Funn], list[Kontroll]]:
    """Kjører alle aktive kontroller.

    Returnerer (funn, hoppet_over). Hoppet over = deaktivert i config,
    ikke implementert ennå, eller mangler kodetabell/master.
    """
    funn: list[Funn] = []
    hoppet_over: list[Kontroll] = []

    for kontroll in _REGISTER:
        if not kontroll.aktiv(k):
            hoppet_over.append(kontroll)
            continue
        if kontroll.krever_kodetabell and k.systemtabell is None and k.komponenttabell is None:
            hoppet_over.append(kontroll)
            continue
        if kontroll.krever_master and k.master is None:
            hoppet_over.append(kontroll)
            continue
        funn.extend(kontroll.kjor(k))

    funn.sort(key=Funn.sorteringsnokkel)
    return funn, hoppet_over
