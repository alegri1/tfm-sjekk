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


def test_dekningen_vises_ogsa_uten_funn(tmp_path):
    """Den rene rapporten er nettopp den en leser trenger å kunne stole på."""
    sti = skriv_html([], tmp_path / "r.html", "test", objekter=412, dekning={"ark.ifc": (0, 412)})
    html = sti.read_text(encoding="utf-8")

    assert "ark.ifc" in html
    assert "412" in html
    assert "Ingen funn" in html


def test_lest_og_i_omfanget_er_ulike_tall(tmp_path):
    """«objekter kontrollert» var antall leste objekter — den etiketten løy."""
    sti = skriv_html([], tmp_path / "r.html", "test", objekter=412, dekning={"ark.ifc": (0, 412)})
    html = sti.read_text(encoding="utf-8")

    assert "objekter kontrollert" in html
    assert "objekter lest" in html
    # Tallet ved «kontrollert» skal være omfanget, ikke antall leste.
    kontrollert = html.split("objekter kontrollert")[0].rsplit("<b>", 1)[1].split("</b>")[0]
    assert kontrollert == "0"


def test_hoppet_over_viser_grunnen(tmp_path):
    """Rapporten skal si det samme som konsollen.

    Sto det bare «Hoppet over: K3, K4», maatte den som fikk rapporten gjette
    om kontrollene var slaatt av eller om data manglet — motsatte handlinger.
    """
    from tfm_sjekk.kontroller import Hoppgrunn

    sti = skriv_html(
        [],
        tmp_path / "rapport.html",
        "modell.ifc",
        1,
        [
            ("K3", Hoppgrunn.MANGLER_KODETABELL.tekst, Hoppgrunn.MANGLER_KODETABELL.raad),
            ("K8", Hoppgrunn.SLATT_AV.tekst, Hoppgrunn.SLATT_AV.raad),
        ],
    )
    html = sti.read_text(encoding="utf-8")

    assert "--systemtabell" in html
    assert "slått av" in html
    assert "K3" in html and "K8" in html


def test_hoppet_over_bruker_bare_farger_som_finnes_i_begge_paletter(tmp_path):
    """En farge som bare finnes i den lyse paletten blir usynlig i den moerke.

    Det har skjedd her foer: moerk modus hadde 1,11:1 kontrast, og CSS-en var
    syntaktisk feilfri.
    """
    import re

    sti = skriv_html([], tmp_path / "rapport.html", "m.ifc", 1, [("K3", "ingen kodetabell", "")])
    html = sti.read_text(encoding="utf-8")

    regel = re.search(r"ul\.hoppet \{[^}]*\}", html).group(0)
    for variabel in re.findall(r"var\((--[a-zæøå-]+)\)", regel):
        lys = re.search(r":root \{[^}]*" + variabel + r":", html, re.S)
        assert lys, f"{variabel} mangler i den lyse paletten"
        assert html.count(variabel + ":") >= 2, f"{variabel} finnes bare i én palett"


def test_unntatt_fagmodell_markeres_ikke_som_advarsel(tmp_path):
    """Et bevisst unntak er ikke en forglemmelse.

    Rapporten viste tre oransje advarselstriper ved siden av «0 advarsler» —
    to paastander paa samme side som motsa hverandre. Konsollen sa
    «unntatt», tabellen sa «0».
    """
    sti = skriv_html(
        [],
        tmp_path / "rapport.html",
        "ark.ifc, rie.ifc",
        100,
        None,
        {"ark.ifc": (0, 7745), "rie.ifc": (1492, 2439)},
        ["ark.ifc"],
    )
    html = sti.read_text(encoding="utf-8")

    # Hele raden, ikke en enkelt linje: malen bryter lange rader over flere.
    rad = next(r for r in re.findall(r"<tr.*?</tr>", html, re.S) if "ark.ifc" in r)
    assert "unntatt" in rad
    assert "advarsel" not in rad


def test_uteglemt_fagmodell_markeres_fortsatt_som_advarsel(tmp_path):
    """Tomt omfang ved et uhell skal fortsatt se ut som noe aa se paa."""
    sti = skriv_html(
        [], tmp_path / "rapport.html", "ark.ifc", 100, None, {"ark.ifc": (0, 7745)}, []
    )
    html = sti.read_text(encoding="utf-8")

    assert 'class="advarsel"' in html


def test_unntatt_raden_bruker_ingen_farge_som_mangler_i_moerk_modus(tmp_path):
    import re

    sti = skriv_html([], tmp_path / "r.html", "m.ifc", 1, None, {"a.ifc": (0, 5)}, ["a.ifc"])
    html = sti.read_text(encoding="utf-8")

    regel = re.search(r"tr\.unntatt td \{[^}]*\}", html).group(0)
    for variabel in re.findall(r"var\((--[a-zæøå-]+)\)", regel):
        assert html.count(variabel + ":") >= 2, f"{variabel} finnes bare i én palett"


def test_kolonnen_for_uleselig_tfm_vises_bare_naar_noe_falt_ut(tmp_path):
    """En kolonne med null i hver rad i hver kjoering blir ikke lest."""
    uten = skriv_html([], tmp_path / "a.html", "m.ifc", 9, None, {"m.ifc": (9, 9)}, [], {})
    med = skriv_html([], tmp_path / "b.html", "m.ifc", 9, None, {"m.ifc": (9, 9)}, [], {"m.ifc": 3})

    assert "Uleselig TFM" not in uten.read_text(encoding="utf-8")
    html = med.read_text(encoding="utf-8")
    assert "Uleselig TFM" in html
    rad = next(r for r in re.findall(r"<tr.*?</tr>", html, re.S) if "m.ifc" in r and "<td>" in r)
    assert ">3<" in rad
