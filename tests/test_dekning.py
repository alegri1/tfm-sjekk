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


# --- Hoppet over skal si hvorfor ---


def test_hver_grunn_navngis_riktig(tmp_path):
    """Tre ulike aarsaker falt sammen til ett ord for denne endringen.

    For den som leser er de motsatte handlinger: la det vaere, skaff dataene,
    vent paa en senere utgave.
    """
    from tfm_sjekk.kontroller import Hoppgrunn

    config = Konfigurasjon()
    config.kontroller["K8"] = KontrollOppsett(aktiv=False)
    _, hoppet = kjor_alle(Kontekst.bygg([objekt()], config))
    grunner = {k.id: grunn for k, grunn in hoppet}

    assert grunner["K8"] is Hoppgrunn.SLATT_AV
    assert grunner["K3"] is Hoppgrunn.MANGLER_KODETABELL
    assert grunner["K7"] is Hoppgrunn.MANGLER_MASTER


def test_slaatt_av_vinner_over_manglende_data():
    """Rekkefoelgen i _hoppgrunn ER betydningen.

    En kontroll som baade er slaatt av og mangler tabell skal melde at den er
    slaatt av — det er valget brukeren tok. Snus rekkefoelgen, faar hun beskjed
    om aa skaffe data hun bevisst har valgt bort.
    """
    from tfm_sjekk.kontroller import Hoppgrunn

    config = Konfigurasjon()
    config.kontroller["K3"] = KontrollOppsett(aktiv=False)

    _, hoppet = kjor_alle(Kontekst.bygg([objekt()], config))

    assert {k.id: g for k, g in hoppet}["K3"] is Hoppgrunn.SLATT_AV


def test_grunnen_sier_hva_som_skal_til():
    """Forskjellen mellom aa lete i dokumentasjonen og aa rette en linje."""
    from tfm_sjekk.kontroller import Hoppgrunn

    tabell = Hoppgrunn.MANGLER_KODETABELL.raad
    assert "--systemtabell" in tabell
    assert "--komponenttabell" in tabell
    assert "tfm-sjekk.toml" in tabell

    master = Hoppgrunn.MANGLER_MASTER.raad
    assert "--master" in master
    assert "tfm_master" in master


# --- Uleselig TFM er usynlig for sju kontroller ---


def utenfor(gid: str, tfm: str | None):
    """Et objekt i en klasse som IKKE staar i ifc_klasser."""
    from tfm_sjekk.modell import IfcObjekt

    return IfcObjekt(
        global_id=gid,
        ifc_klasse="IfcWall",
        ifc_supertyper=["IfcBuildingElement", "IfcProduct"],
        kildefil="test.ifc",
        tfm_forekomst=tfm,
    )


def test_uleselige_telles_per_fagmodell():
    """med_tfm() returnerer bare det som parset, og sju kontroller leser den.

    Et objekt i parsefeil er lest, i omfanget, og likevel usynlig for K3 til K9.
    """
    k = Kontekst.bygg(
        [
            objekt(tfm="++11508=4310.001.12-QLF005", global_id="a"),
            objekt(tfm="++115080=4310.001.12-QLF001", global_id="b"),
        ],
        Konfigurasjon(),
    )

    assert k.uleselige() == {"test.ifc": 1}


def test_alt_parser_gir_ingen_uleselige():
    k = Kontekst.bygg([objekt(tfm="++115080=4310.001.12-QLF001", global_id="a")], Konfigurasjon())

    assert k.uleselige() == {}


def test_objekter_utenfor_omfanget_telles_ikke():
    """Et objekt utenfor ifc_klasser er ikke ukontrollert AV DENNE GRUNNEN.

    Det er ikke kontrollert i det hele tatt, og det er dekningen som svarer
    for det. Blandes de to, blir tallet meningsløst i en federering med ARK.
    """
    k = Kontekst.bygg(
        [
            objekt(tfm="++11508=4310.001.12-QLF005", global_id="a"),
            utenfor("b", "++11508=4310.001.12-QLF009"),
        ],
        Konfigurasjon(),
    )

    assert k.uleselige() == {"test.ifc": 1}


def test_med_tfm_verdi_skiller_umerket_fra_uleselig():
    """«Ingen tolkbar TFM» og «ingen TFM i det hele tatt» er ulike ting.

    Det siste er K1s jobb, og en umerket modell skal ikke i tillegg faa en
    advarsel om grammatikken.
    """
    k = Kontekst.bygg(
        [
            objekt(tfm="++11508=4310.001.12-QLF005", global_id="a"),
            objekt(tfm=None, global_id="b"),
        ],
        Konfigurasjon(),
    )

    assert k.med_tfm_verdi() == {"test.ifc": 1}
    assert k.uleselige() == {"test.ifc": 1}


# --- D2: falt ALT ut paa grammatikken? ---


def d2_funn(objekter, config=None):
    funn, _ = kjor_alle(Kontekst.bygg(objekter, config or Konfigurasjon()))
    return [f for f in funn if f.kontroll == "D2"]


def test_alle_faller_ut_gir_funn():
    """Enkeltfeil rettes objekt for objekt. Faller alt ut, er det en
    merkekonvensjon som ikke stemmer med oppsettet — motsatt handling.
    """
    funn = d2_funn(
        [
            objekt(tfm="++11508=4310.001.12-QLF001", global_id="a"),
            objekt(tfm="++11508=4310.001.12-QLF002", global_id="b"),
        ]
    )

    assert len(funn) == 1
    assert funn[0].alvorlighet is Alvorlighet.ADVARSEL


def test_en_som_parser_er_nok_til_at_det_ikke_er_konvensjonen():
    """Grensen er ALLE, ikke en terskel.

    En terskel ville vaert et tall uten begrunnelse. Staar noen igjen, er de
    ekte funn, og K2 sier fortsatt hva som er galt med hver enkelt.
    """
    funn = d2_funn(
        [
            objekt(tfm="++11508=4310.001.12-QLF001", global_id="a"),
            objekt(tfm="++115080=4310.001.12-QLF002", global_id="b"),
        ]
    )

    assert not funn


def test_umerket_modell_gir_ikke_konvensjonsfunn():
    """«Ingen tolkbar TFM» og «ingen TFM i det hele tatt» er ulike ting.

    Det siste er K1s jobb. En umerket modell skal ikke i tillegg faa en
    advarsel om grammatikken.
    """
    funn = d2_funn([objekt(tfm=None, global_id="a"), objekt(tfm=None, global_id="b")])

    assert not funn


def test_vurderingen_er_per_fagmodell():
    """I en federering kan RIE vaere riktig merket mens RIV bruker en annen
    konvensjon. Samlet vurdering ville latt nettopp det gaa stille forbi.
    """
    funn = d2_funn(
        [
            objekt(tfm="++115080=4310.001.12-QLF001", global_id="a", kildefil="rie.ifc"),
            objekt(tfm="++11508=3600.001.04-JVZ001", global_id="b", kildefil="riv.ifc"),
        ]
    )

    assert [f.kildefil for f in funn] == ["riv.ifc"]


def test_meldingen_navngir_grammatikken_og_viser_et_avvik():
    """Et tall sier at noe er galt; meldingen sier hva."""
    funn = d2_funn([objekt(tfm="++11508=4310.001.12-QLF001", global_id="a")])

    assert "[grammatikk]" in funn[0].melding
    assert "5 siffer" in funn[0].melding, "det foerste avviket skal staa ordrett"


def test_d2_endrer_ikke_exit_koden():
    """Advarsel, som D1. Verktoyet staar som port i en leveranseprosess (§5),
    og et prosjekt med en annen grammatikk skal ikke stenge doera paa et funn
    som handler om oppsettet.
    """
    funn = d2_funn([objekt(tfm="++11508=4310.001.12-QLF001", global_id="a")])

    assert all(f.alvorlighet is not Alvorlighet.FEIL for f in funn)


def test_k2_meldingen_sier_hva_funnet_koster():
    """Et syntaksfunn ser ut som en detalj, men skjuler sju kontroller."""
    funn, _ = kjor_alle(
        Kontekst.bygg([objekt(tfm="++11508=4310.001.12-QLF001", global_id="a")], Konfigurasjon())
    )
    k2 = next(f for f in funn if f.kontroll == "K2")

    assert "ikke kontrollert av de øvrige" in k2.melding
    for nummer in ("K3", "K6", "K9"):
        assert nummer not in k2.melding, "numrene tar plassen fra selve feilen"


# --- D3: er funnene festet til riktig fil? ---


def i_fil(gid: str, fil: str, klasse: str = "IfcFlowTerminal", supertyper=None):
    from tfm_sjekk.modell import IfcObjekt

    return IfcObjekt(
        global_id=gid,
        ifc_klasse=klasse,
        ifc_supertyper=(supertyper if supertyper is not None else ["IfcDistributionFlowElement"]),
        kildefil=fil,
        tfm_forekomst="++115080=4310.001.12-QLF001",
    )


def test_samme_identitet_i_to_filer_finnes():
    """_etter_id er en dict paa global_id. To like ID-er kollapser, og funn
    festes til en vilkaarlig av filene."""
    k = Kontekst.bygg([i_fil("a", "rie.ifc"), i_fil("a", "kopi.ifc")], Konfigurasjon())

    assert k.delt_identitet() == {"a": ["kopi.ifc", "rie.ifc"]}


def test_delt_identitet_utenfor_omfanget_meldes_ikke():
    """Revit eksporterer delte rutenett inn i hver lenke. Snowdon-kjoringen har
    to IfcGrid i tre filer — normalt, og uten folger."""
    k = Kontekst.bygg(
        [
            i_fil("g", "rie.ifc", "IfcGrid", ["IfcProduct"]),
            i_fil("g", "riv.ifc", "IfcGrid", ["IfcProduct"]),
        ],
        Konfigurasjon(),
    )

    assert k.delt_identitet() == {}


def test_samme_identitet_i_samme_fil_er_noe_annet():
    """IFC krever unikhet i EN fil. Bryter en fil det, er det en annen sak enn
    to filer som overlapper."""
    k = Kontekst.bygg([i_fil("a", "rie.ifc"), i_fil("a", "rie.ifc")], Konfigurasjon())

    assert k.delt_identitet() == {}


def test_d3_melder_med_advarsel_og_navngir_filene():
    funn, _ = kjor_alle(
        Kontekst.bygg([i_fil("a", "rie.ifc"), i_fil("a", "kopi.ifc")], Konfigurasjon())
    )
    d3 = [f for f in funn if f.kontroll == "D3"]

    assert len(d3) == 1
    assert d3[0].alvorlighet is Alvorlighet.ADVARSEL
    assert "rie.ifc" in d3[0].melding and "kopi.ifc" in d3[0].melding
    assert "sendt inn to ganger" in d3[0].melding


def test_d3_sier_hva_som_ER_paalitelig():
    """En bruker skal ikke lese advarselen som at verktoyet ikke virker."""
    funn, _ = kjor_alle(
        Kontekst.bygg([i_fil("a", "rie.ifc"), i_fil("a", "kopi.ifc")], Konfigurasjon())
    )
    melding = next(f for f in funn if f.kontroll == "D3").melding

    assert "riktige" in melding
    assert "tilfeldig hvilken av filene" in melding


def test_uten_kollisjon_ingen_d3():
    funn, _ = kjor_alle(
        Kontekst.bygg([i_fil("a", "rie.ifc"), i_fil("b", "kopi.ifc")], Konfigurasjon())
    )

    assert not [f for f in funn if f.kontroll == "D3"]


def test_begge_objektene_staar_igjen():
    """Ingen sammenslaaing eller forkasting. Hvilket av to like objekter som er
    det rette, kan bare den som sendte inn filene svare paa."""
    k = Kontekst.bygg([i_fil("a", "rie.ifc"), i_fil("a", "kopi.ifc")], Konfigurasjon())

    assert len(k.objekter) == 2
    assert k.dekning() == {"kopi.ifc": (1, 1), "rie.ifc": (1, 1)}


def test_ett_funn_per_filkombinasjon_ikke_per_objekt():
    """Deler to filer tusen objekter, er det ETT problem."""
    objekter = [i_fil(f"o{i}", fil) for i in range(5) for fil in ("rie.ifc", "kopi.ifc")]
    funn, _ = kjor_alle(Kontekst.bygg(objekter, Konfigurasjon()))
    d3 = [f for f in funn if f.kontroll == "D3"]

    assert len(d3) == 1
    assert "5 objekt(er)" in d3[0].melding
