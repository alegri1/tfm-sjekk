"""Tester for verdiuttrekket (openspec: verdiuttrekk).

Scenarioene i spec-en, ett for ett. De bygger IFC-filer med egenskapssett som
ikke ligner dem fixturene ellers lager — det er nettopp de rotete tilfellene
kravet handler om.
"""

from __future__ import annotations

import ifcopenshell
import ifcopenshell.guid as guid
import pytest

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.ifc import les_modell
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle
from tfm_sjekk.modell import Kilde
from tfm_sjekk.parser import mmi_niva

GYLDIG = "++115080=3600.001.04-JVZ001"


def lag(sti, psets: dict[str, list[tuple[str, str]]], klasse: str = "IfcFlowTerminal"):
    """Én IFC-fil med ett objekt og de egenskapssettene som oppgis.

    Feltene beholder rekkefølgen de står i, siden flere av scenarioene handler
    om nettopp den.
    """
    f = ifcopenshell.file(schema="IFC4")
    element = f.create_entity(klasse, GlobalId=guid.new(), Name="Objekt")
    for pset_navn, felter in psets.items():
        props = [
            f.create_entity(
                "IfcPropertySingleValue", Name=n, NominalValue=f.create_entity("IfcLabel", v)
            )
            for n, v in felter
        ]
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name=pset_navn, HasProperties=props
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )
    f.write(str(sti))
    return les_modell(sti)[0]


def funn_for(objekt, kontroll: str):
    funn, _ = kjor_alle(Kontekst.bygg([objekt], Konfigurasjon()))
    return [f for f in funn if f.kontroll == kontroll]


# --- Konfigurert egenskapssett og felt har forrang -------------------------


def test_verdien_ligger_der_den_skal(tmp_path):
    o = lag(tmp_path / "a.ifc", {"TFM11_Forekomst": [("TFM", GYLDIG)]})
    assert o.tfm_forekomst == GYLDIG
    assert o.kilder["forekomst"].kilde is Kilde.KONFIGURERT


def test_konfigurert_vei_slar_gjenkjent_felt_andre_steder(tmp_path):
    o = lag(
        tmp_path / "b.ifc",
        {
            "Pset_Revit": [("TFM", "++115080=9999.001.04-QLF001")],
            "TFM11_Forekomst": [("TFM", GYLDIG)],
        },
    )
    assert o.tfm_forekomst == GYLDIG


# --- Gjenkjent feltnavn i et hvilket som helst egenskapssett ---------------


def test_riktig_felt_i_feil_egenskapssett(tmp_path):
    o = lag(tmp_path / "c.ifc", {"Pset_Revit_Data": [("TFM", GYLDIG)]})
    assert o.tfm_forekomst == GYLDIG
    assert o.kilder["forekomst"].kilde is Kilde.GJENKJENT_FELT


# --- En verdi uten gjenkjent feltnavn må være gjenkjennelig ----------------


def test_fremmed_verdi_forkastes(tmp_path):
    """«Systemair» er ikke en TFM-ID, og skal ikke bli meldt som syntaksfeil."""
    o = lag(
        tmp_path / "d.ifc",
        {"TFM11_Forekomst": [("Fabrikat", "Systemair"), ("Modell", "DVCompact 4")]},
    )
    assert o.tfm_forekomst is None
    assert o.kilder["forekomst"].kilde is Kilde.FORKASTET

    assert funn_for(o, "K2") == []
    k1 = funn_for(o, "K1")
    assert len(k1) == 1
    assert "Systemair" in k1[0].melding


def test_odelagt_tfm_id_godtas_og_flagges(tmp_path):
    o = lag(
        tmp_path / "e.ifc",
        {"TFM11_Forekomst": [("TFM-ID", "++11508=3600.001.04-JVZ001")]},
    )
    assert o.tfm_forekomst == "++11508=3600.001.04-JVZ001"
    assert o.kilder["forekomst"].kilde is Kilde.GJETTET
    assert len(funn_for(o, "K2")) == 1


@pytest.mark.parametrize(
    "felter",
    [
        [("TFM-ID", GYLDIG), ("Fabrikat", "Systemair")],
        [("Fabrikat", "Systemair"), ("TFM-ID", GYLDIG)],
    ],
    ids=["tfm først", "tfm sist"],
)
def test_rekkefolgen_i_fila_endrer_ingenting(tmp_path, felter):
    o = lag(tmp_path / f"{felter[0][0]}.ifc", {"TFM11_Forekomst": felter})
    assert o.tfm_forekomst == GYLDIG


# --- Feltnavn brukt til søk på tvers skal være distinkte -------------------


def test_generisk_feltnavn_gir_ikke_treff(tmp_path):
    o = lag(
        tmp_path / "f.ifc",
        {
            "Pset_ManufacturerTypeInformation": [
                ("Manufacturer", "Systemair"),
                ("Type", "DVCompact"),
            ]
        },
    )
    assert o.tfm_type is None


# --- Verktøyet skal gjøre rede for en usikker verdi ------------------------


def test_funnet_forklarer_hvor_verdien_kom_fra(tmp_path):
    o = lag(tmp_path / "g.ifc", {"Pset_Revit_Data": [("TFM", "++11508=3600.001.04-JVZ001")]})
    melding = funn_for(o, "K2")[0].melding
    assert "Pset_Revit_Data" in melding
    assert "TFM" in melding


def test_sikker_verdi_far_ingen_opphavssetning(tmp_path):
    o = lag(tmp_path / "h.ifc", {"TFM11_Forekomst": [("TFM", "++11508=3600.001.04-JVZ001")]})
    melding = funn_for(o, "K2")[0].melding
    assert "ble lest fra" not in melding
    assert "gjettet" not in melding


# --- MMI tolkes bare når verdien er en nivåangivelse -----------------------


@pytest.mark.parametrize("verdi", ["MMI 300", "mmi300", "300", "MMI-300", "mmi: 300"])
def test_skrivemater_av_samme_niva(verdi):
    assert mmi_niva(verdi) == "300"


def test_fritekst_er_ikke_et_niva():
    assert mmi_niva("sjekket av RIE 12.03") is None


def test_ukjent_skala_uten_siffer_beholdes():
    """Et prosjekt kan bruke ord i stedet for tall; da er ordet nivået."""
    assert mmi_niva("prosjektert") == "PROSJEKTERT"


# --- En forkastet verdi skal ikke påvirke andre objekter -------------------


def test_ett_bortkommet_felt_vipper_ikke_hele_fila(tmp_path):
    """Kommentaren i MMI-pset-et skal ikke gjøre at de to andre objektene får
    funn om manglende MMI."""
    f = ifcopenshell.file(schema="IFC4")
    for nummer in range(1, 4):
        el = f.create_entity("IfcFlowTerminal", GlobalId=guid.new(), Name=f"Vifte {nummer}")
        if nummer == 1:
            prop = f.create_entity(
                "IfcPropertySingleValue",
                Name="Kommentar",
                NominalValue=f.create_entity("IfcLabel", "sjekket av RIE 12.03"),
            )
            pset = f.create_entity(
                "IfcPropertySet", GlobalId=guid.new(), Name="MMI", HasProperties=[prop]
            )
            f.create_entity(
                "IfcRelDefinesByProperties",
                GlobalId=guid.new(),
                RelatedObjects=[el],
                RelatingPropertyDefinition=pset,
            )
    sti = tmp_path / "mmi.ifc"
    f.write(str(sti))

    funn, _ = kjor_alle(Kontekst.bygg(les_modell(sti), Konfigurasjon()))
    assert [x for x in funn if x.kontroll == "K9"] == []


# --- Meldingens presisjon skal svare til hva verktøyet vet -----------------


def test_fremmed_verdi_i_konfigurert_felt_beskrives_som_fremmed(tmp_path):
    """Inn gjennom hovedinngangen: en mal som legger fabrikatnavnet i TFM-feltet."""
    o = lag(tmp_path / "i.ifc", {"TFM11_Forekomst": [("TFM", "Systemair")]})
    melding = funn_for(o, "K2")[0].melding
    assert "ser ikke ut som en TFM-ID" in melding
    assert "Mangler" not in melding


def test_nesten_treff_far_spesifikk_anvisning(tmp_path):
    o = lag(tmp_path / "j.ifc", {"TFM11_Forekomst": [("TFM", "++115080-3600.001.04")]})
    assert "Mangler «=»-delen" in funn_for(o, "K2")[0].melding


def test_proveniensen_overlever_prosessgrensa(tmp_path):
    """Federering leser hver fil i egen prosess (§3), så proveniensen må
    pickles sammen med resten av objektet."""
    from tfm_sjekk.ifc import les_modeller

    for navn in ("rie.ifc", "riv.ifc"):
        lag(tmp_path / navn, {"Pset_Revit_Data": [("TFM", GYLDIG)]})

    objekter = les_modeller([tmp_path / "rie.ifc", tmp_path / "riv.ifc"], parallelt=True)
    assert len(objekter) == 2
    assert all(o.kilder["forekomst"].kilde is Kilde.GJENKJENT_FELT for o in objekter)
    assert all(o.kilder["forekomst"].pset == "Pset_Revit_Data" for o in objekter)


def test_bcf_tittelen_forblir_lesbar_og_beskrivelsen_baerer_opphavet(tmp_path):
    """Opphavssetningen gjør meldingen lang. BCF-tittelen kuttes på 100 tegn,
    så detaljen må ligge i beskrivelsen — ikke fylle tittelen."""
    import xml.etree.ElementTree as ET
    import zipfile

    from tfm_sjekk.rapport import skriv_bcf

    o = lag(tmp_path / "k.ifc", {"Pset_Revit_Data": [("TFM", "++11508=3600.001.04-JVZ001")]})
    funn, _ = kjor_alle(Kontekst.bygg([o], Konfigurasjon()))
    sti = skriv_bcf(funn, tmp_path / "funn.bcfzip", "2026-01-01T12:00:00Z")

    with zipfile.ZipFile(sti) as arkiv:
        navn = next(n for n in arkiv.namelist() if n.endswith("markup.bcf"))
        topic = ET.fromstring(arkiv.read(navn)).find("Topic")

    tittel = topic.findtext("Title")
    assert len(tittel) <= 100
    assert tittel.startswith("K2:")
    assert "Pset_Revit_Data" in topic.findtext("Description")
