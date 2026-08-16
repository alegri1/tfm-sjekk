"""Parser for TFM-ID-er.

§6: «Start med regex; bytt til grammatikk først når reglene viser seg mer
sammensatte enn ventet.» Regexen bygges fra `Grammatikk` slik at sifferantall
er data og ikke kode — bytte til lark senere skal ikke endre `TfmId`.
"""

from __future__ import annotations

import re
from functools import lru_cache

from tfm_sjekk.config import Grammatikk
from tfm_sjekk.modell import TfmId


class ParseFeil(ValueError):
    """Strengen er ikke en gyldig TFM-ID. Meldingen er på norsk og går rett
    i rapporten (K2)."""


def bygg_monster(g: Grammatikk) -> re.Pattern[str]:
    """Setter sammen regexen fra konfigurert sifferantall."""
    type_del = (
        rf"%(?P<typekode>[A-ZÆØÅ]{{{g.komponentkode_bokstaver}}})"
        rf"\.(?P<type_lopenummer>\d{{{g.type_lopenummer_siffer}}})"
        rf"\.(?P<type_undernummer>\d{{{g.type_undernummer_siffer}}})"
    )
    if not g.krev_komponenttype:
        type_del = f"(?:{type_del})?"

    monster = (
        (
            rf"^\+\+(?P<plassering>\d{{{g.plassering_siffer}}})"
            rf"=(?P<systemkode>\d{{{g.systemkode_siffer}}})"
            rf"\.(?P<system_lopenummer>\d{{{g.system_lopenummer_siffer}}})"
            rf"\.(?P<undernummer>\d{{{g.undernummer_siffer_min},{g.undernummer_siffer_maks}}})"
            rf"-(?P<komponentkode>[A-ZÆØÅ]{{{g.komponentkode_bokstaver}}})"
            rf"(?P<komponent_lopenummer>\d{{{g.komponent_lopenummer_siffer}}})"
        )
        + type_del
        + r"$"
    )

    return re.compile(monster)


@lru_cache(maxsize=32)
def _kompilert(grammatikk_json: str) -> re.Pattern[str]:
    return bygg_monster(Grammatikk.model_validate_json(grammatikk_json))


def monster_for(g: Grammatikk) -> re.Pattern[str]:
    """Cachet variant — parseren kalles én gang per objekt i store modeller."""
    return _kompilert(g.model_dump_json())


def parse(streng: str, g: Grammatikk | None = None) -> TfmId:
    """Parser én TFM-ID. Kaster `ParseFeil` med norsk melding.

    >>> parse("++115080=3600.001.04-JVZ001%JVZ.001.008").komponentforekomst
    'JVZ001'
    """
    g = g or Grammatikk()
    raa = streng.strip()
    if not raa:
        raise ParseFeil("Tom TFM-verdi")

    treff = monster_for(g).match(raa)
    if treff is None:
        raise ParseFeil(_forklar(raa, g))

    d = treff.groupdict()
    return TfmId(raa=raa, **d)


def parse_valgfri(streng: str | None, g: Grammatikk | None = None) -> TfmId | None:
    """Som `parse`, men returnerer None i stedet for å kaste."""
    if streng is None:
        return None
    try:
        return parse(streng, g)
    except ParseFeil:
        return None


def _forklar(raa: str, g: Grammatikk) -> str:
    """Peker på hvilken del som ryker.

    En melding som «forventet 6 siffer etter ++, fant 5» er verdt mer i en
    BCF-sak enn «matcher ikke mønsteret».
    """
    deler = [
        ("++", r"\+\+", f"plassering ({g.plassering_siffer} siffer)"),
        ("=", "=", f"systemforekomst ({g.systemkode_siffer} siffer + løpenummer + undernummer)"),
        ("-", "-", f"komponentforekomst ({g.komponentkode_bokstaver} bokstaver + løpenummer)"),
    ]
    for prefiks, _, beskrivelse in deler:
        if prefiks not in raa:
            return f"Mangler «{prefiks}»-delen: {beskrivelse}"

    if not raa.startswith("++"):
        return "TFM-ID må starte med «++»"

    if g.krev_komponenttype and "%" not in raa:
        return "Mangler «%»-delen (komponenttype)"

    return (
        f"«{raa}» følger ikke TFM-grammatikken. Forventet formen "
        f"++{'N' * g.plassering_siffer}"
        f"={'N' * g.systemkode_siffer}"
        f".{'N' * g.system_lopenummer_siffer}"
        f".{'N' * g.undernummer_siffer_min}"
        f"-{'B' * g.komponentkode_bokstaver}{'N' * g.komponent_lopenummer_siffer}"
        f" (N=siffer, B=bokstav)"
    )
