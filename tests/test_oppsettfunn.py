"""Tester for evnen «oppsettfunn» — hvordan verktøyet finner oppsettet sitt.

Alt dette er usynlig for brukeren med mindre verktøyet sier fra. En fil som
endrer resultatet uten at noen vet at den ble lest, er verre enn ingen fil — og
en sti som peker feil må ikke kunne se ut som et bevisst valg.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tfm_sjekk.config import Konfigurasjon, finn_oppsett


def oppsett(mappe: Path, innhold: str = "") -> Path:
    mappe.mkdir(parents=True, exist_ok=True)
    sti = mappe / "tfm-sjekk.toml"
    sti.write_text(innhold, encoding="utf-8")
    return sti


def modell(mappe: Path, navn: str = "rie.ifc") -> Path:
    mappe.mkdir(parents=True, exist_ok=True)
    sti = mappe / navn
    sti.write_text("", encoding="utf-8")
    return sti


# --- Å finne fila ---


def test_oppsettet_ligger_hos_modellen(tmp_path):
    m = modell(tmp_path / "modeller")
    oppsett(tmp_path / "modeller")
    funnet = finn_oppsett([m], tmp_path / "annet")
    assert funnet.parent.name == "modeller"


def test_oppsettet_ligger_i_arbeidskatalogen(tmp_path):
    m = modell(tmp_path / "modeller")
    (tmp_path / "annet").mkdir()
    oppsett(tmp_path / "annet")
    funnet = finn_oppsett([m], tmp_path / "annet")
    assert funnet.parent.name == "annet"


def test_modellens_mappe_har_forrang(tmp_path):
    """Ved dra-og-slipp er arbeidskatalogen exe-ens egen mappe.

    Den har ikke noe med prosjektet å gjøre — samme innsikt som ligger bak at
    rapporten legges hos modellen.
    """
    m = modell(tmp_path / "modeller")
    oppsett(tmp_path / "modeller")
    oppsett(tmp_path / "annet")
    assert finn_oppsett([m], tmp_path / "annet").parent.name == "modeller"


def test_ingen_finnes(tmp_path):
    m = modell(tmp_path / "modeller")
    (tmp_path / "annet").mkdir()
    assert finn_oppsett([m], tmp_path / "annet") is None


def test_uten_modeller_letes_det_i_arbeidskatalogen(tmp_path):
    oppsett(tmp_path / "annet")
    assert finn_oppsett([], tmp_path / "annet") is not None


# --- Stier tolkes relativt til fila ---


def test_relativ_sti_loses_mot_konfigurasjonsfila(tmp_path):
    """Kjørt fra en helt annen mappe skal stien fortsatt peke riktig."""
    (tmp_path / "tabeller").mkdir()
    (tmp_path / "tabeller" / "ns3451.csv").write_text("", encoding="utf-8")
    sti = oppsett(tmp_path, 'systemtabell = "tabeller/ns3451.csv"\n')

    k = Konfigurasjon.les(sti)
    assert k.sti("systemtabell") == (tmp_path / "tabeller" / "ns3451.csv").resolve()


def test_sti_over_konfigurasjonsfila(tmp_path):
    (tmp_path / "modeller").mkdir()
    (tmp_path / "TFM-master.csv").write_text("", encoding="utf-8")
    sti = oppsett(tmp_path / "modeller", 'tfm_master = "../TFM-master.csv"\n')

    k = Konfigurasjon.les(sti)
    assert k.sti("tfm_master") == (tmp_path / "TFM-master.csv").resolve()


def test_absolutt_sti_star_urort(tmp_path):
    absolutt = (tmp_path / "et-annet-sted.csv").resolve()
    sti = oppsett(tmp_path, f'tfm_master = "{absolutt.as_posix()}"\n')
    assert Konfigurasjon.les(sti).sti("tfm_master") == absolutt


def test_uten_fil_er_det_ingen_kilde():
    k = Konfigurasjon()
    assert k.kilde is None
    assert k.sti("tfm_master") is None


def test_kilde_folger_ikke_med_i_serialisering(tmp_path):
    """`kilde` er hvor fila lå, ikke en innstilling.

    Kom den med i utdata, ville et forslag fra «oppsett» skrevet maskinstien
    til den som leste det inn i fila til den neste.
    """
    sti = oppsett(tmp_path, 'tfm_master = "m.csv"\n')
    assert "kilde" not in Konfigurasjon.les(sti).model_dump()


# --- Ikke oppgitt er fortsatt et valg ---


@pytest.mark.parametrize("felt", ["tfm_master", "systemtabell", "komponenttabell"])
def test_ikke_oppgitt_gir_ingen_sti(tmp_path, felt):
    assert Konfigurasjon.les(oppsett(tmp_path)).sti(felt) is None
