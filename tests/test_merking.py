"""Tester for merkingen inn i Revit (`dynamo/tfm_fra_revit.py`).

Skriptet kjøres inne i Dynamo og kan ikke prøves der herfra. Den rene logikken
kan derimot prøves fullt ut, og det er den som avgjør om modellen blir merket
riktig — en TFM-ID med feil format gir K2 på hvert eneste objekt, og da sier
rapporten ingenting om noe.

Den viktigste prøven her er ikke at formatet stemmer, men at grafen og
IFC-injektoren ikke kan drive fra hverandre. De utleder de samme kodene av de
samme familienavnene, fra hver sin side av eksporten.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "dynamo"))

from tfm_fra_revit import (
    FAMILIER,
    STANDARD,
    familiekode,
    kursnummer,
    merk,
    sammendrag,
    statistikk,
    tfm_id,
)

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.parser import parse

PLASSERING = "115080"


# --- Kodene utledes av familienavnet ---


def test_kjent_familie():
    assert familiekode("Downlight") == ("4320", "QLF")


def test_treffer_paa_begynnelsen():
    """«Downlight 150mm» og «Downlight 200mm» er samme slags objekt."""
    assert familiekode("Downlight 150mm") == familiekode("Downlight 200mm")


def test_typenavn_etter_kolon_ignoreres():
    """Revit gir «Familie: Type». Bare familien betyr noe her."""
    assert familiekode("Duplex Receptacle: 20A") == ("4330", "QLS")


def test_ukjent_familie_faar_en_kode_framfor_ingenting():
    """Et objekt uten TFM gir K1, og da ser modellen umerket ut.

    En kode verktøyet kan avvise sier «denne familien er ukjent for tabellen».
    Ingen TFM sier «dette objektet er ikke merket», som er noe annet.
    """
    assert familiekode("Vindusvasker 3000") == STANDARD


def test_tomt_familienavn_er_ufarlig():
    assert familiekode(None) == STANDARD
    assert familiekode("") == STANDARD


# --- Kursnummeret leses av Revits egen fritekst ---


@pytest.mark.parametrize(
    "rå, ventet",
    [
        ("1", "01"),
        ("12", "12"),
        ("6,8", "06"),  # to kurser — TFM har plass til én
        ("2,4", "02"),
        ("", "00"),
        (None, "00"),
        ("EM1", "01"),  # bokstaver rundt tallet
        ("Spare", "00"),  # ingen siffer i det hele tatt
    ],
)
def test_kursnummer(rå, ventet):
    assert kursnummer(rå) == ventet


# --- ID-en skal kunne leses av verktøyets egen parser ---


def test_id_en_parser():
    """Den strengeste prøven: grammatikken er verktøyets, ikke grafens."""
    id_ = tfm_id(PLASSERING, "4320", "12", "QLF", 7)
    assert id_ == "++115080=4320.001.12-QLF007"
    parse(id_, Konfigurasjon().grammatikk)  # kaster ved feil format


def test_hele_merkingen_parser():
    familier = ["Downlight", "Duplex Receptacle", "Conduit", "Ukjent"]
    kurser = ["1", "6,8", "", "3"]
    for id_ in merk(familier, kurser, PLASSERING):
        parse(id_, Konfigurasjon().grammatikk)


# --- Løpenummeret er det som holder K6 i sjakk ---


def test_lopenummer_telles_per_systemforekomst():
    ut = merk(["Downlight"] * 3, ["1", "1", "1"], PLASSERING)
    assert ut == [
        "++115080=4320.001.01-QLF001",
        "++115080=4320.001.01-QLF002",
        "++115080=4320.001.01-QLF003",
    ]


def test_ulike_kurser_teller_hver_for_seg():
    ut = merk(["Downlight", "Downlight"], ["1", "2"], PLASSERING)
    assert ut == ["++115080=4320.001.01-QLF001", "++115080=4320.001.02-QLF001"]


def test_ingen_duplikater_i_en_stor_merking():
    """K6 melder om komponentforekomster brukt to steder. Den skal ikke ha noe å melde."""
    familier = [n for n, _ in FAMILIER] * 40
    kurser = [str(i % 17) for i in range(len(familier))]
    ut = merk(familier, kurser, PLASSERING)
    assert len(set(ut)) == len(ut)


# --- Listene må komme fra de samme elementene ---


def test_ulik_lengde_stopper_framfor_aa_forskyve():
    """To lister av ulik lengde betyr at noe er feilkoblet i grafen.

    Uten dette ville zip() kuttet den lengste i stillhet, og hvert element
    etter avviket fått kursnummeret til naboen. Det er en feil ingen ser.
    """
    with pytest.raises(ValueError, match="samme rekkefølge"):
        merk(["Downlight", "Downlight"], ["1"], PLASSERING)


# --- Grafen og IFC-injektoren skal ikke kunne drive fra hverandre ---


def test_familietabellen_er_den_samme_som_i_injektoren():
    """verktoy/legg_til_tfm.py utleder de samme kodene fra den andre siden.

    Driver de to fra hverandre, merkes en modell én vei i Revit og en annen vei
    i IFC-en — og forskjellen ville dukket opp som K3- og K5-funn uten
    forklaring.
    """
    sys.path.insert(0, str(Path(__file__).parent.parent / "verktoy"))
    from legg_til_tfm import FAMILIER as INJEKTOR
    from legg_til_tfm import STANDARD as INJEKTOR_STANDARD

    assert dict(FAMILIER) == INJEKTOR
    assert STANDARD == INJEKTOR_STANDARD


def test_rekkefolgen_i_tabellen_bevares():
    """Dict i injektoren, liste her — men oppslaget skjer på prefiks.

    «Electrical Equipment» og «Electrical Fixtures» deler ikke prefiks, så
    rekkefølgen spiller ingen rolle i dag. Testen låser at det fortsatt er
    sant: legges «Electrical» inn som egen nøkkel, ville den kapret begge.
    """
    nøkler = [n for n, _ in FAMILIER]
    for i, a in enumerate(nøkler):
        for b in nøkler[i + 1 :]:
            assert not b.startswith(a), f"«{a}» skygger for «{b}»"


# --- Tallene skal kunne leses ---


def test_statistikken_teller_det_som_avgjor_tilliten():
    familier = ["Downlight", "Ukjent", "Conduit"]
    kurser = ["1", "2", ""]
    tall = statistikk(familier, kurser, merk(familier, kurser, PLASSERING))
    assert tall["elementer"] == 3
    assert tall["ukjent_familie"] == 1
    assert tall["uten_kurs"] == 1
    assert tall["unike_tfm"] == 3


def test_tom_inndata_sier_fra():
    """En tom liste ser nøyaktig ut som en modell der alt allerede er merket."""
    linjer = sammendrag(statistikk([], [], []))
    assert any("Ingen elementer" in ln for ln in linjer)


def test_sammendraget_advarer_om_duplikater():
    tall = statistikk(["a"], ["1"], ["++115080=4390.001.01-QLX001"] * 2)
    assert any("ADVARSEL" in ln for ln in sammendrag(tall))


# --- Det Dynamo sender inn er ikke alltid en streng ---


def test_tekst_haandterer_none():
    """Revit gir null for en parameter som ikke er satt."""
    from tfm_fra_revit import tekst

    assert tekst(None) == ""


def test_tekst_slipper_gjennom_strenger():
    from tfm_fra_revit import tekst

    assert tekst("Downlight") == "Downlight"
    assert tekst("Kurs «6,8»") == "Kurs «6,8»"


def test_tekst_krasjer_ikke_paa_et_objekt():
    """En feilkoblet node kan gi et Revit-objekt framfor et navn.

    Da skal grafen si fra gjennom statistikken, ikke stoppe med en
    AttributeError ingen kan tolke.
    """
    from tfm_fra_revit import tekst

    class Element:
        def __repr__(self):
            return "<Revit.Elements.Family>"

    assert tekst(Element()) == "<Revit.Elements.Family>"


def test_alle_ukjente_leses_som_feilkobling():
    """Den vanligste feilen: IN[0] gir noe annet enn familienavn.

    Uten dette ville sammendraget sagt «2426 familier står ikke i tabellen»,
    som leses som at tabellen er fattig — ikke som at grafen er feilkoblet.
    """
    familier = ["Revit.Elements.Family"] * 3
    kurser = ["1", "2", "3"]
    tall = statistikk(familier, kurser, merk(familier, kurser, PLASSERING))
    linjer = sammendrag(tall)
    assert any("feilkoblet" in ln for ln in linjer)


def test_noen_ukjente_leses_ikke_som_feilkobling():
    familier = ["Downlight", "Ukjent"]
    kurser = ["1", "2"]
    linjer = sammendrag(statistikk(familier, kurser, merk(familier, kurser, PLASSERING)))
    assert not any("feilkoblet" in ln for ln in linjer)
    assert any("står ikke i tabellen" in ln for ln in linjer)
