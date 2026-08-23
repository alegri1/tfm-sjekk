"""Tester for evnen «kursnummer» — når undernummeret skal være utfylt.

To slags objekter er unntatt, og av samme grunn: fordelingen er roten kursene
går ut fra, og føringsveien er det som bærer dem. Ingen av dem ligger på en
kurs.

Uten det andre unntaket ga en ekte Revit-eksport med 2439 objekter 1018 funn om
kabelrør og 11 om ekte feil.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from tfm_sjekk.config import ElektroOppsett, Konfigurasjon
from tfm_sjekk.ifc.loader import les_modell
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.k8_elektro import K8Elektro
from tfm_sjekk.modell import IfcObjekt

UTEN_KURS = "++115080=4320.001.00-QLF001"
MED_KURS = "++115080=4320.001.12-QLF002"


def objekt(
    global_id: str = "a",
    klasse: str = "IfcLamp",
    supertyper: tuple[str, ...] = ("IfcFlowTerminal", "IfcDistributionElement", "IfcProduct"),
    tfm: str = UTEN_KURS,
) -> IfcObjekt:
    return IfcObjekt(
        global_id=global_id,
        ifc_klasse=klasse,
        ifc_supertyper=list(supertyper),
        kildefil="rie.ifc",
        tfm_forekomst=tfm,
    )


def k8(objekter: list[IfcObjekt], config: Konfigurasjon | None = None) -> list:
    k = Kontekst.bygg(objekter, config or Konfigurasjon())
    return K8Elektro().kjor(k)


def kursfunn(funn: list) -> list:
    return [f for f in funn if "kurs-/sløyfenummer" in f.melding]


# --- Kursnummer kreves av elektroobjekter ---


def test_lampe_uten_kursnummer_meldes():
    assert len(kursfunn(k8([objekt()]))) == 1


def test_lampe_med_kursnummer_meldes_ikke():
    assert kursfunn(k8([objekt(tfm=MED_KURS)])) == []


def test_andre_fag_er_upavirket():
    """Undernummeret betyr noe annet utenfor kapittel 4 og 5."""
    vvs = objekt(tfm="++115080=3600.001.00-JVZ001")
    assert kursfunn(k8([vvs])) == []


# --- Objekter som ikke ligger på en kurs er unntatt ---


def test_fordelingen_er_roten():
    tavle = objekt(
        klasse="IfcElectricDistributionBoard",
        supertyper=("IfcDistributionElement", "IfcProduct"),
        tfm="++115080=4310.001.00-QLF100",
    )
    assert kursfunn(k8([tavle])) == []


def test_foringsvei_baerer_kurser():
    ror = objekt(
        klasse="IfcFlowSegment",
        supertyper=("IfcDistributionFlowElement", "IfcDistributionElement", "IfcProduct"),
        tfm="++115080=4360.001.00-QLK001",
    )
    assert kursfunn(k8([ror])) == []


def test_bend_er_ogsaa_foringsvei():
    bend = objekt(
        klasse="IfcFlowFitting",
        supertyper=("IfcDistributionFlowElement", "IfcDistributionElement", "IfcProduct"),
        tfm="++115080=4360.001.00-QLK002",
    )
    assert kursfunn(k8([bend])) == []


def test_utstyr_er_ikke_unntatt():
    """Lampe i samme system som røret meldes fortsatt."""
    ror = objekt("a", "IfcFlowSegment", ("IfcDistributionElement",), "++115080=4360.001.00-QLK001")
    lampe = objekt("b", tfm="++115080=4320.001.00-QLF001")
    assert len(kursfunn(k8([ror, lampe]))) == 1


# --- Konfigurerbart, med en standardliste som virker ---


def test_standardlista_dekker_det_vanlige():
    assert {"IfcFlowSegment", "IfcFlowFitting"} <= set(ElektroOppsett().foring_klasser)


def test_prosjektet_kan_utvide_lista():
    config = Konfigurasjon(elektro=ElektroOppsett(foring_klasser=["IfcSpesialRor"]))
    spesial = objekt(klasse="IfcSpesialRor", supertyper=("IfcProduct",))
    assert kursfunn(k8([spesial], config)) == []


def test_klassenavn_som_ikke_finnes_er_ufarlig():
    """Lista kan nevne IFC4-klasser selv når fila er 2x3.

    Treff går mot objektets egen arvekjede, så et navn som ikke finnes i
    skjemaet matcher aldri noe — det gir ingen feil.
    """
    config = Konfigurasjon(elektro=ElektroOppsett(foring_klasser=["IfcFinnesIkke"]))
    assert len(kursfunn(k8([objekt()], config))) == 1


# --- Unntaket gjelder bare kravet om kursnummer ---


def test_foringsvei_teller_fortsatt_i_koblingsgrafen():
    """En lampe koblet til en fordeling GJENNOM et kabelrør.

    Utelot vi føringsveien fra grafen, ville lampen mistet fordelingen sin, og
    K8b kunne ikke sett at den hører til et annet system.
    """
    tavle = IfcObjekt(
        global_id="tavle",
        ifc_klasse="IfcElectricDistributionBoard",
        ifc_supertyper=["IfcDistributionElement", "IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst="++115080=4310.001.00-QLF100",
        tilkoblet=["ror"],
    )
    ror = IfcObjekt(
        global_id="ror",
        ifc_klasse="IfcFlowSegment",
        ifc_supertyper=["IfcDistributionElement", "IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst="++115080=4360.001.00-QLK001",
        tilkoblet=["tavle", "lampe"],
    )
    lampe = IfcObjekt(
        global_id="lampe",
        ifc_klasse="IfcLamp",
        ifc_supertyper=["IfcFlowTerminal", "IfcDistributionElement", "IfcProduct"],
        kildefil="rie.ifc",
        # Annet system enn tavla — det er dette K8b skal se
        tfm_forekomst="++115080=4999.001.12-QLF001",
        tilkoblet=["ror"],
    )
    funn = k8([tavle, ror, lampe])
    assert any("tilkoblet fordelingen" in f.melding for f in funn), (
        "lampen mistet fordelingen sin gjennom kabelrøret"
    )


# --- Systemkoden kan si det IFC-klassen ikke sier ---
#
# En ekte Revit-eksport ga seksten koblingsbokser som IfcBuildingElementProxy.
# TFM-en sa 4360 — kabelforing — mens klassen ikke sa noe. K8 trodde på klassen.


def proxy(tfm: str = "++115080=4360.001.00-QLK001") -> IfcObjekt:
    """Et objekt uten føringsvei-klasse. Slik en koblingsboks kom ut av Revit."""
    return objekt(klasse="IfcBuildingElementProxy", supertyper=("IfcProduct",), tfm=tfm)


def test_systemkoden_kan_frita_et_objekt_uten_foringsveiklasse():
    config = Konfigurasjon(elektro=ElektroOppsett(foring_systemkoder=["4360"]))
    assert kursfunn(k8([proxy()], config)) == []


def test_uten_oppsett_meldes_det_som_for():
    """Standardoppførselen skal ikke røre seg. Lista er tom til noen fyller den."""
    assert len(kursfunn(k8([proxy()]))) == 1


def test_standardlista_er_tom():
    """Tom med vilje, av juridiske grunner (§8), ikke av forglemmelse.

    Uten denne testen ville noen fylt lista i god tro første gang de så at den
    var tom — og da hadde innholdet i NS 3451 ligget i repoet.
    """
    assert ElektroOppsett().foring_systemkoder == []


def test_klassen_alene_holder():
    """Standardlista over klasser skal virke selv når ingen kode er oppgitt."""
    ror = objekt(
        klasse="IfcFlowSegment",
        supertyper=("IfcDistributionElement", "IfcProduct"),
        tfm="++115080=4360.001.00-QLK001",
    )
    assert kursfunn(k8([ror])) == []


def test_klassen_holder_ogsaa_naar_en_annen_kode_er_oppgitt():
    """Å konfigurere systemkoder skal ikke slå av klasselista."""
    config = Konfigurasjon(elektro=ElektroOppsett(foring_systemkoder=["4999"]))
    ror = objekt(
        klasse="IfcFlowSegment",
        supertyper=("IfcDistributionElement", "IfcProduct"),
        tfm="++115080=4360.001.00-QLK001",
    )
    assert kursfunn(k8([ror], config)) == []


def test_en_annen_systemkode_meldes_fortsatt():
    config = Konfigurasjon(elektro=ElektroOppsett(foring_systemkoder=["4360"]))
    lampe = proxy(tfm="++115080=4320.001.00-QLF001")
    assert len(kursfunn(k8([lampe], config))) == 1


def test_unntaket_sprer_seg_ikke_til_koblingsgrafen():
    """Et objekt unntatt på systemkoden skal fortsatt telle for K8b.

    Samme prøve som for klasseunntaket: utelot vi objektet fra grafen, ville
    lampen bak det mistet fordelingen sin.
    """
    config = Konfigurasjon(elektro=ElektroOppsett(foring_systemkoder=["4360"]))
    tavle = IfcObjekt(
        global_id="tavle",
        ifc_klasse="IfcElectricDistributionBoard",
        ifc_supertyper=["IfcDistributionElement", "IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst="++115080=4310.001.00-QLF100",
        tilkoblet=["boks"],
    )
    boks = IfcObjekt(
        global_id="boks",
        ifc_klasse="IfcBuildingElementProxy",
        ifc_supertyper=["IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst="++115080=4360.001.00-QLK001",
        tilkoblet=["tavle", "lampe"],
    )
    lampe = IfcObjekt(
        global_id="lampe",
        ifc_klasse="IfcLamp",
        ifc_supertyper=["IfcFlowTerminal", "IfcDistributionElement", "IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst="++115080=4999.001.12-QLF001",
        tilkoblet=["boks"],
    )
    funn = k8([tavle, boks, lampe], config)
    assert kursfunn(funn) == [], "koblingsboksen skulle vært unntatt"
    assert any("tilkoblet fordelingen" in f.melding for f in funn), (
        "lampen mistet fordelingen sin gjennom koblingsboksen"
    )


# --- Demomodellen skal faktisk demonstrere regelen ---


def demofunn(config_sti):
    """Kjører eksempler/foringsvei.ifc slik README-en sier, og teller K8-funn."""
    sys.path.insert(0, str(Path(__file__).parent))
    from fixtures.syntetisk import lag_foringsveimodell

    modell = lag_foringsveimodell(Path(tempfile.mkdtemp()) / "foringsvei.ifc")
    objekter = les_modell(modell)
    config = Konfigurasjon.les(config_sti)
    return [f for f in K8Elektro().kjor(Kontekst.bygg(objekter, config)) if "kurs-" in f.melding]


def test_demomodellen_viser_forskjellen():
    """Uten oppsettet to funn, med det ett — og det ene er koblingsboksen.

    Tallet alene beviser ingenting: en modell der begge funnene forsvant ville
    gitt samme retning. Testen krever at det som blir igjen er uttaket, og at
    det som forsvant er proxyen.
    """
    eksempler = Path(__file__).parent.parent / "eksempler"
    uten = demofunn(None)
    med = demofunn(eksempler / "foringsvei.toml")

    assert {f.ifc_klasse for f in uten} == {"IfcOutlet", "IfcBuildingElementProxy"}
    assert {f.ifc_klasse for f in med} == {"IfcOutlet"}


def test_kabelroret_meldes_aldri():
    """IfcFlowSegment dekkes av standardlista over klasser, begge veier.

    Å konfigurere systemkoder skal ikke slå av klasselista — og modellen har
    et kabelrør nettopp for å vise det.
    """
    eksempler = Path(__file__).parent.parent / "eksempler"
    for config in (None, eksempler / "foringsvei.toml"):
        assert not [f for f in demofunn(config) if "QLK002" in (f.tfm or "")]


def test_oppsettet_og_modellen_bruker_samme_kode():
    """Endres koden i fiksturen uten at TOML-en følger med, slutter demoen å
    demonstrere noe — og den ville sett like riktig ut."""
    sys.path.insert(0, str(Path(__file__).parent))
    from fixtures.syntetisk import FORINGSVEI

    eksempler = Path(__file__).parent.parent / "eksempler"
    koder = Konfigurasjon.les(eksempler / "foringsvei.toml").elektro.foring_systemkoder
    proxy_tfm = next(t for k, t in FORINGSVEI if k == "IfcBuildingElementProxy")
    assert proxy_tfm.split("=")[1][:4] in koder
