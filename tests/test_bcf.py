"""Tester for BCF 2.1-eksport (§5).

BCF er formatet som avgjør om verktøyet blir tatt i bruk, og strukturen er
det ingen leser før en viewer avviser fila. Testene her sjekker derfor både
at innholdet er der og at zip-en er byte-identisk mellom to kjøringer — det
siste er forutsetningen for golden files (§7).
"""

from __future__ import annotations

import math
import struct
import xml.etree.ElementTree as ET
import zipfile
import zlib

import pytest
from conftest import uten_ansi
from fixtures.syntetisk import GYLDIG, lag_modell
from typer.testing import CliRunner

from tfm_sjekk.cli import app
from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.rapport import normaliser_tidsstempel, skriv_bcf

OPPRETTET = "2026-01-01T12:00:00Z"


def funn_med_objekt() -> Funn:
    return Funn(
        kontroll="K6",
        alvorlighet=Alvorlighet.FEIL,
        melding="Komponentforekomsten «++115080=4310.001.12-QLF001» er brukt på 2 objekter.",
        global_id="1hqA2bC3dE4fG5hI6jK7lM",
        ifc_klasse="IfcFlowTerminal",
        kildefil="demo-rie.ifc",
        verdi="++115080=4310.001.12-QLF001",
    )


def funn_uten_objekt() -> Funn:
    return Funn(
        kontroll="K7",
        alvorlighet=Alvorlighet.INFO,
        melding="1 system i TFM-mastera er ikke brukt i modellen: 3600.002.04.",
    )


def les(sti, navn: str) -> ET.Element:
    with zipfile.ZipFile(sti) as arkiv:
        return ET.fromstring(arkiv.read(navn))


def navn_i(sti) -> list[str]:
    with zipfile.ZipFile(sti) as arkiv:
        return sorted(arkiv.namelist())


def les_forste(sti, endelse: str) -> ET.Element:
    return les(sti, next(n for n in navn_i(sti) if n.endswith(endelse)))


def test_skriver_gyldig_zip_med_versjonsfil(tmp_path):
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    assert zipfile.is_zipfile(sti)

    versjon = les(sti, "bcf.version")
    assert versjon.get("VersionId") == "2.1"


def test_ett_emne_per_funn(tmp_path):
    sti = skriv_bcf([funn_med_objekt(), funn_uten_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    markuper = [n for n in navn_i(sti) if n.endswith("markup.bcf")]
    assert len(markuper) == 2


def test_markup_har_det_skjemaet_krever(tmp_path):
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    markup = les_forste(sti, "markup.bcf")

    topic = markup.find("Topic")
    assert topic is not None
    assert topic.get("Guid")
    assert topic.findtext("Title").startswith("K6:")
    assert topic.findtext("CreationDate") == OPPRETTET
    assert topic.findtext("Priority") == "feil"
    assert topic.findtext("Labels") == "K6"  # det viewerne filtrerer på
    assert "QLF001" in topic.findtext("Description")

    assert markup.find("Comment") is not None
    assert markup.findtext("Header/File/Filename") == "demo-rie.ifc"


def test_viewpoint_peker_pa_objektet(tmp_path):
    """Uten dette er saken ikke klikkbar, og formatet mister hensikten."""
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    bcfv = les_forste(sti, ".bcfv")

    komponent = bcfv.find("Components/Selection/Component")
    assert komponent is not None
    assert komponent.get("IfcGuid") == "1hqA2bC3dE4fG5hI6jK7lM"

    # Markup må referere fila for at viewer-en skal finne den.
    markup = les_forste(sti, "markup.bcf")
    referert = markup.findtext("Viewpoints/Viewpoint")
    assert referert and any(n.endswith(referert) for n in navn_i(sti)), (
        f"markup peker på {referert}, som ikke finnes i arkivet"
    )


def test_viewpointet_har_et_kamera_som_ser_mot_objektet(tmp_path):
    """Uten kamera svarer viewer-en «this issue has no viewpoint to zoom to».

    Et utvalg alene er ikke en synsvinkel. Kameraet er valgfritt i skjemaet,
    så dette er ikke noe en validering fanger — det viste seg først i en ekte
    viewer.
    """
    f = funn_med_objekt()
    f.posisjon = (6.0, 0.0, 0.0)
    sti = skriv_bcf([f], tmp_path / "funn.bcfzip", OPPRETTET)
    kamera = les_forste(sti, ".bcfv").find("PerspectiveCamera")
    assert kamera is not None

    def vektor(navn):
        node = kamera.find(navn)
        return tuple(float(node.find(akse).text) for akse in "XYZ")

    øye, retning, opp = (
        vektor("CameraViewPoint"),
        vektor("CameraDirection"),
        vektor("CameraUpVector"),
    )

    assert øye[2] > 0, "kameraet står under bakken"

    # Retningen skal peke fra øyet mot objektet.
    mot_målet = [m - o for m, o in zip(f.posisjon, øye, strict=True)]
    lengde = math.sqrt(sum(k * k for k in mot_målet))
    for forventet, faktisk in zip(mot_målet, retning, strict=True):
        assert abs(forventet / lengde - faktisk) < 1e-6

    # Opp-vektoren må stå vinkelrett på retningen, ellers vipper bildet.
    assert abs(sum(a * b for a, b in zip(retning, opp, strict=True))) < 1e-6
    assert opp[2] > 0


def test_uten_posisjon_skrives_viewpointet_uten_kamera(tmp_path):
    """En modell uten plassering skal gi et utvalg, ikke en krasj."""
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    bcfv = les_forste(sti, ".bcfv")
    assert bcfv.find("PerspectiveCamera") is None
    assert bcfv.find("Components/Selection/Component") is not None


def test_viewpointet_har_snapshot(tmp_path):
    """BIMcollab regner viewpointet som fraværende uten et bilde.

    Snapshot er valgfritt i skjemaet, men alle buildingSMARTs egne
    konformitetsfiler har ett.
    """
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)

    bilder = [n for n in navn_i(sti) if n.endswith(".png")]
    assert len(bilder) == 1

    markup = les_forste(sti, "markup.bcf")
    referert = markup.findtext("Viewpoints/Snapshot")
    assert referert and bilder[0].endswith(referert), "markup peker på feil filnavn"


def test_snapshotet_er_et_gyldig_png(tmp_path):
    """Skrevet uten bildebibliotek, så blokkene og CRC-ene sjekkes her."""
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    with zipfile.ZipFile(sti) as arkiv:
        data = arkiv.read(next(n for n in navn_i(sti) if n.endswith(".png")))

    assert data[:8] == b"\x89PNG\r\n\x1a\n"

    blokker, i = [], 8
    while i < len(data):
        lengde = struct.unpack(">I", data[i : i + 4])[0]
        merke, innhold = data[i + 4 : i + 8], data[i + 8 : i + 8 + lengde]
        crc = struct.unpack(">I", data[i + 8 + lengde : i + 12 + lengde])[0]
        assert crc == zlib.crc32(merke + innhold) & 0xFFFFFFFF, f"CRC-feil i {merke!r}"
        blokker.append(merke)
        i += 12 + lengde

    assert blokker == [b"IHDR", b"IDAT", b"IEND"]
    bredde, høyde, dybde, fargetype = struct.unpack(">IIBB", data[16:26])
    assert (bredde, høyde, dybde, fargetype) == (320, 180, 8, 2)


def test_funn_uten_objekt_far_ikke_viewpoint(tmp_path):
    """Samlefunnene fra K7 og K8c peker på modellen, ikke på noe å zoome til."""
    sti = skriv_bcf([funn_uten_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    assert not [n for n in navn_i(sti) if n.endswith(".bcfv")]

    markup = les_forste(sti, "markup.bcf")
    assert markup.find("Viewpoints") is None
    assert markup.find("Header") is None


def test_modellnivafunn_er_merket_som_sadan(tmp_path):
    """«Ingenting å zoome til» skal være noe man kan filtrere på, ikke noe
    som ser ut som en feil i verktøyet."""
    sti = skriv_bcf([funn_uten_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    etiketter = [e.text for e in les_forste(sti, "markup.bcf").findall("Topic/Labels")]
    assert etiketter == ["K7", "modellnivå"]


def test_objektfunn_far_ikke_modellnivaetiketten(tmp_path):
    sti = skriv_bcf([funn_med_objekt()], tmp_path / "funn.bcfzip", OPPRETTET)
    etiketter = [e.text for e in les_forste(sti, "markup.bcf").findall("Topic/Labels")]
    assert etiketter == ["K6"]


def test_samme_funn_gir_byte_identisk_fil(tmp_path):
    """Golden files (§7) forutsetter det, og en diff uten reelle endringer
    er verdiløs i en leveranseprosess."""
    funn = [funn_med_objekt(), funn_uten_objekt()]
    a = skriv_bcf(funn, tmp_path / "a.bcfzip", OPPRETTET)
    b = skriv_bcf(list(reversed(funn)), tmp_path / "b.bcfzip", OPPRETTET)
    assert a.read_bytes() == b.read_bytes()


def test_emne_guid_folger_innholdet(tmp_path):
    """Samme funn skal beholde identiteten sin mellom kjøringer, slik at et
    emne som allerede er importert i en viewer ikke dukker opp på nytt."""
    a = skriv_bcf([funn_med_objekt()], tmp_path / "a.bcfzip", OPPRETTET)
    b = skriv_bcf([funn_med_objekt()], tmp_path / "b.bcfzip", "2027-06-06T06:06:06Z")
    assert navn_i(a) == navn_i(b)


def test_identiske_funn_kolliderer_ikke(tmp_path):
    sti = skriv_bcf([funn_uten_objekt(), funn_uten_objekt()], tmp_path / "f.bcfzip", OPPRETTET)
    assert len([n for n in navn_i(sti) if n.endswith("markup.bcf")]) == 2


def test_tom_rapport_er_fortsatt_en_gyldig_bcf(tmp_path):
    sti = skriv_bcf([], tmp_path / "tom.bcfzip", OPPRETTET)
    assert navn_i(sti) == ["bcf.version"]


def test_tidsstempel_regnes_om_til_utc():
    """Samme øyeblikk skal gi samme fil uansett hvilken sone det ble skrevet i."""
    assert normaliser_tidsstempel("2026-01-01T13:00:00+01:00") == OPPRETTET
    assert normaliser_tidsstempel("2026-01-01T12:00:00Z") == OPPRETTET


def test_tidsstempel_uten_sone_tolkes_som_utc():
    """Lokal tid ville gitt ulik fil på to maskiner — da er poenget borte."""
    assert normaliser_tidsstempel("2026-01-01 12:00:00") == OPPRETTET
    assert normaliser_tidsstempel("2026-01-01") == "2026-01-01T00:00:00Z"


def test_ugyldig_tidsstempel_avvises():
    with pytest.raises(ValueError, match="ISO 8601"):
        normaliser_tidsstempel("i går")


def test_cli_med_opprettet_gir_identisk_fil(tmp_path):
    """Lovnaden flagget gir: to kjøringer, samme byte."""
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "modell.ifc")
    runner = CliRunner()

    filer = []
    for katalog in ("a", "b"):
        resultat = runner.invoke(
            app,
            [
                "sjekk",
                str(modell),
                "--ut",
                str(tmp_path / katalog),
                "--opprettet",
                OPPRETTET,
            ],
        )
        assert resultat.exit_code == 0, resultat.output
        filer.append((tmp_path / katalog / "funn.bcfzip").read_bytes())

    assert filer[0] == filer[1]


def test_viewpointene_peker_pa_objekter_som_finnes_i_modellen(tmp_path):
    """Koblingen skjemaet ikke kan si noe om.

    Et viewpoint velger et objekt med IfcGuid. At XML-en validerer betyr bare
    at attributtet er der — ikke at GUID-en finnes i modellen. Er den feil,
    åpnes emnet i viewer-en uten å velge noe, og BCF-en har mistet hensikten
    sin uten å se ødelagt ut.
    """
    import ifcopenshell
    from fixtures.syntetisk import lag_elektromodell

    from tfm_sjekk.config import Konfigurasjon
    from tfm_sjekk.ifc import les_modell
    from tfm_sjekk.kontekst import Kontekst
    from tfm_sjekk.kontroller import kjor_alle

    modell = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [
                    {"klasse": "IfcLamp", "tfm": "++115080=4320.001.12-QLF010"},  # K8b
                    {"klasse": "IfcLamp", "tfm": None},  # K1
                ],
            }
        ],
        tmp_path / "modell.ifc",
    )
    funn, _ = kjor_alle(Kontekst.bygg(les_modell(modell), Konfigurasjon()))
    sti = skriv_bcf(funn, tmp_path / "funn.bcfzip", OPPRETTET)

    i_modellen = {p.GlobalId for p in ifcopenshell.open(modell).by_type("IfcProduct")}

    guider = []
    with zipfile.ZipFile(sti) as arkiv:
        for navn in arkiv.namelist():
            if navn.endswith(".bcfv"):
                rot = ET.fromstring(arkiv.read(navn))
                guider += [k.get("IfcGuid") for k in rot.iter("Component")]

    assert guider, "ingen viewpoints å sjekke"
    assert all(g in i_modellen for g in guider), [g for g in guider if g not in i_modellen]


def test_cli_avviser_ugyldig_opprettet(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "modell.ifc")
    resultat = CliRunner().invoke(
        app, ["sjekk", str(modell), "--ut", str(tmp_path / "ut"), "--opprettet", "i går"]
    )
    assert resultat.exit_code != 0
    assert "--opprettet" in uten_ansi(resultat.output)
