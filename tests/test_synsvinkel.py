"""Tester for evnen «synsvinkel» — hva et BCF-emne lover om det å finne objektet.

Et utvalg alene er ikke nok. En viewer gjenoppretter en synsvinkel, og uten
kamera svarer den at emnet ikke har noe å zoome til. Med et kamera i feil enhet
er det verre: da flytter den seg dit den blir bedt om.

Det skjedde. En Revit-eksport i fot ga kamera 969 kilometer fra objektet, og
modellen forsvant ut av bildet uten at noe sa hvorfor. Ingen fikstur hadde en
annen enhet enn meter, så antakelsen var sann overalt vi prøvde.
"""

from __future__ import annotations

import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fixtures.syntetisk import FOT, METER, MILLIMETER, lag_modell_med_enhet

from tfm_sjekk.ifc.loader import les_modell
from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.rapport import skriv_bcf

FOT_PER_METER = 1 / 0.3048


def modell(enhet, punkt) -> Path:
    return lag_modell_med_enhet(Path(tempfile.mkdtemp()) / "m.ifc", enhet, punkt)


def kamera(objekt) -> tuple[float, float, float]:
    """Kamerapunktet slik det står i BCF-en, lest tilbake ut av fila."""
    funn = [Funn.for_objekt("K2", Alvorlighet.FEIL, "syntaks", objekt)]
    sti = Path(tempfile.mkdtemp()) / "funn.bcfzip"
    skriv_bcf(funn, sti, opprettet="2026-01-01T12:00:00Z")
    with zipfile.ZipFile(sti) as z:
        navn = next(n for n in z.namelist() if n.endswith(".bcfv"))
        rot = ET.fromstring(z.read(navn).decode("utf-8"))
    p = rot.find(".//CameraViewPoint")
    return (float(p.find("X").text), float(p.find("Y").text), float(p.find("Z").text))


def avstand(a, b) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True)) ** 0.5


# --- Kameraet skal stå i den enheten formatet krever ---


def test_meter_gir_objektets_koordinater():
    o = les_modell(modell(METER, (100.0, 200.0, 3.0)))[0]
    assert o.posisjon is not None
    assert o.posisjon[0] == 100.0


def test_fot_regnes_om_til_meter():
    """Samme fysiske punkt, uttrykt i fot. 100 meter er 328.084 fot."""
    o = les_modell(
        modell(FOT, (100.0 * FOT_PER_METER, 200.0 * FOT_PER_METER, 3.0 * FOT_PER_METER))
    )[0]
    assert o.posisjon is not None
    assert abs(o.posisjon[0] - 100.0) < 0.001, f"fikk {o.posisjon[0]}, ventet 100 meter"


def test_millimeter_regnes_om_til_meter():
    """Den vanligste norske modellen. Der har feilen vært mildere og like sann."""
    o = les_modell(modell(MILLIMETER, (100_000.0, 200_000.0, 3_000.0)))[0]
    assert o.posisjon is not None
    assert abs(o.posisjon[0] - 100.0) < 0.001


def test_samme_objekt_i_to_enheter_gir_samme_kamera():
    """Prøven som betyr noe: det fysiske objektet står på samme sted."""
    i_meter = les_modell(modell(METER, (100.0, 200.0, 3.0)))[0]
    i_fot = les_modell(
        modell(FOT, (100.0 * FOT_PER_METER, 200.0 * FOT_PER_METER, 3.0 * FOT_PER_METER))
    )[0]
    assert avstand(kamera(i_meter), kamera(i_fot)) < 0.01


# --- Kameraet skal stå i nærheten av objektet ---


def test_kameraet_star_noen_titalls_meter_fra_objektet():
    """969 kilometer var tallet før. Grensen her er romslig og likevel avgjørende.

    Sammenligningen går mot et FASTSATT punkt i meter, ikke mot `o.posisjon`.
    Med posisjonen som fasit ville testen vært tautologisk: kameraet regnes ut
    av den samme verdien, så avstanden stemmer uansett hvilken enhet begge er
    i. Den varianten passerte med feilen på plass.
    """
    fysisk = (100.0, 200.0, 3.0)  # meter, uansett hva modellen er tegnet i
    for enhet, punkt in (
        (METER, fysisk),
        (FOT, tuple(v * FOT_PER_METER for v in fysisk)),
        (MILLIMETER, tuple(v * 1000.0 for v in fysisk)),
    ):
        o = les_modell(modell(enhet, punkt))[0]
        d = avstand(kamera(o), fysisk)
        # Grensen er romslig med vilje: den skal fange en enhetsfeil, ikke
        # låse en synsvinkel. Avstanden er 4,1 m i dag, justert etter å ha
        # sett på en ekte modell i en viewer.
        assert 1.0 < d < 50.0, f"{enhet[0]}: kameraet står {d:,.0f} m fra objektet"
        assert abs(d - 4.1) < 0.1, f"{enhet[0]}: avstanden er {d:.1f} m, ventet 4,1"


# --- Et emne uten kjent posisjon skal fortsatt kunne åpnes ---


def test_funn_uten_posisjon_gir_emne_uten_kamera():
    """Et emne som sier «ingenting å zoome til» er ærlig. Et som peker feil er ikke det."""
    funn = [Funn(kontroll="K7", alvorlighet=Alvorlighet.INFO, melding="ikke modellert")]
    sti = Path(tempfile.mkdtemp()) / "funn.bcfzip"
    skriv_bcf(funn, sti, opprettet="2026-01-01T12:00:00Z")
    with zipfile.ZipFile(sti) as z:
        assert not [n for n in z.namelist() if n.endswith(".bcfv")]


def test_bcf_er_fortsatt_reproduserbar():
    """Samme funn og samme --opprettet skal gi byte-identisk fil."""
    o = les_modell(modell(FOT, (328.0, 656.0, 9.8)))[0]
    funn = [Funn.for_objekt("K2", Alvorlighet.FEIL, "syntaks", o)]
    filer = []
    for _ in range(2):
        sti = Path(tempfile.mkdtemp()) / "funn.bcfzip"
        skriv_bcf(funn, sti, opprettet="2026-01-01T12:00:00Z")
        filer.append(sti.read_bytes())
    assert filer[0] == filer[1]


def test_bcf_py_kjenner_ingen_enheter():
    """Omregningen hører hjemme i loaderen. Ser rapportmodulen etter enheter,
    har en IFC-detalj lekket ut i konsumentene."""
    kilde = (Path(__file__).parent.parent / "src/tfm_sjekk/rapport/bcf.py").read_text(
        encoding="utf-8"
    )
    kode = "\n".join(ln for ln in kilde.splitlines() if not ln.strip().startswith("#"))
    for ord_ in ("UnitAssignment", "LENGTHUNIT", "IfcSIUnit", "ConversionFactor"):
        assert ord_ not in kode, f"bcf.py nevner {ord_}"


def test_kameraavstanden_er_dokumentert_som_meter():
    """Kommentaren tok forbehold — «modellens enhet (normalt meter)» — og det
    forbeholdet var selve feilen. Låser at det ikke sniker seg inn igjen."""
    kilde = (Path(__file__).parent.parent / "src/tfm_sjekk/rapport/bcf.py").read_text(
        encoding="utf-8"
    )
    rundt = re.search(r"((?:#.*\n)+)KAMERAAVSTAND", kilde)
    assert rundt, "fant ingen kommentar over KAMERAAVSTAND"
    # Bare definisjonslinja. Resten av blokka forklarer hvorfor forbeholdet er
    # borte, og siterer det — en test som forbød ordet ville forbudt
    # forklaringen.
    forste = rundt.group(1).splitlines()[0]
    assert "i meter" in forste, forste
    assert "normalt" not in forste, forste
