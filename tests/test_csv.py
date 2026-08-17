"""Tester for CSV-rapporten (§5).

CSV-en skal kunne dobbeltklikkes i Excel *og* leses av et program. De to
ønskene trekker i hver sin retning — «sep=;»-linja er en Excel-konvensjon,
ikke CSV — så begge sidene er testet her.
"""

from __future__ import annotations

import csv

from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.rapport import skriv_csv


def funn() -> list[Funn]:
    return [
        Funn(
            kontroll="K6",
            alvorlighet=Alvorlighet.FEIL,
            melding="Komponentforekomsten «++115080=4310.001.12-QLF001» er brukt to ganger.",
            global_id="1hqA2bC3dE4fG5hI6jK7lM",
            ifc_klasse="IfcFlowTerminal",
            kildefil="demo-rie.ifc",
            verdi="++115080=4310.001.12-QLF001",
        )
    ]


def linjer(sti) -> list[str]:
    return sti.read_text(encoding="utf-8-sig").splitlines()


def test_sep_linja_star_forst(tmp_path):
    """Uten den havner hele rapporten i kolonne A i Excel på web."""
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    assert linjer(sti)[0] == "sep=;"
    assert linjer(sti)[1].startswith("kontroll;alvorlighet")


def test_ren_csv_starter_pa_overskriftsraden(tmp_path):
    sti = skriv_csv(funn(), tmp_path / "ren.csv", sep_linje=False)
    assert linjer(sti)[0].startswith("kontroll;alvorlighet")


def test_bom_beholdes(tmp_path):
    """Excel trenger BOM-en for å skjønne at æ, ø og å er UTF-8."""
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    assert sti.read_bytes().startswith(b"\xef\xbb\xbf")


def test_kan_leses_programmatisk_ved_a_hoppe_over_sep_linja(tmp_path):
    sti = skriv_csv(funn(), tmp_path / "funn.csv")
    tekst = sti.read_text(encoding="utf-8-sig").splitlines()
    rader = list(csv.DictReader(tekst[1:], delimiter=";"))
    assert rader[0]["kontroll"] == "K6"
    assert rader[0]["global_id"] == "1hqA2bC3dE4fG5hI6jK7lM"


def test_ren_csv_leses_uten_a_hoppe_over_noe(tmp_path):
    sti = skriv_csv(funn(), tmp_path / "ren.csv", sep_linje=False)
    rader = list(csv.DictReader(sti.read_text(encoding="utf-8-sig").splitlines(), delimiter=";"))
    assert rader[0]["alvorlighet"] == "feil"


def test_semikolon_i_meldingen_siteres(tmp_path):
    """Ellers ville meldinga sprengt kolonnene."""
    med_semikolon = funn()
    med_semikolon[0].melding = "Fant 4310.001.12; forventet 4310.001.13"
    sti = skriv_csv(med_semikolon, tmp_path / "sitat.csv")
    rader = list(csv.DictReader(linjer(sti)[1:], delimiter=";"))
    assert rader[0]["melding"] == "Fant 4310.001.12; forventet 4310.001.13"
