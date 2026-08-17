"""Tester for CSV-rapporten (§5).

CSV-en er det maskinlesbare formatet: den skal kunne leses rett fram av
`csv`-modulen, pandas og `Import-Csv`. Excel-jobben ligger i XLSX-en — se
test_xlsx.py og docstringen i csv_rapport.
"""

from __future__ import annotations

import csv

from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.rapport import skriv_csv

NORSK = "«++11508=4310.001.12-QLF005» følger ikke TFM-grammatikken. Blåbærsyltetøy."


def funn() -> list[Funn]:
    return [
        Funn(
            kontroll="K2",
            alvorlighet=Alvorlighet.FEIL,
            melding=NORSK,
            global_id="1hqA2bC3dE4fG5hI6jK7lM",
            ifc_klasse="IfcFlowTerminal",
            kildefil="demo-rie.ifc",
            verdi="++11508=4310.001.12-QLF005",
        )
    ]


def test_starter_pa_overskriftsraden(tmp_path):
    """Ingen «sep=»-linje: den fikk Excel til å ignorere BOM-en, og da ble
    «følger» til «fÃ¸lger»."""
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    assert sti.read_text(encoding="utf-8-sig").splitlines()[0].startswith("kontroll;alvorlighet")


def test_bom_star_forst(tmp_path):
    """BOM-en er det eneste signalet Excel har om at fila er UTF-8."""
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    rå = sti.read_bytes()
    assert rå.startswith(b"\xef\xbb\xbf")
    assert rå[3:4].isalpha()  # rett på overskriften, ingenting imellom


def test_norske_tegn_overlever_rundturen(tmp_path):
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    tekst = sti.read_text(encoding="utf-8-sig")
    assert NORSK in tekst
    assert "Ã¸" not in tekst and "Â«" not in tekst


def test_leses_rett_fram(tmp_path):
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    rader = list(csv.DictReader(sti.read_text(encoding="utf-8-sig").splitlines(), delimiter=";"))
    assert rader[0]["kontroll"] == "K2"
    assert rader[0]["melding"] == NORSK


def test_semikolon_i_meldingen_siteres(tmp_path):
    """Ellers ville meldinga sprengt kolonnene."""
    med_semikolon = funn()
    med_semikolon[0].melding = "Fant 4310.001.12; forventet 4310.001.13"
    sti = skriv_csv(med_semikolon, tmp_path / "sitat.csv")
    rader = list(csv.DictReader(sti.read_text(encoding="utf-8-sig").splitlines(), delimiter=";"))
    assert rader[0]["melding"] == "Fant 4310.001.12; forventet 4310.001.13"
