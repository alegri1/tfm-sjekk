from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.modell import IfcObjekt, Krets
from tfm_sjekk.tabeller import Kodetabell, TfmMaster

GYLDIG = "++115080=3600.001.04-JVZ001%JVZ.001.008"

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def uten_ansi(tekst: str) -> str:
    """Fjerner fargekoder fra CLI-utdata før den sammenlignes.

    Rich slår på farger når den kjenner igjen et CI-miljø, og den styler
    opsjonsnavn — med escape-sekvenser *inne i* tokenet. «--opprettet» er da
    ikke lenger en sammenhengende streng, og en assert som leter etter den
    feiler i CI selv om alt er som det skal. Lokalt, uten farger, passerer den.
    """
    return ANSI.sub("", tekst)


@pytest.fixture
def config() -> Konfigurasjon:
    return Konfigurasjon()


@pytest.fixture
def systemtabell() -> Kodetabell:
    """Fiktiv tabell — ikke normativ. Se §8.

    «2300» har barn (2310/2320) og skal derfor utløse K4.
    """
    return Kodetabell(
        navn="fiktiv systemtabell",
        koder={
            "3600": "Fiktivt luftbehandlingssystem",
            "2300": "Fiktivt overordnet system",
            "2310": "Fiktivt underordnet system",
            "2320": "Fiktivt underordnet system 2",
            "4300": "Fiktivt elkraftsystem",
        },
    )


@pytest.fixture
def komponenttabell() -> Kodetabell:
    return Kodetabell(navn="fiktiv komponenttabell", koder={"JVZ": "Fiktiv vifte", "QLF": "Fiktiv"})


@pytest.fixture
def master() -> TfmMaster:
    """Fiktiv TFM-master som akkurat dekker GYLDIG — verken mer eller mindre.

    At den er nøyaktig dekkende er poenget: da gir en modell som bare bruker
    GYLDIG hverken funn i retning modell → master eller master → modell.
    """
    return TfmMaster(
        kilde="FIKTIV-tfm-master.csv",
        systemer={"3600.001.04"},
        komponenttyper={"JVZ.001.008"},
    )


def objekt(
    tfm: str | None = GYLDIG,
    global_id: str = "0001",
    klasse: str = "IfcFlowTerminal",
    kildefil: str = "test.ifc",
    navn: str | None = None,
    tilkoblet: list[str] | None = None,
    kretser: list[str] | None = None,
    mmi: str | None = None,
) -> IfcObjekt:
    """`kretser` oppgis som navn; GlobalId-en er navnet, siden identiteten
    bare brukes til å skille kurser fra hverandre (K8c)."""
    return IfcObjekt(
        global_id=global_id,
        ifc_klasse=klasse,
        ifc_supertyper=["IfcDistributionFlowElement", "IfcDistributionElement", "IfcProduct"],
        kildefil=kildefil,
        navn=navn,
        tfm_forekomst=tfm,
        mmi=mmi,
        tilkoblet=tilkoblet or [],
        kretser=[Krets(global_id=navn_, navn=navn_) for navn_ in kretser or []],
    )
