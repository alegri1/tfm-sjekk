"""Tester for komponenttype (openspec: komponenttype).

Komponenttypen kan stå to steder — i %-delen av TFM-ID-en og i typefeltet.
Scenarioene her er spec-ens, ett for ett.
"""

from __future__ import annotations

import pytest
from conftest import objekt

from tfm_sjekk.config import Konfigurasjon, KontrollOppsett
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle
from tfm_sjekk.modell import Alvorlighet
from tfm_sjekk.tabeller import TfmMaster

MED_TYPE = "++115080=3600.001.04-JVZ001%JVZ.001.008"
UTEN_TYPE = "++115080=3600.001.04-JVZ001"


def lag(tfm: str | None = MED_TYPE, typefelt: str | None = None, **kw):
    o = objekt(tfm=tfm, **kw)
    o.tfm_type = typefelt
    return o


def funn_for(kontroll: str, objekter, config=None, master=None):
    k = Kontekst.bygg(objekter, config or Konfigurasjon(), master=master)
    funn, _ = kjor_alle(k)
    return [f for f in funn if f.kontroll == kontroll]


# --- Komponenttypen skal være den samme i begge feltene --------------------


def test_de_to_feltene_spriker():
    funn = funn_for("T1", [lag(typefelt="JVZ.001.009")])
    assert len(funn) == 1
    assert funn[0].alvorlighet is Alvorlighet.FEIL
    assert "JVZ.001.009" in funn[0].melding and "JVZ.001.008" in funn[0].melding


def test_de_to_feltene_er_like():
    assert funn_for("T1", [lag(typefelt="JVZ.001.008")]) == []


@pytest.mark.parametrize("typefelt", [" JVZ.001.008 ", "jvz.001.008", "%JVZ.001.008"])
def test_skrivemate_skiller_dem_ikke(typefelt):
    assert funn_for("T1", [lag(typefelt=typefelt)]) == []


# --- Én kilde med forrang -------------------------------------------------


def test_prosentdelen_har_forrang():
    k = Kontekst.bygg([lag(typefelt="JVZ.001.008")], Konfigurasjon())
    assert k.komponenttype_for(k.objekter[0]) == "JVZ.001.008"


def test_typefeltet_er_eneste_kilde():
    o = lag(tfm=UTEN_TYPE, typefelt="JVZ.001.008")
    k = Kontekst.bygg([o], Konfigurasjon())
    assert k.komponenttype_for(o) == "JVZ.001.008"


def test_ingen_av_delene():
    o = lag(tfm=UTEN_TYPE)
    k = Kontekst.bygg([o], Konfigurasjon())
    assert k.komponenttype_for(o) is None
    assert k.komponenttype_spriker(o) is None


# --- Komponenttypen fra typefeltet sjekkes mot mastera --------------------


def test_type_bare_i_typefeltet_ukjent_i_mastera():
    """K7 hoppet før over dette objektet, siden %-delen manglet."""
    master = TfmMaster(kilde="m.csv", systemer={"3600.001.04"}, komponenttyper={"QLF.001.001"})
    funn = funn_for("K7", [lag(tfm=UTEN_TYPE, typefelt="JVZ.001.008")], master=master)
    feil = [f for f in funn if f.alvorlighet is Alvorlighet.FEIL]
    assert len(feil) == 1
    assert "JVZ.001.008" in feil[0].melding


def test_type_bare_i_typefeltet_kjent_i_mastera():
    master = TfmMaster(kilde="m.csv", systemer={"3600.001.04"}, komponenttyper={"JVZ.001.008"})
    funn = funn_for("K7", [lag(tfm=UTEN_TYPE, typefelt="JVZ.001.008")], master=master)
    assert [f for f in funn if f.alvorlighet is Alvorlighet.FEIL] == []


def test_umodellert_teller_ogsa_typer_fra_typefeltet():
    """Motsatt retning: typen er brukt, så mastera skal ikke melde den umodellert."""
    master = TfmMaster(kilde="m.csv", systemer={"3600.001.04"}, komponenttyper={"JVZ.001.008"})
    funn = funn_for("K7", [lag(tfm=UTEN_TYPE, typefelt="JVZ.001.008")], master=master)
    assert [f for f in funn if f.alvorlighet is Alvorlighet.INFO] == []


# --- Et sprik gir ikke funn om mastera i tillegg --------------------------


def test_sprik_melder_bare_spriket():
    master = TfmMaster(kilde="m.csv", systemer={"3600.001.04"}, komponenttyper={"QLF.001.001"})
    objekter = [lag(typefelt="JVZ.001.009")]
    assert len(funn_for("T1", objekter, master=master)) == 1
    k7 = [f for f in funn_for("K7", objekter, master=master) if f.alvorlighet is Alvorlighet.FEIL]
    assert k7 == [], "K7 skal tie når typen er uavklart"


# --- Konfigurerbar som enhver annen kontroll ------------------------------


def test_kontrollen_kan_slas_av():
    config = Konfigurasjon()
    config.kontroller["T1"] = KontrollOppsett(aktiv=False)
    assert funn_for("T1", [lag(typefelt="JVZ.001.009")], config) == []


def test_graden_kan_overstyres():
    config = Konfigurasjon()
    config.kontroller["T1"] = KontrollOppsett(alvorlighet=Alvorlighet.ADVARSEL)
    funn = funn_for("T1", [lag(typefelt="JVZ.001.009")], config)
    assert funn[0].alvorlighet is Alvorlighet.ADVARSEL


# --- Fella som sprang da verdien ble tatt i bruk --------------------------


def test_tfm_er_ikke_lenger_kandidatnavn_for_typen(tmp_path):
    """«TFM» er forekomstens eget kandidatnavn. Sto det i typelista, ble hele
    TFM-ID-en lest som komponenttype, og T1 meldte sprik på hvert objekt."""
    from fixtures.syntetisk import lag_modell

    from tfm_sjekk.ifc import les_modell

    sti = lag_modell([("IfcFlowTerminal", MED_TYPE)], tmp_path / "vanlig.ifc")
    o = les_modell(sti)[0]
    assert o.tfm_type is None
    assert funn_for("T1", [o]) == []
