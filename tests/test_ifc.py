"""Tester for IFC-lesing mot syntetiske modeller (§7)."""

from __future__ import annotations

import pytest
from fixtures.syntetisk import GYLDIG, lag_elektromodell, lag_modell

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


def test_leser_koblingsgrafen_gjennom_portene(tmp_path):
    """Porten er kanten mellom to objekter (K8b/K8c)."""
    sti = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [
                    {"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010", "kurs": "Kurs 12"}
                ],
            }
        ],
        tmp_path / "elektro.ifc",
    )
    objekter = {o.navn: o for o in les_modell(sti)}

    tavle, lampe = objekter["Fordeling 1"], objekter["Objekt 1.1"]
    assert lampe.global_id in tavle.tilkoblet
    assert tavle.global_id in lampe.tilkoblet
    assert [str(krets) for krets in lampe.kretser] == ["Kurs 12"]


def test_porter_er_ikke_objekter(tmp_path):
    """IfcDistributionPort er en IfcProduct, men skal ikke telles som et
    kontrollert objekt — den bærer ingen TFM og ville forurenset K1."""
    sti = lag_elektromodell(
        [{"navn": "F1", "tfm": None, "objekter": [{"klasse": "IfcLamp", "tfm": None}]}],
        tmp_path / "porter.ifc",
    )
    klasser = {o.ifc_klasse for o in les_modell(sti)}
    assert "IfcDistributionPort" not in klasser
    assert klasser == {"IfcElectricDistributionBoard", "IfcLamp"}


def test_fordelinger_bygges_i_konteksten(tmp_path):
    sti = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [
                    {"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010"},
                    {"klasse": "IfcLamp", "tfm": "++115080=4310.001.13-QLF011"},
                ],
            }
        ],
        tmp_path / "graf.ifc",
    )
    kontekst = Kontekst.bygg(les_modell(sti), Konfigurasjon())
    assert len(kontekst.fordelinger) == 1
    (medlemmer,) = kontekst.fordelinger.values()
    assert len(medlemmer) == 2


def test_federering_parallelt_gir_samme_resultat(tmp_path):
    a = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "a.ifc")
    b = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "b.ifc")
    sekvensielt = les_modeller([a, b], parallelt=False)
    parallelt = les_modeller([a, b], parallelt=True)
    assert [o.global_id for o in sekvensielt] == [o.global_id for o in parallelt]
