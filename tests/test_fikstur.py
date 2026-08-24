"""Tester for at fikstur-modellene har fast identitet.

Demomodellene fikk ny GlobalId hver gang de ble laget. En BCF skrevet før
forrige kjøring pekte da på objekter som ikke fantes, og BIMcollab svarte «None
of the viewpoint components are found in your project». Målt: null av 13
GUID-er matchet etter én regenerering.

Halve saken var alt løst: rapport/bcf.py utleder emne-GUID-ene av innholdet med
uuid5. Fiksturen gjorde det ikke.

Funntallet er det samme uansett, og alt annet ser likt ut. Byte-sammenligning er
den eneste prøven som fanger dette.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import ifcopenshell

sys.path.insert(0, str(Path(__file__).parent))
from fixtures.syntetisk import (
    GYLDIG,
    lag_elektromodell,
    lag_modell,
)

from tfm_sjekk.ifc.loader import les_modell
from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.rapport import skriv_bcf

OBJEKTER = [("IfcFlowTerminal", GYLDIG), ("IfcFlowTerminal", None)]
ELEKTRO = [
    {
        "navn": "Fordeling 1",
        "tfm": "++115080=4310.001.00-QLF001",
        "objekter": [{"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010"}],
    }
]


def test_to_kjoringer_gir_identiske_filer(tmp_path):
    a = lag_modell(OBJEKTER, tmp_path / "a" / "m.ifc", plassering=True)
    b = lag_modell(OBJEKTER, tmp_path / "b" / "m.ifc", plassering=True)
    assert a.read_bytes() == b.read_bytes()


def test_geometrimodellen_ogsaa(tmp_path):
    """Med geometri kommer GUID-ene også fra ifcopenshell.template.create.

    Det er et eget sted å glemme: prosjektet får sin identitet der, ikke i
    fiksturens egne create_entity-kall.
    """
    a = lag_elektromodell(ELEKTRO, tmp_path / "a" / "e.ifc", geometri=True)
    b = lag_elektromodell(ELEKTRO, tmp_path / "b" / "e.ifc", geometri=True)
    assert a.read_bytes() == b.read_bytes()


def test_en_bcf_overlever_at_modellen_lages_pa_nytt(tmp_path):
    """Selve saken: emnet skal fortsatt finne objektet sitt etterpå."""
    sti = tmp_path / "m.ifc"
    lag_modell(OBJEKTER, sti, plassering=True)
    objekt = les_modell(sti)[0]
    bcf = tmp_path / "funn.bcfzip"
    skriv_bcf(
        [Funn.for_objekt("K2", Alvorlighet.FEIL, "syntaks", objekt)],
        bcf,
        opprettet="2026-01-01T12:00:00Z",
    )

    sti.unlink()
    lag_modell(OBJEKTER, sti, plassering=True)
    finnes = {p.GlobalId for p in ifcopenshell.open(sti).by_type("IfcProduct")}

    with zipfile.ZipFile(bcf) as z:
        navn = next(n for n in z.namelist() if n.endswith(".bcfv"))
        pekt_paa = {
            c.get("IfcGuid")
            for c in ET.fromstring(z.read(navn).decode("utf-8")).findall(".//Component")
        }
    assert pekt_paa <= finnes, "emnet peker på objekter modellen ikke har lenger"


def test_samme_fro_gir_samme_rekke():
    from fixtures.syntetisk import guidgiver

    a, b = guidgiver("m.ifc"), guidgiver("m.ifc")
    assert [a() for _ in range(5)] == [b() for _ in range(5)]


def test_ulikt_fro_gir_ulik_rekke():
    """To filer i samme kjøring skal ikke dele identiteter."""
    from fixtures.syntetisk import guidgiver

    a, b = guidgiver("rie.ifc"), guidgiver("riv.ifc")
    assert not set(a() for _ in range(5)) & set(b() for _ in range(5))


def test_guid_ene_er_gyldige_ifc_identifikatorer():
    """22 tegn i IFCs base64-variant. En uuid-hex ville vært 32 og ulovlig."""
    from fixtures.syntetisk import guidgiver

    ny = guidgiver("m.ifc")
    for _ in range(20):
        g = ny()
        assert len(g) == 22, g
        assert set(g) <= set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$"), g
