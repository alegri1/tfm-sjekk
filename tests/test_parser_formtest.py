"""Formtesten: er strengen gjenkjennelig som en TFM-ID?

Strengene er de fjorten fra utforskingen som ledet til kravet. De to gruppene
er det testen skal skille: verdier som aldri var TFM-ID-er, og TFM-ID-er som
er ødelagt på hver sin måte.
"""

from __future__ import annotations

import pytest

from tfm_sjekk.parser import ligner_tfm_id

IKKE_TFM = [
    ("Systemair", "fabrikat"),
    ("DVCompact 4", "modell"),
    ("84 kg", "vekt"),
    ("sjekket av RIE 12.03", "kommentar"),
    ("A-1000", "internt merke"),
    ("Kurs 12-3", "kurstekst"),
    ("JVZ001", "bare komponentforekomst"),
    ("3600.001.04", "bare systemforekomst"),
    ("", "tom"),
]

ODELAGT_TFM = [
    ("115080=3600.001.04-JVZ001", "mangler ++"),
    ("++115080-3600.001.04", "mangler ="),
    ("++11508=3600.001.04-JVZ001", "fem siffer i plasseringen"),
    ("++115080=3600.001.4-JVZ001", "kort undernummer"),
    ("++115080=3600.001.04-jvz001", "små bokstaver"),
]


@pytest.mark.parametrize(("streng", "hva"), IKKE_TFM)
def test_forkaster_verdier_som_ikke_er_tfm(streng, hva):
    assert not ligner_tfm_id(streng), hva


@pytest.mark.parametrize(("streng", "hva"), ODELAGT_TFM)
def test_godtar_odelagte_tfm_ider(streng, hva):
    assert ligner_tfm_id(streng), hva


def test_gyldig_tfm_id_er_gjenkjennelig():
    assert ligner_tfm_id("++115080=3600.001.04-JVZ001%JVZ.001.008")
