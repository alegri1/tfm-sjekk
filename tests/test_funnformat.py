"""Tester for evnen «funnformat» — kontrakten de maskinlesbare rapportene gir.

Fila leses av skript, av en Dynamo-graf og av Excel. Et felt som betyr to ting
avhengig av hvilken kontroll som meldte, kan ikke brukes til noen av dem — og
det var nettopp det som skjedde: `verdi` bar TFM-ID-en for de fleste funn og
MMI-verdien for K9, uten at noe sa fra.
"""

from __future__ import annotations

import csv
import inspect
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import openpyxl

from tfm_sjekk.modell import Alvorlighet, Funn, IfcObjekt
from tfm_sjekk.rapport import skriv_bcf, skriv_csv, skriv_html, skriv_xlsx
from tfm_sjekk.rapport.csv_rapport import KOLONNER

TFM = "++115080=4310.001.14-QLF105"


def objekt(tfm: str | None = TFM, mmi: str | None = "200") -> IfcObjekt:
    return IfcObjekt(
        global_id="a",
        ifc_klasse="IfcOutlet",
        ifc_supertyper=["IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst=tfm,
        mmi=mmi,
    )


def rader(funn: list[Funn], tmp_path: Path) -> list[dict]:
    """Skriver med prosjektets egen CSV-skriver og leser tilbake.

    Går veien om den ekte skriveren med vilje: en test som konstruerte radene
    for hånd ville vært grønn den dagen kolonnene endret seg.
    """
    sti = tmp_path / "funn.csv"
    skriv_csv(funn, sti)
    linjer = sti.read_text(encoding="utf-8-sig").splitlines()
    return list(csv.DictReader(linjer, delimiter=";"))


# --- Hvert funn skal bære objektets egen TFM-verdi ---


def test_funn_om_tfm_verdien(tmp_path):
    r = rader([Funn.for_objekt("K2", Alvorlighet.FEIL, "syntaks", objekt())], tmp_path)[0]
    assert r["tfm"] == TFM


def test_funn_om_noe_annet_baerer_fortsatt_tfm(tmp_path):
    """K9 melder om MMI. «tfm» skal likevel være TFM-verdien."""
    funn = Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")
    r = rader([funn], tmp_path)[0]
    assert r["tfm"] == TFM
    assert r["verdi"] == "200"


def test_objekt_uten_tfm_gir_tomt_felt(tmp_path):
    funn = Funn.for_objekt("K1", Alvorlighet.FEIL, "mangler TFM", objekt(tfm=None))
    assert rader([funn], tmp_path)[0]["tfm"] == ""


def test_funn_uten_objekt_har_tomme_identitetsfelter(tmp_path):
    """K7 melder om mastera, ikke om et objekt."""
    funn = Funn(kontroll="K7", alvorlighet=Alvorlighet.INFO, melding="ikke modellert")
    r = rader([funn], tmp_path)[0]
    assert r["tfm"] == ""
    assert r["global_id"] == ""


# --- «verdi» beholder sin betydning ---


def test_de_to_feltene_kan_vaere_ulike(tmp_path):
    funn = Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")
    r = rader([funn], tmp_path)[0]
    assert r["tfm"] != r["verdi"]


def test_kontrollene_kan_ikke_sette_tfm():
    """Overstyrbarheten er nettopp det som gjorde «verdi» ubrukelig som nøkkel.

    Et felt som skal kunne stoles på, må ikke kunne settes av den som melder
    funnet. Låser at signaturen ikke tar det imot.
    """
    parametere = set(inspect.signature(Funn.for_objekt).parameters)
    assert "verdi" in parametere
    assert "tfm" not in parametere


# --- De maskinlesbare rapportene skal ha samme felter ---


def test_csv_og_xlsx_har_samme_felter(tmp_path):
    funn = [Funn.for_objekt("K2", Alvorlighet.FEIL, "syntaks", objekt())]

    csv_felter = set(rader(funn, tmp_path)[0])
    sti = tmp_path / "funn.xlsx"
    skriv_xlsx(funn, sti)
    ark = openpyxl.load_workbook(sti).active
    xlsx_kolonner = [c.value for c in ark[1]]

    assert "tfm" in csv_felter
    assert len(xlsx_kolonner) == len(KOLONNER)
    assert "TFM" in xlsx_kolonner


def test_xlsx_skriver_tfm_verdien(tmp_path):
    funn = [Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")]
    sti = tmp_path / "funn.xlsx"
    skriv_xlsx(funn, sti)
    ark = openpyxl.load_workbook(sti).active
    overskrifter = [c.value for c in ark[1]]
    rad = [c.value for c in ark[2]]
    verdier = dict(zip(overskrifter, rad, strict=True))
    assert verdier["TFM"] == TFM
    assert verdier["TFM-verdi"] == "200"


def test_kolonnelistene_kan_ikke_drive_fra_hverandre():
    """XLSX importerer KOLONNER fra CSV-skriveren.

    Legges en kolonne til uten en overskrift, feiler XLSX-skriveren med KeyError
    framfor å skrive en fil med feil antall kolonner.
    """
    from tfm_sjekk.rapport.xlsx import OVERSKRIFTER

    assert set(KOLONNER) <= set(OVERSKRIFTER)


# --- Rapporten til lesing og emnene til vieweren ---
#
# Prøven hviler på ett tilfelle: et funn der «tfm» og «verdi» er ulike. For alle
# andre funn er de like, og en test mot dem ville passert både før og etter at
# feilen ble rettet. Derfor er det alltid et K9-funn som brukes her.


def html(funn: list[Funn], tmp_path: Path) -> str:
    sti = tmp_path / "rapport.html"
    skriv_html(funn, sti, "test")
    return sti.read_text(encoding="utf-8")


def bcf_kommentarer(funn: list[Funn], tmp_path: Path) -> list[str]:
    """Kommentarteksten i hvert emne, som den står i zip-en."""
    sti = tmp_path / "funn.bcfzip"
    skriv_bcf(funn, sti, opprettet="2026-01-01T12:00:00Z")
    ut = []
    with zipfile.ZipFile(sti) as z:
        for navn in z.namelist():
            if navn.endswith("markup.bcf"):
                rot = ET.fromstring(z.read(navn).decode("utf-8"))
                # «Comment/Comment»: BCF pakker teksten i et element med samme
                # navn som beholderen. Leter man med iter(), treffer man
                # beholderen først, og dens tekst er bare innrykk — da blir
                # enhver «står ikke der»-test grønn uten å ha sett på noe.
                ut += [k.text or "" for k in rot.findall(".//Comment/Comment")]
    return ut


def test_html_viser_objektets_tfm_ikke_meldt_verdi(tmp_path):
    """K9 melder om MMI. Raden skal likevel identifisere objektet."""
    funn = [Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")]
    ut = html(funn, tmp_path)
    tabell = ut[ut.index("<table id=") :]
    assert TFM in tabell, "raden identifiserer ikke objektet sitt"
    assert "<code>200</code>" not in tabell, "MMI-verdien står i TFM-feltet"


def test_html_merker_kolonnen_tfm(tmp_path):
    """Overskriften skal ikke love «TFM-verdi» over noe som ikke er det."""
    ut = html([Funn.for_objekt("K2", Alvorlighet.FEIL, "syntaks", objekt())], tmp_path)
    assert ">TFM<" in ut
    assert ">TFM-verdi<" not in ut


def test_bcf_oppgir_objektets_tfm_ikke_meldt_verdi(tmp_path):
    funn = [Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")]
    kommentar = bcf_kommentarer(funn, tmp_path)[0]
    assert f"TFM: {TFM}" in kommentar
    assert "TFM-verdi: 200" not in kommentar


def test_bcf_beholder_meldinga_i_description(tmp_path):
    """Verdien funnet handler om går ikke tapt — den står i meldinga."""
    funn = [Funn.for_objekt("K9", Alvorlighet.INFO, "MMI «200» avviker", objekt(), verdi="200")]
    sti = tmp_path / "funn.bcfzip"
    skriv_bcf(funn, sti, opprettet="2026-01-01T12:00:00Z")
    with zipfile.ZipFile(sti) as z:
        navn = next(n for n in z.namelist() if n.endswith("markup.bcf"))
        rot = ET.fromstring(z.read(navn).decode("utf-8"))
    assert "200" in rot.find(".//Description").text


def test_html_uten_tfm_gir_tom_celle(tmp_path):
    """K1 melder at verdien mangler. Raden skal ikke motsi meldinga med «None»."""
    funn = [Funn.for_objekt("K1", Alvorlighet.FEIL, "mangler TFM", objekt(tfm=None))]
    ut = html(funn, tmp_path)
    assert "None" not in ut


def test_bcf_uten_tfm_utelater_leddet(tmp_path):
    funn = [Funn.for_objekt("K1", Alvorlighet.FEIL, "mangler TFM", objekt(tfm=None))]
    kommentar = bcf_kommentarer(funn, tmp_path)[0]
    assert "TFM" not in kommentar
    assert "None" not in kommentar


def test_funn_uten_objekt_gir_tomt_felt_i_begge(tmp_path):
    """K7 melder om mastera, ikke om et objekt."""
    funn = [Funn(kontroll="K7", alvorlighet=Alvorlighet.INFO, melding="ikke modellert")]
    assert "None" not in html(funn, tmp_path)
    assert "TFM" not in bcf_kommentarer(funn, tmp_path)[0]
