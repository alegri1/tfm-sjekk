"""Tredje trinn i meldingsstigen (openspec: verdiuttrekk).

Alle disse verdiene ga tidligere samme melding — «følger ikke
TFM-grammatikken. Forventet formen ++NNNNNN=…» — uansett hva som var galt.
"""

from __future__ import annotations

import pytest

from tfm_sjekk.config import Grammatikk
from tfm_sjekk.parser import ParseFeil, monster_for, parse

GYLDIG = "++115080=3600.001.04-JVZ001%JVZ.001.008"


def melding(streng: str, g: Grammatikk | None = None) -> str:
    with pytest.raises(ParseFeil) as feil:
        parse(streng, g or Grammatikk())
    return str(feil.value)


# --- Den løse regexen -----------------------------------------------------


@pytest.mark.parametrize(
    "streng",
    [
        "++11508=3600.001.04-JVZ001",
        "++1150800=3600.001.04-JVZ001",
        "++115080=360.001.04-JVZ001",
        "++115080=3600.1.04-JVZ001",
        "++115080=3600.001.4-JVZ001",
        "++115080=3600.001.04-jvz001",
        "++115080=3600.001.04-JV001",
        "++115080=3600.001.04-JVZ01",
        "++115080=3600.001.04-JVZ001%JVZ.1.008",
    ],
)
def test_los_regex_fanger_innholdsfeil(streng):
    assert monster_for(Grammatikk(), streng=False).match(streng)


@pytest.mark.parametrize("streng", ["Systemair", "3600.001.04", "84 kg", ""])
def test_los_regex_matcher_ikke_fremmede_verdier(streng):
    assert monster_for(Grammatikk(), streng=False).match(streng) is None


def test_de_to_monstrene_beskriver_samme_form():
    """Alt det strenge godtar, godtar også det løse. Ellers ville meldingen
    kunne peke på noe annet enn regelen som avviste verdien."""
    g = Grammatikk()
    for streng in (GYLDIG, "++115080=3600.001.04-JVZ001", "++115080=3600.001.040-JVZ001"):
        if monster_for(g).match(streng):
            assert monster_for(g, streng=False).match(streng), streng


# --- Meldingen navngir delen ----------------------------------------------


def test_feil_sifferantall_oppgir_forventet_og_funnet():
    m = melding("++11508=3600.001.04-JVZ001")
    assert "Plasseringen" in m
    assert "5 siffer" in m and "forventet 6" in m


@pytest.mark.parametrize(
    ("streng", "del_"),
    [
        ("++115080=360.001.04-JVZ001", "Systemkoden"),
        ("++115080=3600.1.04-JVZ001", "Systemets løpenummer"),
        ("++115080=3600.001.4-JVZ001", "Undernummeret"),
        ("++115080=3600.001.04-JV001", "Komponentkoden"),
        ("++115080=3600.001.04-JVZ01", "Komponentens løpenummer"),
        ("++115080=3600.001.04-JVZ001%JVZ.1.008", "Komponenttypens løpenummer"),
        ("++115080=3600.001.04-JVZ001%JVZ.001.08", "Komponenttypens undernummer"),
    ],
)
def test_hver_del_kan_navngis(streng, del_):
    assert del_ in melding(streng)


def test_avvik_i_ulike_deler_gir_ulike_meldinger():
    a = melding("++11508=3600.001.04-JVZ001")
    b = melding("++115080=3600.001.04-JVZ01")
    assert a != b


def test_undernummeret_oppgir_et_intervall():
    """Undernummeret er det eneste med et spenn, ikke ett eksakt antall."""
    assert "forventet 2-3" in melding("++115080=3600.001.4-JVZ001")


def test_sma_bokstaver_i_komponentkoden():
    m = melding("++115080=3600.001.04-jvz001")
    assert "store bokstaver" in m
    assert "siffer" not in m


# --- Første avvik, ikke alle ----------------------------------------------


def test_flere_avvik_gir_det_forste():
    """Både plasseringen og komponentkoden er gale; bare den første omtales."""
    m = melding("++11508=3600.001.04-jvz001")
    assert "Plasseringen" in m
    assert "Komponentkoden" not in m


# --- Forventningen følger konfigurasjonen ---------------------------------


def test_konfigurert_grammatikk_gir_konfigurert_antall():
    g = Grammatikk(plassering_siffer=8)
    m = melding("++115080=3600.001.04-JVZ001", g)
    assert "6 siffer" in m and "forventet 8" in m


# --- De to første trinnene er uendret -------------------------------------


def test_fremmed_verdi_beskrives_fortsatt_som_fremmed():
    assert "ser ikke ut som en TFM-ID" in melding("Systemair")


def test_manglende_markor_navngis_fortsatt():
    assert "Mangler «=»-delen" in melding("++115080-3600.001.04")


def test_generisk_melding_som_siste_utvei():
    """Alle tre markørene finnes, men formen er så forskrudd at heller ikke den
    løse regexen matcher."""
    m = melding("++=-115080.3600")
    assert "følger ikke TFM-grammatikken" in m
