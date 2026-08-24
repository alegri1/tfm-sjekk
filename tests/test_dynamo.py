"""Tester for koblingen tilbake til Revit (`dynamo/tfm_til_revit.py`).

Skriptet kjøres inne i Dynamo og kan ikke prøves der herfra. Den rene logikken
kan derimot prøves fullt ut, og det er den som kan ryke: fila den leser er
`funn.csv`, og kolonnene der eies av dette prosjektet.

Uten disse testene ville en endring i rapportformatet brutt koblingen uten at
noe sa fra — nøyaktig det mønsteret som har bitt seks ganger her.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "dynamo"))

from tfm_til_revit import (
    avvikstekster,
    grupper,
    har_tfm_kolonne,
    les_funn,
    ligner_tfm,
    sammendrag,
    statistikk,
    tfm_per_element,
)

from tfm_sjekk.modell import Alvorlighet, Funn, IfcObjekt
from tfm_sjekk.rapport import skriv_csv

TFM = "++115080=3600.001.04-JVZ001"


def objekt(global_id: str = "a") -> IfcObjekt:
    return IfcObjekt(
        global_id=global_id,
        ifc_klasse="IfcFlowTerminal",
        ifc_supertyper=["IfcProduct"],
        kildefil="rie.ifc",
        tfm_forekomst=TFM,
    )


def csv_funn(funn: list[Funn], tmp_path: Path) -> list[dict]:
    """Skriver funnene med prosjektets egen CSV-skriver og leser dem tilbake.

    Går veien om den ekte skriveren med vilje. En test som konstruerte radene
    for hånd ville fortsatt vært grønn den dagen kolonnenavnene endret seg.
    """
    sti = tmp_path / "funn.csv"
    skriv_csv(funn, sti)
    return les_funn(sti.read_text(encoding="utf-8-sig"))


# --- Lesing av fila ---


def test_bom_fjernes_saa_forste_kolonne_kan_slaas_opp(tmp_path):
    """Med BOM-en igjen heter første kolonne «﻿kontroll», og oppslaget

    på «kontroll» gir None uten at noe krasjer."""
    rader = csv_funn([Funn.for_objekt("K2", Alvorlighet.FEIL, "melding", objekt())], tmp_path)
    assert rader[0]["kontroll"] == "K2"


def test_skilletegnet_folger_rapporten(tmp_path):
    sti = tmp_path / "funn.csv"
    skriv_csv([Funn.for_objekt("K2", Alvorlighet.FEIL, "m", objekt())], sti)
    linjer = sti.read_text(encoding="utf-8-sig").splitlines()
    assert csv.Sniffer().sniff(linjer[0]).delimiter == ";"


def test_kolonnene_rapporten_skriver_er_de_koblingen_leser(tmp_path):
    """Låser kontrakten mellom rapportformatet og Dynamo-skriptet."""
    rader = csv_funn([Funn.for_objekt("K2", Alvorlighet.FEIL, "m", objekt())], tmp_path)
    assert {"kontroll", "alvorlighet", "melding", "global_id", "verdi"} <= set(rader[0])


# --- Hva som duger som nøkkel ---


@pytest.mark.parametrize(
    ("verdi", "ventet"),
    [
        (TFM, True),
        ("=3600.001.04-JVZ001", True),
        ("200", False),
        ("", False),
        (None, False),
    ],
)
def test_ligner_tfm(verdi, ventet):
    assert ligner_tfm(verdi) is ventet


def test_element_med_bare_et_k9_funn_kobles(tmp_path):
    """Tilfellet som falt ut i stillhet før «tfm»-kolonnen fantes.

    K9 legger MMI-verdien i «verdi». Uten en egen kolonne for elementets TFM
    hadde et element med BARE et K9-funn ingen nøkkel og ingen søskenrad å låne
    en fra — funnet forsvant uten et ord.
    """
    funn = [Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")]
    rader = csv_funn(funn, tmp_path)
    assert tfm_per_element(rader) == {"a": TFM}
    assert avvikstekster(rader, [TFM])[0].startswith("K9")


def test_mmi_verdien_blir_fortsatt_ikke_en_nokkel(tmp_path):
    """«200» skal aldri behandles som en TFM-ID å koble på."""
    funn = [Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", objekt(), verdi="200")]
    rader = csv_funn(funn, tmp_path)
    assert "200" not in grupper(rader)


def test_uten_tfm_kolonnen_utledes_nokkelen_som_for(tmp_path):
    """En rapport fra før kolonnen fantes skal fortsatt virke.

    Da faller koblingen tilbake på søskenrad-utledningen, og statistikken sier
    fra om at den gjorde det.
    """
    o = objekt()
    funn = [
        Funn.for_objekt("K8", Alvorlighet.FEIL, "kursnummer", o),
        Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", o, verdi="200"),
    ]
    gamle = [{k: v for k, v in rad.items() if k != "tfm"} for rad in csv_funn(funn, tmp_path)]

    assert not har_tfm_kolonne(gamle)
    assert tfm_per_element(gamle) == {"a": TFM}
    assert statistikk(gamle, [TFM])["nokkel_fra"] == "utledet av søskenrader"


def test_statistikken_sier_at_kolonnen_ble_brukt(tmp_path):
    rader = csv_funn([Funn.for_objekt("K2", Alvorlighet.FEIL, "m", objekt())], tmp_path)
    assert statistikk(rader, [TFM])["nokkel_fra"] == "tfm-kolonnen"


def test_soskenrad_gir_nokkelen_til_et_funn_uten_egen(tmp_path):
    """Elementet har både K8 (TFM i «verdi») og K9 (MMI i «verdi»).

    Uten dette ville K9-funnet aldri festet seg til noe element, og det ville
    forsvunnet i stillhet.
    """
    o = objekt()
    funn = [
        Funn.for_objekt("K8", Alvorlighet.FEIL, "kursnummer", o),
        Funn.for_objekt("K9", Alvorlighet.INFO, "MMI avviker", o, verdi="200"),
    ]
    rader = csv_funn(funn, tmp_path)
    assert tfm_per_element(rader) == {"a": TFM}
    assert len(grupper(rader)[TFM]) == 2


def test_funn_uten_element_kobles_ikke(tmp_path):
    """K7 melder om mastera, ikke om et objekt. Det har ingen global_id."""
    funn = [Funn(kontroll="K7", alvorlighet=Alvorlighet.INFO, melding="ikke modellert")]
    assert grupper(csv_funn(funn, tmp_path)) == {}


# --- Teksten som havner i schedulen ---


def test_avvikstekst_per_element(tmp_path):
    rader = csv_funn(
        [Funn.for_objekt("K2", Alvorlighet.FEIL, "For få siffer.", objekt())], tmp_path
    )
    tekster = avvikstekster(rader, [TFM, "++115080=3600.001.04-JVZ999", None])
    assert tekster[0] == "K2 feil: For få siffer."
    assert tekster[1] == ""
    assert tekster[2] == ""


def test_rekkefolgen_folger_elementene(tmp_path):
    """Dynamo kobler utdata mot elementene på indeks. Går den i utakt, havner
    avviket på feil objekt i modellen."""
    rader = csv_funn([Funn.for_objekt("K2", Alvorlighet.FEIL, "m", objekt())], tmp_path)
    verdier = ["x", TFM, "y", None, "z"]
    assert len(avvikstekster(rader, verdier)) == len(verdier)
    assert avvikstekster(rader, verdier)[1].startswith("K2")


def test_mange_funn_kortes_ned():
    rader = [
        {"kontroll": f"K{i}", "alvorlighet": "feil", "melding": "m", "verdi": TFM} for i in range(9)
    ]
    tekst = sammendrag(rader)
    assert tekst.count("\n") == 5
    assert "… og 4 til" in tekst


# --- Tallene som skiller «ingen avvik» fra «traff ingenting» ---


def test_statistikken_skiller_null_treff_fra_ingen_avvik(tmp_path):
    rader = csv_funn([Funn.for_objekt("K2", Alvorlighet.FEIL, "m", objekt())], tmp_path)

    traff = statistikk(rader, [TFM])
    bommet = statistikk(rader, ["helt-annet"])
    assert traff["elementer_med_avvik"] == 1
    assert bommet["elementer_med_avvik"] == 0
    assert bommet["tfm_verdier_uten_element"] == [TFM]


# --- Grafene: kopien inne i .dyn-fila kan ikke drive fra kilden ---

DYNAMO = Path(__file__).parent.parent / "dynamo"

GRAFER = {
    "tfm-sjekk-tfm-fra-revit.dyn": "tfm_fra_revit.py",
    "tfm-sjekk-tfm-til-revit.dyn": "tfm_til_revit.py",
}


def python_noden(dyn: Path) -> str:
    graf = json.loads(dyn.read_text(encoding="utf-8"))
    noder = [n for n in graf["Nodes"] if n.get("NodeType") == "PythonScriptNode"]
    assert len(noder) == 1, f"{dyn.name} har {len(noder)} Python-noder, venter én"
    return noder[0]["Code"]


@pytest.mark.parametrize(("dyn", "py"), sorted(GRAFER.items()))
def test_skriptkopien_i_grafen_er_lik_kilden(dyn, py):
    """Python-noden lagrer en kopi, ikke en peker.

    Den leser ikke fra `dynamo/*.py`, og den vet ikke at fila har endret seg.
    Det er ikke teoretisk: grafen beskrev seg selv med en nodekobling repoet
    dokumenterte som feil, mens ledningene var riktige. Tallene stemte,
    ingenting så galt ut, og ingenting sa fra.
    """
    i_grafen = python_noden(DYNAMO / dyn).replace("\r\n", "\n")
    i_repoet = (DYNAMO / py).read_text(encoding="utf-8").replace("\r\n", "\n")

    assert i_grafen == i_repoet, (
        f"{dyn} bærer en eldre kopi av {py}. Kjør «uv run python verktoy/oppdater-grafene.py»."
    )


@pytest.mark.parametrize("dyn", sorted(GRAFER))
def test_grafen_har_ingen_sti_fra_maskinen_den_ble_bygget_pa(dyn):
    """En graf som leveres med en sti hjem til den som bygget den, er ubrukelig.

    Verre: den peker på en fil som *kan* finnes hos noen andre. Plassholderne
    her er valgt for å feile høylytt — `les_fil` kaster på en sti som ikke
    finnes, og `merk` nekter å merke med plasseringskoden grafen leveres med.
    """
    tekst = (DYNAMO / dyn).read_text(encoding="utf-8")

    assert "Users" not in tekst
    assert "Desktop" not in tekst
