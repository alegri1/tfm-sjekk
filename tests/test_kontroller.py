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


def test_k7_flagger_system_som_ikke_star_i_mastera(config, master):
    k = Kontekst.bygg([objekt(tfm="++115080=9100.001.04-JVZ001")], config, master=master)
    funn = funn_for("K7", k)
    feil = [f for f in funn if f.alvorlighet is Alvorlighet.FEIL]
    assert len(feil) == 1
    assert "9100.001.04" in feil[0].melding


def test_k7_flagger_komponenttype_som_ikke_star_i_mastera(config, master):
    k = Kontekst.bygg(
        [objekt(tfm="++115080=3600.001.04-JVZ001%XXX.001.008")], config, master=master
    )
    feil = [f for f in funn_for("K7", k) if f.alvorlighet is Alvorlighet.FEIL]
    assert len(feil) == 1
    assert "XXX.001.008" in feil[0].melding


def test_k7_er_stille_nar_modellen_stemmer_med_mastera(config, master):
    k = Kontekst.bygg([objekt()], config, master=master)
    assert funn_for("K7", k) == []


def test_k7_sjekker_ikke_en_liste_mastera_ikke_forer(config):
    """En master med bare systemliste skal ikke flagge alle komponenttyper."""
    from tfm_sjekk.tabeller import TfmMaster

    bare_systemer = TfmMaster(kilde="delvis.csv", systemer={"3600.001.04"})
    k = Kontekst.bygg([objekt()], config, master=bare_systemer)
    assert funn_for("K7", k) == []


def test_k7_melder_umodellerte_oppforinger_som_info(config):
    """Motsatt retning (§4). Info, ikke feil — se modulens docstring."""
    from tfm_sjekk.tabeller import TfmMaster

    stor_master = TfmMaster(
        kilde="master.csv",
        systemer={"3600.001.04", "4310.001.12", "5600.001.01"},
        komponenttyper={"JVZ.001.008"},
    )
    k = Kontekst.bygg([objekt()], config, master=stor_master)
    funn = funn_for("K7", k)
    assert len(funn) == 1
    assert funn[0].alvorlighet is Alvorlighet.INFO
    assert "2 systemer" in funn[0].melding
    assert "4310.001.12" in funn[0].melding and "5600.001.01" in funn[0].melding
    assert funn[0].global_id is None


def test_k7_umodellert_forblir_info_selv_om_graden_overstyres(config):
    """Retningen skal aldri kunne bryte et CI-bygg. Se §5 og modulens docstring."""
    from tfm_sjekk.config import KontrollOppsett
    from tfm_sjekk.tabeller import TfmMaster

    config.kontroller["K7"] = KontrollOppsett(alvorlighet=Alvorlighet.FEIL)
    master = TfmMaster(kilde="master.csv", systemer={"3600.001.04", "4310.001.12"})
    k = Kontekst.bygg([objekt()], config, master=master)
    assert funn_for("K7", k)[0].alvorlighet is Alvorlighet.INFO


def test_k7_hoppes_over_uten_master(config):
    _, hoppet_over = kjor_alle(Kontekst.bygg([objekt()], config))
    assert "K7" in {k.id for k in hoppet_over}


def test_k8_krever_kursnummer_pa_elektro(config):
    k = Kontekst.bygg([objekt(tfm="++115080=4300.001.00-QLF001")], config)
    funn = funn_for("K8", k)
    assert len(funn) == 1
    assert "kurs" in funn[0].melding


def test_k8_ignorerer_ikke_elektro(config):
    k = Kontekst.bygg([objekt(tfm="++115080=3600.001.00-JVZ001")], config)
    assert funn_for("K8", k) == []


def fordeling(tfm: str | None = "++115080=4310.001.00-QLF001", medlemmer: list = ()):
    """En fordeling med objektene som henger på den, ferdig koblet begge veier."""
    tavle = objekt(
        tfm=tfm,
        global_id="tavle1",
        klasse="IfcElectricDistributionBoard",
        navn="Fordeling 1",
        tilkoblet=[m.global_id for m in medlemmer],
    )
    for medlem in medlemmer:
        medlem.tilkoblet = [tavle.global_id]
    return [tavle, *medlemmer]


def test_k8b_flagger_objekt_med_annet_system_enn_fordelingen(config):
    avvik = objekt(tfm="++115080=4320.001.12-QLF010", global_id="a")
    k = Kontekst.bygg(fordeling(medlemmer=[avvik]), config)
    funn = [f for f in funn_for("K8", k) if f.global_id == "a"]
    assert len(funn) == 1
    assert "4310.001" in funn[0].melding and "4320.001" in funn[0].melding


def test_k8b_godtar_ulike_kursnumre_i_samme_system(config):
    """Undernummeret er nettopp det som skal variere på en fordeling."""
    medlemmer = [
        objekt(tfm="++115080=4310.001.12-QLF010", global_id="a"),
        objekt(tfm="++115080=4310.001.13-QLF011", global_id="b"),
    ]
    k = Kontekst.bygg(fordeling(medlemmer=medlemmer), config)
    assert [f for f in funn_for("K8", k) if f.alvorlighet is Alvorlighet.FEIL] == []


def test_k8b_hopper_over_fordeling_uten_egen_tfm(config):
    """Uten TFM på tavla er det K1 som har jobben — ikke gjett systemet."""
    avvik = objekt(tfm="++115080=4320.001.12-QLF010", global_id="a")
    k = Kontekst.bygg(fordeling(tfm=None, medlemmer=[avvik]), config)
    assert [f for f in funn_for("K8", k) if f.global_id == "a"] == []


def test_k8b_stopper_i_neste_fordeling(config):
    """En underfordeling er sin egen rot; den skal ikke arve systemet over."""
    underfordeling = objekt(
        tfm="++115080=4320.001.00-QLF002",
        global_id="tavle2",
        klasse="IfcElectricDistributionBoard",
        navn="Underfordeling",
    )
    lampe = objekt(tfm="++115080=4320.001.12-QLF010", global_id="a")
    objekter = fordeling(medlemmer=[underfordeling])
    underfordeling.tilkoblet = ["tavle1", "a"]
    lampe.tilkoblet = ["tavle2"]
    k = Kontekst.bygg([*objekter, lampe], config)

    # Lampa hører til underfordelingen, ikke hovedfordelingen, og har samme
    # system som den. Ingen K8b-feil på lampa.
    assert [f for f in funn_for("K8", k) if f.global_id == "a"] == []


def test_k8c_flagger_kursnummer_brukt_av_to_kurser(config):
    medlemmer = [
        objekt(tfm="++115080=4310.001.12-QLF010", global_id="a", kretser=["Kurs 12"]),
        objekt(tfm="++115080=4310.001.12-QLF011", global_id="b", kretser=["Kurs 12B"]),
    ]
    k = Kontekst.bygg(fordeling(medlemmer=medlemmer), config)
    funn = [f for f in funn_for("K8", k) if f.alvorlighet is Alvorlighet.FEIL]
    assert len(funn) == 2  # begge objektene rapporteres, som i K6
    assert "Kurs 12" in funn[0].melding and "Kurs 12B" in funn[0].melding


def test_k8c_godtar_mange_objekter_pa_samme_kurs(config):
    """Ti armaturer på kurs 12 er normalt, ikke en kollisjon."""
    medlemmer = [
        objekt(tfm=f"++115080=4310.001.12-QLF01{i}", global_id=f"a{i}", kretser=["Kurs 12"])
        for i in range(3)
    ]
    k = Kontekst.bygg(fordeling(medlemmer=medlemmer), config)
    assert [f for f in funn_for("K8", k) if f.alvorlighet is Alvorlighet.FEIL] == []


def test_k8c_sier_fra_nar_modellen_mangler_kursgrupper(config):
    """Uten kursgrupper kan ikke K8c konkludere — da skal den si det."""
    medlemmer = [objekt(tfm="++115080=4310.001.12-QLF010", global_id="a")]
    k = Kontekst.bygg(fordeling(medlemmer=medlemmer), config)
    info = [f for f in funn_for("K8", k) if f.alvorlighet is Alvorlighet.INFO]
    assert len(info) == 1
    assert "kursgrupper" in info[0].melding


def test_k8c_er_stille_uten_fordelinger(config):
    """Ingen tavler i modellen betyr ikke at noe er galt."""
    k = Kontekst.bygg([objekt(tfm="++115080=4310.001.12-QLF010")], config)
    assert funn_for("K8", k) == []


def test_k9_er_stille_nar_modellen_ikke_bruker_mmi(config):
    """Ingen har MMI = prosjektet bruker det ikke. Ikke ett funn per objekt."""
    k = Kontekst.bygg([objekt(global_id="a"), objekt(global_id="b")], config)
    assert funn_for("K9", k) == []


def test_k9_flagger_manglende_mmi_nar_feltet_er_i_bruk(config):
    k = Kontekst.bygg(
        [objekt(global_id="a", mmi="300"), objekt(global_id="b")],
        config,
    )
    funn = funn_for("K9", k)
    assert [f.global_id for f in funn] == ["b"]


def test_k9_vurderer_mmi_bruk_per_fagmodell(config):
    """RIE kan ha kommet til 300 mens RIV ikke har begynt (§3, federering)."""
    k = Kontekst.bygg(
        [
            objekt(global_id="a", kildefil="rie.ifc", mmi="300"),
            objekt(global_id="b", kildefil="rie.ifc"),
            objekt(global_id="c", kildefil="riv.ifc"),
        ],
        config,
    )
    mangler = [f for f in funn_for("K9", k) if "mangler" in f.melding]
    assert [f.global_id for f in mangler] == ["b"]


def test_k9_kan_kreve_mmi_pa_alle(config):
    config.mmi.krev_pa_alle = True
    k = Kontekst.bygg([objekt(global_id="a"), objekt(global_id="b")], config)
    funn = funn_for("K9", k)
    assert len(funn) == 1  # ett samlet funn, ikke ett per objekt
    assert "Ingen av de 2" in funn[0].melding


def test_k9_flagger_verdi_utenfor_skalaen(config):
    k = Kontekst.bygg([objekt(mmi="275")], config)
    funn = funn_for("K9", k)
    assert len(funn) == 1
    assert "275" in funn[0].melding


def test_k9_godtar_skrivemater_av_samme_niva(config):
    """«MMI 300» og «300» er samme nivå."""
    k = Kontekst.bygg(
        [
            objekt(global_id="a", mmi="MMI 300"),
            objekt(global_id="b", mmi="mmi300"),
            objekt(global_id="c", mmi="300"),
        ],
        config,
    )
    assert funn_for("K9", k) == []


def test_k9_flagger_sprik_innenfor_systemet(config):
    """Avviket rapporteres, ikke flertallet."""
    k = Kontekst.bygg(
        [
            objekt(global_id="a", mmi="300"),
            objekt(global_id="b", mmi="300"),
            objekt(global_id="c", mmi="400"),
        ],
        config,
    )
    funn = funn_for("K9", k)
    assert [f.global_id for f in funn] == ["c"]
    assert "300" in funn[0].melding and "400" in funn[0].melding


def test_k9_skiller_mellom_systemer(config):
    """Ulik MMI i to ulike systemer er ikke et sprik."""
    k = Kontekst.bygg(
        [
            objekt(global_id="a", tfm="++115080=3600.001.04-JVZ001", mmi="300"),
            objekt(global_id="b", tfm="++115080=4310.001.12-QLF001", mmi="400"),
        ],
        config,
    )
    assert funn_for("K9", k) == []


def test_k9_har_info_som_standardgrad(config):
    k = Kontekst.bygg([objekt(mmi="275")], config)
    assert funn_for("K9", k)[0].alvorlighet is Alvorlighet.INFO


def test_k9_skalaen_kan_konfigureres(config):
    """Egne systemer på de to, ellers ville K9c slått ut på spriket i tillegg."""
    config.mmi.gyldige_verdier = ["A", "B"]
    k = Kontekst.bygg(
        [
            objekt(global_id="a", tfm="++115080=3600.001.04-JVZ001", mmi="A"),
            objekt(global_id="b", tfm="++115080=4310.001.12-QLF001", mmi="300"),
        ],
        config,
    )
    funn = funn_for("K9", k)
    assert [f.global_id for f in funn] == ["b"]


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


def test_gyldig_modell_gir_ingen_funn(config, systemtabell, komponenttabell, master):
    k = Kontekst.bygg(
        [objekt(tfm=GYLDIG)],
        config,
        systemtabell=systemtabell,
        komponenttabell=komponenttabell,
        master=master,
    )
    funn, _ = kjor_alle(k)
    assert funn == []
