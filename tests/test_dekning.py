"""Tester for dekning (openspec: dekning).

Spørsmålet kontrollen svarer på er hva null funn betyr. Testene her er
scenarioene fra spec-en.
"""

from __future__ import annotations

from conftest import objekt

from tfm_sjekk.config import Konfigurasjon, KontrollOppsett
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle
from tfm_sjekk.modell import Alvorlighet

UTENFOR = ["IfcBuildingElement", "IfcElement", "IfcProduct"]


def utenfor_omfanget(global_id: str, kildefil: str, klasse: str = "IfcWall"):
    o = objekt(tfm=None, global_id=global_id, klasse=klasse, kildefil=kildefil)
    o.ifc_supertyper = UTENFOR
    return o


def d1(kontekst):
    funn, _ = kjor_alle(kontekst)
    return [f for f in funn if f.kontroll == "D1"]


# --- Rapporten sier hvor mye som ble sjekket -------------------------------


def test_dekningen_oppgis_ved_ren_kjoring(config):
    k = Kontekst.bygg([objekt(global_id="a", kildefil="rie.ifc")], config)
    assert k.dekning() == {"rie.ifc": (1, 1)}


def test_dekningen_oppgis_per_fagmodell(config):
    k = Kontekst.bygg(
        [
            objekt(global_id="a", kildefil="rie.ifc"),
            objekt(global_id="b", kildefil="rie.ifc"),
            objekt(global_id="c", kildefil="riv.ifc"),
            utenfor_omfanget("d", "ark.ifc"),
            utenfor_omfanget("e", "ark.ifc", "IfcSlab"),
        ],
        config,
    )
    assert k.dekning() == {"ark.ifc": (0, 2), "rie.ifc": (2, 2), "riv.ifc": (1, 1)}


# --- Tomt omfang i en fagmodell gir et funn --------------------------------


def test_ingen_objekter_i_omfanget_gir_funn(config):
    k = Kontekst.bygg(
        [utenfor_omfanget("a", "ark.ifc"), utenfor_omfanget("b", "ark.ifc", "IfcSlab")], config
    )
    funn = d1(k)
    assert len(funn) == 1
    assert funn[0].alvorlighet is Alvorlighet.ADVARSEL
    assert funn[0].kildefil == "ark.ifc"


def test_en_tom_fagmodell_blant_flere(config):
    k = Kontekst.bygg(
        [
            objekt(global_id="a", kildefil="rie.ifc"),
            objekt(global_id="b", kildefil="riv.ifc"),
            utenfor_omfanget("c", "ark.ifc"),
        ],
        config,
    )
    funn = d1(k)
    assert len(funn) == 1
    assert funn[0].kildefil == "ark.ifc"


def test_modell_uten_objekter_i_det_hele_tatt(config):
    """En fil verktøyet ikke leser noe fra skal behandles likt."""
    k = Kontekst.bygg([], config)
    assert d1(k) == []  # ingen filer å melde om

    k = Kontekst.bygg([utenfor_omfanget("a", "tom.ifc")], config)
    assert len(d1(k)) == 1


# --- Tomt omfang endrer ikke exit-koden ------------------------------------


def test_funnet_er_advarsel_og_teller_ikke_som_feil(config):
    k = Kontekst.bygg([utenfor_omfanget("a", "ark.ifc")], config)
    funn, _ = kjor_alle(k)
    assert [f for f in funn if f.alvorlighet is Alvorlighet.FEIL] == []
    assert any(f.kontroll == "D1" for f in funn)


def test_ekte_feil_i_en_annen_fagmodell_gir_fortsatt_feil(config):
    k = Kontekst.bygg(
        [
            objekt(tfm=None, global_id="a", kildefil="rie.ifc"),  # K1: mangler TFM
            utenfor_omfanget("b", "ark.ifc"),
        ],
        config,
    )
    funn, _ = kjor_alle(k)
    assert any(f.alvorlighet is Alvorlighet.FEIL for f in funn)
    assert any(f.kontroll == "D1" for f in funn)


# --- Funnet peker på årsaken ----------------------------------------------


def test_meldingen_navngir_innstillingen_og_klassene(config):
    k = Kontekst.bygg(
        [utenfor_omfanget("a", "ark.ifc"), utenfor_omfanget("b", "ark.ifc", "IfcSlab")], config
    )
    melding = d1(k)[0].melding
    assert "ifc_klasser" in melding
    assert "IfcWall" in melding and "IfcSlab" in melding


# --- Konfigurerbar som enhver annen kontroll -------------------------------


def test_kontrollen_kan_slas_av(config):
    config.kontroller["D1"] = KontrollOppsett(aktiv=False)
    k = Kontekst.bygg([utenfor_omfanget("a", "ark.ifc")], config)
    assert d1(k) == []


def test_graden_kan_overstyres():
    config = Konfigurasjon()
    config.kontroller["D1"] = KontrollOppsett(alvorlighet=Alvorlighet.FEIL)
    k = Kontekst.bygg([utenfor_omfanget("a", "ark.ifc")], config)
    assert d1(k)[0].alvorlighet is Alvorlighet.FEIL


# --- Modeller med objekter i omfanget skal ikke få funnet ------------------


def test_full_dekning_gir_ingen_funn(config):
    k = Kontekst.bygg([objekt(global_id="a", kildefil="rie.ifc")], config)
    assert d1(k) == []
