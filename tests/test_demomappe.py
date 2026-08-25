"""Tester for evnen «demomappe» — at mappa er en utdata og ikke et sted man redigerer.

Byggingen kan ikke prøves i sin helhet herfra: den henter en binær fra en
utgivelse og kjører den i minutter. Det som *kan* prøves er alt som avgjør om
resultatet er til å stole på — at kopiene er kopier, at et manglende ledd stopper
byggingen, og at et tall ingen målte aldri havner i teksten.

Det siste er hele grunnen til at evnen finnes. Tre tall var gale samtidig i
august 2026, og ett av dem var skrevet en time før det ble oppdaget.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "verktoy"))

from lag_demomappe import (
    FRA_REVIT,
    KOPIER,
    MAL,
    Byggefeil,
    kopier_kildene,
    lag_modellene,
    sjekk_revitfilene,
    skriv_les_meg,
    skriv_oppsettet,
)

ROT = Path(__file__).parent.parent


@pytest.fixture(scope="session", autouse=True)
def modellene_finnes():
    """De halve kildene i KOPIER er GENERERTE og gitignorerte.

    `demo-*.ifc`, `avveie.ifc`, `blindsone.ifc`, `tidligfase.ifc` og
    `foringsvei.ifc` finnes på maskinen til den som har kjørt generatoren, og
    aldri i en fersk klone. Uten dette gikk testene her grønt hos meg og røk på
    alle tre plattformene i CI — samme feil som `.gitignore` som skjulte hele
    `rapport/`-pakken, og av samme grunn: tilstand på min disk.

    Byggingen kaller den samme funksjonen, så fiksturen prøver den også — og
    den er da det eneste som knytter KOPIER-tabellen til at filene faktisk
    lages. En skrivefeil i et av navnene ville ellers først vist seg i en ekte
    bygging.
    """
    lag_modellene()


def mappe_med_revitfiler(tmp_path: Path) -> Path:
    """En mappe der forutsetningene er på plass, men ingenting er bygget."""
    for navn in FRA_REVIT:
        (tmp_path / navn).write_bytes(b"attrapp")
    return tmp_path


def alle_verdier() -> dict[str, str]:
    """En verdi til hver plassholder malen har, uten å måle noe."""
    return {navn: "0" for navn in re.findall(r"\{([a-z_]+)\}", MAL.read_text(encoding="utf-8"))}


# --- Kopiene er kopier ------------------------------------------------------


def test_hver_kopi_er_lik_kilden_sin(tmp_path):
    kopier_kildene(tmp_path)

    for navn, kilde in KOPIER.items():
        assert (tmp_path / navn).read_bytes() == (ROT / kilde).read_bytes(), navn


def test_en_redigert_kopi_overskrives(tmp_path):
    """Kilden er repoet. En endring gjort i mappa er tapt ved neste bygging.

    Det er meningen: femten av tjueto filer var kopier, og en kopi som
    redigeres på ett av to steder er ikke en kopi lenger — uten at noe sier fra.
    """
    kopier_kildene(tmp_path)
    navn = next(iter(KOPIER))
    (tmp_path / navn).write_bytes(b"noen har rort denne")

    kopier_kildene(tmp_path)

    assert (tmp_path / navn).read_bytes() == (ROT / KOPIER[navn]).read_bytes()


def test_manglende_kilde_navngis(tmp_path, monkeypatch):
    monkeypatch.setitem(KOPIER, "oppdiktet.csv", "eksempler/finnes-ikke.csv")

    with pytest.raises(Byggefeil, match=re.escape("finnes-ikke.csv")):
        kopier_kildene(tmp_path)


# --- Revit-filene er en forutsetning, ikke en utdata ------------------------


def test_manglende_revitfil_stopper_byggingen(tmp_path):
    mappe = mappe_med_revitfiler(tmp_path)
    (mappe / FRA_REVIT[1]).unlink()

    with pytest.raises(Byggefeil, match=re.escape(FRA_REVIT[1])):
        sjekk_revitfilene(mappe)


def test_revitfilene_rores_ikke(tmp_path):
    """De er det eneste i mappa som ikke kan lages på nytt."""
    mappe = mappe_med_revitfiler(tmp_path)
    for navn in FRA_REVIT:
        (mappe / navn).write_bytes(b"ekte innhold")

    sjekk_revitfilene(mappe)
    kopier_kildene(mappe)
    skriv_oppsettet(mappe)

    for navn in FRA_REVIT:
        assert (mappe / navn).read_bytes() == b"ekte innhold", navn


# --- Tallene måles, de skrives ikke -----------------------------------------


def test_malen_inneholder_ingen_kjoringstall():
    """Et tall i malen er et tall ingen målte.

    Historiske tall står igjen med vilje — «969 kilometer», «1029 funn før
    v0.4.0» — de beskriver noe som var, ikke noe kjøringen ga. Vakten her er de
    formene som pleide å bære et målt tall.
    """
    mal = MAL.read_text(encoding="utf-8")

    mistenkte = [
        linje
        for linje in mal.split("\n")
        if re.search(r"-> +\d|^\s*\d+ funn|, \d+ funn|\d+ av \d+ objekter", linje)
        and "{" not in linje
    ]
    assert not mistenkte, "tall som ser målte ut, men ikke er det:\n" + "\n".join(mistenkte)


def test_en_plassholder_uten_verdi_stopper_skrivingen(tmp_path):
    verdier = alle_verdier()
    manglende = verdier.popitem()[0]

    with pytest.raises(Byggefeil, match=manglende):
        skriv_les_meg(tmp_path, verdier)

    assert not (tmp_path / "LES-MEG.txt").exists()


def test_et_tall_lagt_til_i_malen_uten_maaling_stopper_skrivingen(tmp_path, monkeypatch):
    """`str.format` kaster på plassholder uten verdi, ikke omvendt.

    Legger noen et tall i malen uten å måle det, ville teksten blitt skrevet med
    «{nytt_tall}» stående midt i. Det ser ut som en skrivefeil og ikke som en
    manglende måling, og mottakeren kan ikke vite hvilken.
    """
    falsk = tmp_path / "mal.txt"
    falsk.write_text("Du får {umalt} funn.\n", encoding="utf-8")
    monkeypatch.setattr("lag_demomappe.MAL", falsk)

    with pytest.raises(Byggefeil, match="umalt"):
        skriv_les_meg(tmp_path, {})


# --- Fila slik Notisblokk vil ha den ----------------------------------------


def test_les_meg_skrives_med_bom_crlf_og_ingen_tabulator(tmp_path):
    skriv_les_meg(tmp_path, alle_verdier())

    raa = (tmp_path / "LES-MEG.txt").read_bytes()
    tekst = raa.decode("utf-8-sig")

    assert raa[:3] == b"\xef\xbb\xbf"
    assert tekst.count("\n") == tekst.count("\r\n")
    assert chr(9) not in tekst


def test_oppsettet_baerer_ruten_men_ikke_tabellene(tmp_path):
    """Mappa er ikke ett prosjekt, den er flere uavhengige demoer.

    Tabellene i oppsettet ville gjeldt for hver kjøring der, og
    snowdon-tfm.ifc skal med vilje kjøre uten dem.
    """
    skriv_oppsettet(tmp_path)
    toml = (tmp_path / "tfm-sjekk.toml").read_text(encoding="utf-8")
    # Bytes, ikke read_text: universelle linjeskift ville skjult CRLF-en, og
    # cmd.exe er en av konsumentene som faktisk bryr seg om den.
    cmd = (tmp_path / "kjor.cmd").read_bytes().decode("ascii")

    assert "modeller = [" in toml
    assert 'ut = "rapport"' in toml
    assert not re.search(r"^\s*systemtabell\s*=", toml, re.M)
    assert "--systemtabell" in cmd
    assert cmd.endswith("pause\r\n")
