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

# Strukturmarkørene i en TFM-ID. Samme tre brukes tre steder: i mønsteret
# under, i formtesten, og i feilforklaringen — så de ikke kan komme i utakt.
MARKORER = ("++", "=", "-")


def ligner_tfm_id(streng: str) -> bool:
    """Er strengen gjenkjennelig som en TFM-ID, om enn ødelagt?

    Sann når høyst én av strukturmarkørene mangler. Det er linja der parseren
    kan navngi delen som mangler — og der en anvisning derfor er verdt å følge.
    Under den er det ærlige svaret at strengen ikke ser ut som en TFM-ID.

    Målt mot fabrikatnavn, modellbetegnelser, vekt, kommentarer og interne
    merker: ingen av dem kommer gjennom. Målt mot TFM-ID-er ødelagt på fem
    ulike måter: alle godtas.

    Brukes to steder — som port for en verdi verktøyet har gjettet seg til, og
    som valg av hvor spesifikk en feilmelding kan være. Én dom, to kall.
    """
    raa = streng.strip()
    return sum(markor in raa for markor in MARKORER) >= len(MARKORER) - 1


def ligner_komponenttype(streng: str) -> bool:
    """Er strengen gjenkjennelig som en komponenttype, altså «JVZ.001.008»?

    Bokstaver, punktum, siffer. Fabrikatnavn og modellbetegnelser har ikke den
    formen, og det er nok til å skille dem fra hverandre.
    """
    return bool(re.match(r"^[A-ZÆØÅa-zæøå]{2,}\.\d", streng.strip()))


def mmi_niva(verdi: str | None) -> str | None:
    """Nivået i en MMI-verdi, eller None hvis verdien ikke er en nivåangivelse.

    «MMI 300», «mmi300» og «300» er samme nivå. «sjekket av RIE 12.03» er ikke
    et nivå i det hele tatt — den gamle regelen trakk ut alle sifre og gjorde
    den om til «1203», en dato forkledd som modenhetsgrad.

    Ligger her framfor i K9 fordi loaderen trenger samme dom når den vurderer
    en gjettet verdi. To definisjoner ville før eller siden vært uenige.
    """
    if verdi is None:
        return None
    tekst = verdi.strip()
    treff = re.fullmatch(r"(?:mmi[\s:-]*)?(\d+)", tekst, flags=re.IGNORECASE)
    if treff:
        return treff.group(1)
    # Ingen siffer i det hele tatt: prosjektet kan bruke en skala vi ikke
    # kjenner, og da er ordet i seg selv nivået.
    if tekst and not any(tegn.isdigit() for tegn in tekst):
        return tekst.upper()
    return None


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
    if not ligner_tfm_id(raa):
        # Under formtesten vet vi ikke hvilken del som mangler — vi vet bare at
        # dette neppe er en TFM-ID. Å peke på «++»-delen her ville vært en
        # presis anvisning om et felt som aldri inneholdt en TFM-ID.
        return (
            f"«{raa}» ser ikke ut som en TFM-ID. Sjekk at riktig felt er lest — "
            f"forventet formen ++NNNNNN=NNNN.NNN.NN-BBBNNN."
        )

    beskrivelser = {
        "++": f"plassering ({g.plassering_siffer} siffer)",
        "=": f"systemforekomst ({g.systemkode_siffer} siffer + løpenummer + undernummer)",
        "-": f"komponentforekomst ({g.komponentkode_bokstaver} bokstaver + løpenummer)",
    }
    for markor in MARKORER:
        if markor not in raa:
            return f"Mangler «{markor}»-delen: {beskrivelser[markor]}"

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
