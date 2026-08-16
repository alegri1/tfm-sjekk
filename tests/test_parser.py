"""Tester for TFM-parseren, inkludert property-based testing (§7)."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from tfm_sjekk.config import Grammatikk
from tfm_sjekk.parser import ParseFeil, parse

GYLDIG = "++115080=3600.001.04-JVZ001%JVZ.001.008"


def test_parser_statsbyggs_eksempel():
    """Eksempelet fra §1: en tilluftsvifte."""
    tfm = parse(GYLDIG)
    assert tfm.plassering == "115080"
    assert tfm.systemkode == "3600"
    assert tfm.system_lopenummer == "001"
    assert tfm.undernummer == "04"
    assert tfm.komponentkode == "JVZ"
    assert tfm.komponent_lopenummer == "001"
    assert tfm.typekode == "JVZ"
    assert tfm.systemforekomst == "3600.001.04"
    assert tfm.komponentforekomst == "JVZ001"
    assert tfm.komponenttype == "JVZ.001.008"


def test_komponenttype_er_valgfri_som_standard():
    tfm = parse("++115080=3600.001.04-JVZ001")
    assert tfm.typekode is None
    assert tfm.komponenttype is None


def test_komponenttype_kan_kreves():
    g = Grammatikk(krev_komponenttype=True)
    with pytest.raises(ParseFeil, match="komponenttype"):
        parse("++115080=3600.001.04-JVZ001", g)


def test_undernummer_tar_bade_to_og_tre_siffer():
    assert parse("++115080=3600.001.04-JVZ001").undernummer == "04"
    assert parse("++115080=3600.001.004-JVZ001").undernummer == "004"


def test_elektro_gjenkjennes_pa_forste_siffer():
    """NS 3451 kapittel 4 og 5 — se K8."""
    assert parse("++115080=4300.001.12-QLF001").er_elektro
    assert parse("++115080=5400.001.12-QLF001").er_elektro
    assert not parse(GYLDIG).er_elektro


@pytest.mark.parametrize(
    "streng,forventet_i_melding",
    [
        ("", "Tom"),
        ("115080=3600.001.04-JVZ001", r"\+\+"),
        ("++115080-JVZ001", "="),
        ("++115080=3600.001.04", "-"),
        ("++11508=3600.001.04-JVZ001", "grammatikken"),  # 5 siffer i plassering
        ("++115080=360.001.04-JVZ001", "grammatikken"),  # 3 siffer i systemkode
        ("++115080=3600.001.04-JV001", "grammatikken"),  # 2 bokstaver
        ("++115080=3600.001.04-jvz001", "grammatikken"),  # små bokstaver
    ],
)
def test_avviser_ugyldige_strenger(streng, forventet_i_melding):
    with pytest.raises(ParseFeil, match=forventet_i_melding):
        parse(streng)


def test_grammatikken_er_konfigurerbar():
    """§14: TFM-tolkningene varierer — sifferantall må være data."""
    g = Grammatikk(plassering_siffer=4)
    assert parse("++1150=3600.001.04-JVZ001", g).plassering == "1150"
    with pytest.raises(ParseFeil):
        parse("++115080=3600.001.04-JVZ001", g)


# --- Property-based (§7) -----------------------------------------------------

BOKSTAVER = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=3, max_size=3)
SIFFER = st.text(alphabet="0123456789", min_size=1, max_size=1)


@st.composite
def gyldig_tfm(draw):
    """Genererer TFM-strenger fra grammatikken."""

    def siffer(n: int) -> str:
        return "".join(draw(SIFFER) for _ in range(n))

    return (
        f"++{siffer(6)}={siffer(4)}.{siffer(3)}.{siffer(2)}"
        f"-{draw(BOKSTAVER)}{siffer(3)}"
        f"%{draw(BOKSTAVER)}.{siffer(3)}.{siffer(3)}"
    )


@given(gyldig_tfm())
def test_genererte_gyldige_strenger_parser(streng):
    assert parse(streng).raa == streng


@given(gyldig_tfm(), st.integers(min_value=0, max_value=40))
def test_muterte_strenger_avvises(streng, posisjon):
    """Bytt ett tegn mot noe som aldri er lovlig, og verifiser at det ryker."""
    if posisjon >= len(streng):
        return
    mutert = streng[:posisjon] + "!" + streng[posisjon + 1 :]
    with pytest.raises(ParseFeil):
        parse(mutert)
