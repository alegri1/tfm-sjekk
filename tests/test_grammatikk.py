"""Tester for evnen «grammatikk» — hvilke deler en TFM-ID må ha.

Fra §11-samtalen 2026-08-20: en tidlig modell har ikke krav til plassering.
Byggnummeret er ikke bestemt ennå, mens systemet og komponenten er merket og
skal kunne kontrolleres.
"""

from __future__ import annotations

import pytest

from tfm_sjekk.config import Grammatikk, Konfigurasjon
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle
from tfm_sjekk.kontroller.k6_unikhet import K6Unikhet
from tfm_sjekk.modell import IfcObjekt
from tfm_sjekk.parser import ParseFeil, ligner_tfm_id, parse

TIDLIG = Grammatikk(krev_plassering=False)
STANDARD = Grammatikk()


def objekt(global_id: str, tfm: str, kildefil: str = "rie.ifc") -> IfcObjekt:
    return IfcObjekt(
        global_id=global_id,
        ifc_klasse="IfcFlowTerminal",
        ifc_supertyper=["IfcProduct"],
        kildefil=kildefil,
        tfm_forekomst=tfm,
    )


# --- Plassering skal kunne gjøres valgfri ---


def test_tidligfase_godtar_id_uten_plassering():
    tfm = parse("=3600.001.04-JVZ001", TIDLIG)
    assert tfm.plassering is None
    assert tfm.systemforekomst == "3600.001.04"
    assert tfm.komponentforekomst == "JVZ001"


def test_plassering_leses_fortsatt_nar_den_er_med():
    tfm = parse("++115080=3600.001.04-JVZ001", TIDLIG)
    assert tfm.plassering == "115080"


def test_standardoppsettet_avviser_id_uten_plassering():
    """Låser at endringen er usynlig for alle som ikke ber om den."""
    with pytest.raises(ParseFeil) as feil:
        parse("=3600.001.04-JVZ001", STANDARD)
    assert "++" in str(feil.value)


def test_ugyldig_plassering_avvises_selv_nar_delen_er_valgfri():
    """Valgfri betyr at delen kan utelates, ikke at den kan være feil."""
    with pytest.raises(ParseFeil) as feil:
        parse("++11508=3600.001.04-JVZ001", TIDLIG)
    assert "Plasseringen" in str(feil.value)
    assert "5 siffer" in str(feil.value)


def test_komponenttypen_virker_fortsatt_uten_plassering():
    tfm = parse("=3600.001.04-JVZ001%JVZ.001.008", TIDLIG)
    assert tfm.plassering is None
    assert tfm.komponenttype == "JVZ.001.008"


# --- De bærende delene skal ikke kunne gjøres valgfrie ---


def test_bare_de_perifere_delene_har_en_bryter():
    felter = set(Grammatikk.model_fields)
    assert {"krev_plassering", "krev_komponenttype"} <= felter
    assert not [
        f
        for f in felter
        if f.startswith("krev_") and f not in {"krev_plassering", "krev_komponenttype"}
    ]


# --- Identiteten bygges av delene som finnes ---


def test_med_og_uten_plassering_er_ulike_komponenter():
    med = parse("++115080=3600.001.04-JVZ001", TIDLIG)
    uten = parse("=3600.001.04-JVZ001", TIDLIG)
    assert med.global_forekomst != uten.global_forekomst


def test_ulikt_bygg_er_ikke_duplikat():
    a = parse("++115080=3600.001.04-JVZ001", TIDLIG)
    b = parse("++115081=3600.001.04-JVZ001", TIDLIG)
    assert a.global_forekomst != b.global_forekomst


def test_to_like_uten_plassering_gir_samme_nokkel():
    a = parse("=3600.001.04-JVZ001", TIDLIG)
    b = parse("=3600.001.04-JVZ001", TIDLIG)
    assert a.global_forekomst == b.global_forekomst


def test_k6_finner_duplikat_uten_plassering_pa_tvers_av_fagmodeller():
    config = Konfigurasjon(grammatikk=TIDLIG)
    k = Kontekst.bygg(
        [
            objekt("a", "=3600.001.04-JVZ001", "rie.ifc"),
            objekt("b", "=3600.001.04-JVZ001", "riv.ifc"),
        ],
        config,
    )
    funn = K6Unikhet().kjor(k)
    assert len(funn) == 2
    assert "rie.ifc" in funn[0].melding
    assert "riv.ifc" in funn[0].melding


def test_k6_melder_ikke_duplikat_for_to_bygg():
    config = Konfigurasjon(grammatikk=TIDLIG)
    k = Kontekst.bygg(
        [
            objekt("a", "++115080=3600.001.04-JVZ001"),
            objekt("b", "++115081=3600.001.04-JVZ001"),
        ],
        config,
    )
    assert K6Unikhet().kjor(k) == []


def test_k6_melder_ikke_duplikat_for_med_og_uten_plassering():
    config = Konfigurasjon(grammatikk=TIDLIG)
    k = Kontekst.bygg(
        [
            objekt("a", "++115080=3600.001.04-JVZ001"),
            objekt("b", "=3600.001.04-JVZ001"),
        ],
        config,
    )
    assert K6Unikhet().kjor(k) == []


# --- Meldingen skal ikke etterlyse en del som ikke kreves ---


def test_valgfri_del_nevnes_ikke_i_meldingen():
    with pytest.raises(ParseFeil) as feil:
        parse("=3600.001.04-JVZ0001", TIDLIG)
    melding = str(feil.value)
    assert "løpenummer" in melding
    assert "lassering" not in melding


def test_pakrevd_del_navngis_som_for():
    with pytest.raises(ParseFeil) as feil:
        parse("=3600.001.04-JVZ001", STANDARD)
    assert "plassering" in str(feil.value)


def test_formmalen_viser_grammatikken_som_gjelder():
    """«++x=y-z» har alle tre markørene, så den når fram til formmalen.

    En verdi med bare to markører stoppes tidligere, av den bedre meldingen om
    hvilken markør som mangler — det er meningen, men da prøves ikke dette.
    """
    with pytest.raises(ParseFeil) as feil:
        parse("++x=y-z", TIDLIG)
    melding = str(feil.value)
    assert "=NNNN.NNN.NN-BBBNNN" in melding
    assert "++NNNNNN" not in melding


def test_formmalen_har_plassering_nar_den_kreves():
    with pytest.raises(ParseFeil) as feil:
        parse("++x=y-z", STANDARD)
    assert "++NNNNNN=NNNN.NNN.NN-BBBNNN" in str(feil.value)


# --- Gjenkjenning og formkrav skal ikke gli fra hverandre ---


def test_id_uten_plassering_gjenkjennes_som_tfm_id():
    assert ligner_tfm_id("=3600.001.04-JVZ001")


def test_fremmed_verdi_er_fortsatt_fremmed():
    assert not ligner_tfm_id("Systemair")


# --- Ingen kontroll skal kaste på en manglende plassering ---


def test_hele_kontrollsettet_taler_en_modell_uten_plassering():
    config = Konfigurasjon(grammatikk=TIDLIG)
    k = Kontekst.bygg(
        [
            objekt("a", "=3600.001.04-JVZ001"),
            objekt("b", "=4310.001.12-QLF001"),
            objekt("c", "=4310.001.00-QLF002"),
        ],
        config,
    )
    funn, _hoppet_over = kjor_alle(k)
    assert all(f.melding for f in funn)
