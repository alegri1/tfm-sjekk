"""Tester for IFC-lesing mot syntetiske modeller (§7)."""

from __future__ import annotations

import pytest
from fixtures.syntetisk import GYLDIG, lag_modell

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.ifc import les_modell, les_modeller
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle


@pytest.fixture
def modell(tmp_path):
    return lag_modell(
        [
            ("IfcFlowTerminal", GYLDIG),
            ("IfcFlowTerminal", "++11508=3600.001.04-JVZ001"),  # for få siffer
            ("IfcFlowTerminal", None),  # uten pset
        ],
        tmp_path / "test.ifc",
    )


def test_leser_alle_produkter(modell):
    objekter = les_modell(modell)
    assert len(objekter) == 3


def test_henter_tfm_fra_pset(modell):
    objekter = les_modell(modell)
    verdier = {o.tfm_forekomst for o in objekter}
    assert GYLDIG in verdier
    assert None in verdier


def test_fyller_arvekjeden(modell):
    objekt = les_modell(modell)[0]
    assert "IfcDistributionElement" in objekt.ifc_supertyper
    assert "IfcProduct" in objekt.ifc_supertyper


def test_kildefil_settes(modell):
    assert all(o.kildefil == "test.ifc" for o in les_modell(modell))


def test_ende_til_ende_gir_forventede_funn(modell):
    kontekst = Kontekst.bygg(les_modell(modell), Konfigurasjon())
    funn, _ = kjor_alle(kontekst)
    kontroller = {f.kontroll for f in funn}
    assert "K1" in kontroller  # objektet uten pset
    assert "K2" in kontroller  # objektet med feil sifferantall


def test_ifc2x3_leses(tmp_path):
    """§3 krever både IFC 2x3 og IFC4."""
    sti = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "gammel.ifc", schema="IFC2X3")
    objekter = les_modell(sti)
    assert len(objekter) == 1
    assert objekter[0].tfm_forekomst == GYLDIG


def test_federering_slar_sammen_filer(tmp_path):
    a = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "rie.ifc")
    b = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "riv.ifc")

    objekter = les_modeller([a, b], parallelt=False)
    assert len(objekter) == 2
    assert {o.kildefil for o in objekter} == {"rie.ifc", "riv.ifc"}

    # Samme komponentforekomst i to fagmodeller — dette er K6-tilfellet.
    funn, _ = kjor_alle(Kontekst.bygg(objekter, Konfigurasjon()))
    assert any(f.kontroll == "K6" for f in funn)


def test_federering_parallelt_gir_samme_resultat(tmp_path):
    a = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "a.ifc")
    b = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "b.ifc")
    sekvensielt = les_modeller([a, b], parallelt=False)
    parallelt = les_modeller([a, b], parallelt=True)
    assert [o.global_id for o in sekvensielt] == [o.global_id for o in parallelt]
