"""Tester for kommandolinja, kjørt som egen prosess.

CliRunner fanger utdata i sin egen strøm og sier derfor ingenting om hva som
skjer i en ekte terminal. Testene her starter en faktisk prosess, fordi det
er den eneste måten å treffe kodesida i konsollen på — og det er nettopp der
exit-koden kan bli feil av grunner som ikke har noe med modellen å gjøre.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from conftest import uten_ansi
from fixtures.syntetisk import GYLDIG, lag_modell


def kjor(argumenter: list[str], koding: str | None = None) -> subprocess.CompletedProcess:
    miljo = dict(os.environ)
    if koding:
        miljo["PYTHONIOENCODING"] = koding
    return subprocess.run(
        [sys.executable, "-m", "tfm_sjekk.cli", *argumenter],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=miljo,
    )


def test_ren_modell_gir_exit_0(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr


def test_modell_med_feil_gir_exit_1(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", None)], tmp_path / "feil.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 1


def test_exit_koden_overlever_en_cp1252_konsoll(tmp_path):
    """«→» i oppsummeringslinja finnes ikke i cp1252.

    Uten omkodingen i cli-en kastet den avsluttende utskriften
    UnicodeEncodeError etter at rapportene var skrevet, og en ren modell fikk
    exit 1 — altså «underkjent» av kodesida i terminalen, ikke av kontrollene.
    Dette er standardoppsettet på en norsk Windows-maskin (§6: BIM-koordinatorer
    kjører Windows).
    """
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor(["sjekk", str(modell), "--ut", str(tmp_path / "ut")], koding="cp1252")

    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "UnicodeEncodeError" not in resultat.stderr
    assert "advarsler" in resultat.stdout  # oppsummeringslinja kom ut


def test_federering_over_prosessgrensa(tmp_path):
    """`python -m tfm_sjekk` med flere filer starter arbeidsprosesser, og de
    importerer __main__ på nytt. Uten `if __name__`-vakta ville hele
    kontrollkjøringen startet om igjen i hvert barn."""
    modeller = [
        str(lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / f"m{i}.ifc")) for i in range(3)
    ]
    resultat = kjor(["sjekk", *modeller, "--ut", str(tmp_path / "ut")])

    assert resultat.returncode == 1, resultat.stdout + resultat.stderr  # K6: samme ID i tre filer
    assert resultat.stdout.count("Leser 3 modell(er)") == 1, "kjørte flere ganger"
    assert "multiprocessing-fork" not in resultat.stderr


def test_filsti_forst_virker_uten_kommandoord(tmp_path):
    """Dra-og-slipp i Utforskeren sender bare filstier — «sjekk» settes inn."""
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "ren.ifc")
    resultat = kjor([str(modell), "--ut", str(tmp_path / "ut")])
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "advarsler" in resultat.stdout


def test_skrivefeil_i_kommandoen_gir_fortsatt_kommandofeil():
    """«sjekk» settes bare inn foran stier som finnes. Ellers ville en
    skrivefeil gitt «Path does not exist» i stedet for noe forståelig."""
    resultat = kjor(["kontrolller"])
    assert resultat.returncode != 0
    assert "No such command" in uten_ansi(resultat.stdout + resultat.stderr)


def test_standardkommando_er_rein_argumentbehandling():
    from tfm_sjekk.cli import _med_standardkommando

    assert _med_standardkommando([]) == []
    assert _med_standardkommando(["kontroller"]) == ["kontroller"]
    assert _med_standardkommando(["--help"]) == ["--help"]
    assert _med_standardkommando(["finnes-ikke.ifc"]) == ["finnes-ikke.ifc"]


def test_rapportmappa_legges_hos_modellen(tmp_path):
    """Ved dobbeltklikk er arbeidskatalogen exe-ens egen mappe, ikke modellens."""
    from tfm_sjekk.cli import _med_rapportmappe

    modell = tmp_path / "modell.ifc"
    modell.write_text("")

    ut = _med_rapportmappe(["sjekk", str(modell)])
    assert ut[-2] == "--ut"
    assert Path(ut[-1]) == tmp_path / "rapport"

    # Har brukeren sagt --ut selv, skal vi ikke overstyre.
    eget = ["sjekk", str(modell), "--ut", "et-annet-sted"]
    assert _med_rapportmappe(eget) == eget


def test_kontroller_listes_i_cp1252_konsoll():
    """Kontrolltitlene har æ, ø og å."""
    resultat = kjor(["kontroller"], koding="cp1252")
    assert resultat.returncode == 0
    assert resultat.stdout.count("\n") >= 9
