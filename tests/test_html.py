"""Tester for HTML-rapporten (§5).

«Én selvstendig fil» er et krav med to sider: ingen eksterne ressurser, og
ingen antakelser om mottakerens oppsett. Rapporten var en stund uleselig i
mørk modus — overskriftsraden hadde fast lys bakgrunn mens teksten arvet
browserens lyse standardfarge — og testene her holder på begge sidene.
"""

from __future__ import annotations

import re

from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.rapport import skriv_html

MAL_KILDE = "src/tfm_sjekk/rapport/html.py"


def funn() -> list[Funn]:
    return [
        Funn(
            kontroll="K8",
            alvorlighet=Alvorlighet.FEIL,
            melding="Elektroobjekt i system 4310 mangler kurs-/sløyfenummer.",
            global_id="1hqA2bC3dE4fG5hI6jK7lM",
            ifc_klasse="IfcLamp",
            kildefil="demo-elektro.ifc",
            verdi="++115080=4310.001.00-QLF002",
        )
    ]


def skriv(tmp_path, funnliste=None) -> str:
    sti = skriv_html(funnliste if funnliste is not None else funn(), tmp_path / "r.html", "test")
    return sti.read_text(encoding="utf-8")


def test_ingen_eksterne_ressurser(tmp_path):
    """Skal kunne åpnes på en maskin uten nett."""
    html = skriv(tmp_path)
    for mønster in ("http://", "https://", "<link", "@import", "src="):
        assert mønster not in html


def test_tegnkoding_deklareres(tmp_path):
    """Fila skrives uten BOM, så meta-taggen er det browseren har å gå etter."""
    html = skriv(tmp_path)
    assert '<meta charset="utf-8">' in html
    assert "sløyfenummer" in html


def test_body_setter_bakgrunn_og_tekstfarge(tmp_path):
    """Uten dem arver sida browserens standardfarger, og de følger mørk modus
    selv om fargene i malen ikke gjør det."""
    html = skriv(tmp_path)
    body = re.search(r"\n  body \{(.+?)\}", html, re.DOTALL)
    assert body is not None
    assert "background: var(--bg)" in body.group(1)
    assert "color: var(--tekst)" in body.group(1)


def test_overskriftsraden_setter_egen_tekstfarge(tmp_path):
    """Den konkrete feilen: fast lys bakgrunn + arvet lys tekst = hvit på hvitt."""
    html = skriv(tmp_path)
    th = re.search(r"\n  th \{(.+?)\}", html, re.DOTALL)
    assert th is not None
    assert "background: var(--th-bg)" in th.group(1)
    assert "color: var(--tekst)" in th.group(1)


def test_morkt_skjema_bytter_bare_ut_kjente_farger(tmp_path):
    """Regelen som ble brutt: ingen farge skal ha sin eneste definisjon inne i
    mørk-modus-blokka. Da mangler den for alle andre."""
    html = skriv(tmp_path)

    mork = re.search(r"@media \(prefers-color-scheme: dark\) \{(.+?)\n  \}", html, re.DOTALL)
    assert mork is not None, "mangler mørk-modus-blokk"

    i_lys = set(re.findall(r"(--[a-zæøå-]+):", html.split("@media")[0]))
    i_mork = set(re.findall(r"(--[a-zæøå-]+):", mork.group(1)))

    assert i_mork, "mørk-modus-blokka definerer ingen farger"
    assert i_mork <= i_lys, f"bare definert for mørk modus: {sorted(i_mork - i_lys)}"


def test_alle_variabler_som_brukes_er_definert(tmp_path):
    html = skriv(tmp_path)
    brukt = set(re.findall(r"var\((--[a-zæøå-]+)\)", html))
    definert = set(re.findall(r"(--[a-zæøå-]+):", html))
    assert brukt <= definert, f"udefinerte variabler: {sorted(brukt - definert)}"


def test_tom_rapport_sier_fra(tmp_path):
    html = skriv(tmp_path, [])
    assert "Ingen funn" in html
