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


def test_kontroller_listes_i_cp1252_konsoll():
    """Kontrolltitlene har æ, ø og å."""
    resultat = kjor(["kontroller"], koding="cp1252")
    assert resultat.returncode == 0
    assert resultat.stdout.count("\n") >= 9
