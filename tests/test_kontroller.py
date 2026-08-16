"""Tester for K1–K8. Hver kontroll isolert (§7).

Merk at ingen av disse trenger en IFC-fil — det er gevinsten ved at
`Kontekst` er ren data. IFC-lesingen testes for seg i `test_ifc.py`.
"""

from __future__ import annotations

from conftest import GYLDIG, objekt

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle
from tfm_sjekk.modell import Alvorlighet


def funn_for(kontroll: str, kontekst: Kontekst):
    funn, _ = kjor_alle(kontekst)
    return [f for f in funn if f.kontroll == kontroll]


def test_k1_flagger_objekt_uten_tfm(config):
    k = Kontekst.bygg([objekt(tfm=None)], config)
    assert len(funn_for("K1", k)) == 1


def test_k1_ignorerer_klasser_utenfor_omfanget(config):
    utenfor = objekt(tfm=None, klasse="IfcWall")
    utenfor.ifc_supertyper = ["IfcBuildingElement", "IfcElement", "IfcProduct"]
    k = Kontekst.bygg([utenfor], config)
    assert funn_for("K1", k) == []


def test_k1_matcher_pa_arvekjeden(config):
    """IfcAirTerminal er ikke listet i config, men arver IfcFlowTerminal."""
    arvet = objekt(tfm=None, klasse="IfcAirTerminal")
    arvet.ifc_supertyper = ["IfcFlowTerminal", "IfcDistributionElement", "IfcProduct"]
    k = Kontekst.bygg([arvet], config)
    assert len(funn_for("K1", k)) == 1


def test_k2_flagger_syntaksfeil(config):
    k = Kontekst.bygg([objekt(tfm="++11508=3600.001.04-JVZ001")], config)
    funn = funn_for("K2", k)
    assert len(funn) == 1
    assert funn[0].alvorlighet is Alvorlighet.FEIL


def test_k2_er_stille_pa_gyldig_verdi(config):
    k = Kontekst.bygg([objekt()], config)
    assert funn_for("K2", k) == []


def test_k3_flagger_ukjent_systemkode(config, systemtabell, komponenttabell):
    k = Kontekst.bygg(
        [objekt(tfm="++115080=9999.001.04-JVZ001")],
        config,
        systemtabell=systemtabell,
        komponenttabell=komponenttabell,
    )
    assert len(funn_for("K3", k)) == 1


def test_k4_advarer_om_overordnet_kode(config, systemtabell):
    """PA 0805-eksempelet: 2300 skal ikke brukes når 2310/2320 finnes."""
    k = Kontekst.bygg(
        [objekt(tfm="++115080=2300.001.04-JVZ001")], config, systemtabell=systemtabell
    )
    funn = funn_for("K4", k)
    assert len(funn) == 1
    assert funn[0].alvorlighet is Alvorlighet.ADVARSEL
    assert "2310" in funn[0].melding


def test_k4_er_stille_pa_mest_spesifikk_kode(config, systemtabell):
    k = Kontekst.bygg(
        [objekt(tfm="++115080=2310.001.04-JVZ001")], config, systemtabell=systemtabell
    )
    assert funn_for("K4", k) == []


def test_k5_flagger_ukjent_komponentkode(config, komponenttabell):
    k = Kontekst.bygg(
        [objekt(tfm="++115080=3600.001.04-XXX001")], config, komponenttabell=komponenttabell
    )
    assert len(funn_for("K5", k)) == 1


def test_k6_finner_duplikat_i_en_fil(config):
    k = Kontekst.bygg([objekt(global_id="a"), objekt(global_id="b")], config)
    funn = funn_for("K6", k)
    assert len(funn) == 2  # begge objektene rapporteres
    assert "JVZ001" in funn[0].melding


def test_k6_finner_duplikat_pa_tvers_av_fagmodeller(config):
    """Den relasjonelle kontrollen IDS ikke kan uttrykke (§2)."""
    k = Kontekst.bygg(
        [
            objekt(global_id="a", kildefil="rie.ifc"),
            objekt(global_id="b", kildefil="riv.ifc"),
        ],
        config,
    )
    funn = funn_for("K6", k)
    assert len(funn) == 2
    assert "rie.ifc" in funn[0].melding and "riv.ifc" in funn[0].melding


def test_k6_godtar_samme_lopenummer_i_ulike_bygg(config):
    k = Kontekst.bygg(
        [
            objekt(global_id="a", tfm="++115080=3600.001.04-JVZ001"),
            objekt(global_id="b", tfm="++115081=3600.001.04-JVZ001"),
        ],
        config,
    )
    assert funn_for("K6", k) == []


def test_k8_krever_kursnummer_pa_elektro(config):
    k = Kontekst.bygg([objekt(tfm="++115080=4300.001.00-QLF001")], config)
    funn = funn_for("K8", k)
    assert len(funn) == 1
    assert "kurs" in funn[0].melding


def test_k8_ignorerer_ikke_elektro(config):
    k = Kontekst.bygg([objekt(tfm="++115080=3600.001.00-JVZ001")], config)
    assert funn_for("K8", k) == []


def test_k7_og_k9_hoppes_over_inntil_de_er_implementert(config):
    _, hoppet_over = kjor_alle(Kontekst.bygg([objekt()], config))
    assert {k.id for k in hoppet_over} >= {"K7", "K9"}


def test_kontroll_kan_slas_av(config):
    from tfm_sjekk.config import KontrollOppsett

    config.kontroller["K1"] = KontrollOppsett(aktiv=False)
    k = Kontekst.bygg([objekt(tfm=None)], config)
    assert funn_for("K1", k) == []


def test_alvorlighet_kan_overstyres(config):
    from tfm_sjekk.config import KontrollOppsett

    config.kontroller["K2"] = KontrollOppsett(alvorlighet=Alvorlighet.ADVARSEL)
    k = Kontekst.bygg([objekt(tfm="tull")], config)
    assert funn_for("K2", k)[0].alvorlighet is Alvorlighet.ADVARSEL


def test_funn_kommer_i_deterministisk_rekkefolge(config):
    """Golden files (§7) forutsetter dette."""
    objekter = [objekt(global_id=f"id{i}", tfm=None) for i in range(5)]
    funn_a, _ = kjor_alle(Kontekst.bygg(objekter, config))
    funn_b, _ = kjor_alle(Kontekst.bygg(list(reversed(objekter)), config))
    assert [f.sorteringsnokkel() for f in funn_a] == [f.sorteringsnokkel() for f in funn_b]


def test_gyldig_modell_gir_ingen_funn(config, systemtabell, komponenttabell):
    k = Kontekst.bygg(
        [objekt(tfm=GYLDIG)],
        config,
        systemtabell=systemtabell,
        komponenttabell=komponenttabell,
    )
    funn, _ = kjor_alle(k)
    assert funn == []
