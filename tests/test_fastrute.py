"""Tester for evnen «fastrute» — en kjøring beskrevet ferdig i oppsettet.

Runden fra funn til rettet modell gjentas mange ganger, og hver gjentakelse
skulle ikke kreve at eksporten finnes igjen for hånd. Prisen er at ruten skrives
én gang og leses aldri igjen — derfor handler halvparten av testene her om at en
rute som ikke treffer noe sier fra framfor å levere en tom, grønn rapport.
"""

from __future__ import annotations

import pathlib
from pathlib import Path

from conftest import uten_ansi
from fixtures.syntetisk import GYLDIG, lag_modell
from test_cli import kjor

from tfm_sjekk.config import Konfigurasjon


def prosjekt(mappe: Path, oppsett: str, modeller: dict[str, Path | None] | None = None) -> Path:
    """En mappe med tfm-sjekk.toml og de modellene testen ber om."""
    mappe.mkdir(parents=True, exist_ok=True)
    (mappe / "tfm-sjekk.toml").write_text(oppsett, encoding="utf-8")
    for navn in modeller or {}:
        lag_modell([("IfcFlowTerminal", GYLDIG)], mappe / navn)
    return mappe


def test_relativ_sti_loses_mot_oppsettfila_ikke_arbeidskatalogen(tmp_path):
    """Oppsettet hører til prosjektet og skal kunne sendes til en kollega.

    Tolket mot arbeidskatalogen ville samme fil gitt ulikt resultat avhengig av
    hvor terminalen tilfeldigvis sto. Det er samme regel som for tabellene og
    mastera, og den er testet her fordi listefeltet har sin egen kodevei.
    """
    rot = tmp_path / "prosjekt"
    (rot / "eksport").mkdir(parents=True)
    lag_modell([("IfcFlowTerminal", GYLDIG)], rot / "eksport" / "rie.ifc")
    sti = rot / "tfm-sjekk.toml"
    sti.write_text('modeller = ["eksport/rie.ifc"]\n', encoding="utf-8")

    oppsett = Konfigurasjon.les(sti)
    (rå, _, treff) = oppsett.stier("modeller")[0]

    assert rå == "eksport/rie.ifc"
    assert treff == [(rot / "eksport" / "rie.ifc").resolve()]


def test_monsteret_gir_sortert_rekkefolge(tmp_path, monkeypatch):
    """Filsystemets egen rekkefølge er ikke lik mellom maskiner.

    Rapporttittelen og BCF-fila bygges av rekkefølgen, og BCF-en skal være
    byte-identisk for samme funn. Usortert ville den ikke vært det — og avviket
    ville bare vist seg hos noen andre. Derfor leverer glob-en her i motsatt
    rekkefølge: uten sorteringen ville testen sett riktig ut på denne maskinen.
    """
    rot = prosjekt(
        tmp_path, 'modeller = ["*.ifc"]\n', {"a.ifc": None, "b.ifc": None, "c.ifc": None}
    )

    ekte = pathlib.Path.glob
    monkeypatch.setattr(pathlib.Path, "glob", lambda s, m: reversed(list(ekte(s, m))))

    (_, _, treff) = Konfigurasjon.les(rot / "tfm-sjekk.toml").stier("modeller")[0]
    assert [p.name for p in treff] == ["a.ifc", "b.ifc", "c.ifc"]


def test_kjoring_uten_argumenter_leser_modellene_fra_oppsettet(tmp_path):
    rot = prosjekt(tmp_path, 'modeller = ["rie.ifc"]\nut = "rapport"\n', {"rie.ifc": None})

    resultat = kjor(["sjekk"], mappe=rot)

    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert (rot / "rapport" / "rapport.html").is_file()


def test_filargumenter_vinner_over_oppsettet(tmp_path):
    """Den faste ruten er for den gjentatte kjøringen.

    En enkeltfil skal kunne sjekkes uten å røre prosjektets oppsett — samme
    regel som flaggene for tabellene og mastera følger.
    """
    rot = prosjekt(tmp_path, 'modeller = ["rie.ifc"]\n', {"rie.ifc": None, "annen.ifc": None})

    resultat = kjor(["sjekk", "annen.ifc", "--ut", "ut"], mappe=rot)

    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "annen.ifc" in uten_ansi(resultat.stdout)
    assert "rie.ifc" not in uten_ansi(resultat.stdout)


def test_ut_flagget_vinner_over_oppsettet(tmp_path):
    rot = prosjekt(tmp_path, 'modeller = ["rie.ifc"]\nut = "fra-oppsettet"\n', {"rie.ifc": None})

    resultat = kjor(["sjekk", "--ut", "fra-flagget"], mappe=rot)

    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert (rot / "fra-flagget" / "rapport.html").is_file()
    assert not (rot / "fra-oppsettet").exists()


def test_rapportmappa_hentes_fra_oppsettet(tmp_path):
    rot = prosjekt(
        tmp_path, 'modeller = ["rie.ifc"]\nut = "leveranse/kontroll"\n', {"rie.ifc": None}
    )

    resultat = kjor(["sjekk"], mappe=rot)

    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert (rot / "leveranse" / "kontroll" / "rapport.html").is_file()


def test_monster_uten_treff_stopper_framfor_a_gi_tom_rapport(tmp_path):
    """En kjøring på null modeller gir en rapport uten funn.

    Den ser ut som en modell uten feil. Ruten leses aldri igjen etter at den er
    skrevet, så en eksport som havnet i feil mappe ville gitt grønt hver runde.
    """
    rot = prosjekt(tmp_path, 'modeller = ["eksport/*.ifc"]\nut = "rapport"\n')

    resultat = kjor(["sjekk"], mappe=rot)
    tekst = uten_ansi(resultat.stdout + resultat.stderr)

    assert resultat.returncode == 2, tekst
    assert "eksport/*.ifc" in tekst
    assert not (rot / "rapport").exists()


def test_ingen_modell_noe_sted_sier_hvor_den_kan_oppgis(tmp_path):
    rot = prosjekt(tmp_path, 'ifc_klasser = ["IfcFlowTerminal"]\n')

    resultat = kjor(["sjekk"], mappe=rot)
    tekst = uten_ansi(resultat.stdout + resultat.stderr)

    assert resultat.returncode == 2, tekst
    assert "tfm-sjekk.toml" in tekst


def test_samme_fil_leses_bare_en_gang(tmp_path):
    """To mønstre som overlapper ville lest fila to ganger.

    Da melder K6 hver eneste TFM-verdi som duplisert — en rapport som ser
    alvorlig ut og handler om oppsettet, ikke om modellen. Det har skjedd før,
    med en glob som sveipet med en kopi av elektromodellen.
    """
    rot = prosjekt(tmp_path, 'modeller = ["*.ifc", "rie.ifc"]\nut = "rapport"\n', {"rie.ifc": None})

    resultat = kjor(["sjekk"], mappe=rot)
    tekst = uten_ansi(resultat.stdout + resultat.stderr)

    assert resultat.returncode == 0, tekst
    assert "Leser 1 modell(er)" in tekst


def test_dra_og_slipp_beholder_rapporten_hos_modellen(tmp_path):
    """Dra-og-slipp peker på en bestemt fil, og rapporten skal dukke opp der.

    `_med_rapportmappe` setter `--ut` for dem, og et påsatt flagg vinner over
    oppsettet. Konsekvensen er tilsiktet: den faste ruten er for `.cmd`-fila,
    ikke for en fil brukeren nettopp slapp oppå programmet.
    """
    from tfm_sjekk.cli import _med_rapportmappe

    rot = prosjekt(tmp_path, 'modeller = ["rie.ifc"]\nut = "fra-oppsettet"\n', {"rie.ifc": None})
    modell = rot / "rie.ifc"

    argumenter = _med_rapportmappe(["sjekk", str(modell)])

    assert argumenter[-2] == "--ut"
    assert Path(argumenter[-1]) == rot / "rapport"
