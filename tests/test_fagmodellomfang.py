"""Tester for evnen «fagmodellomfang» — omfang per fagmodell, ikke per kjøring.

Bakgrunnen er en ekte federering: Snowdon Towers med RIE, ARK, RIB og tomt ga
675 K1-funn på armaturer og servanter arkitekten hadde tegnet inn, mot 177 ekte
funn i elektromodellen. Rapporten var teknisk korrekt og ubrukelig som
arbeidsliste.

Det som gjør endringen liten, er at bare K1 og D1 følger omfanget. K3–K8 leser
`med_tfm()`, som aldri har filtrert på klasse — og det er derfor K6 fortsatt
finner duplikater på tvers av en unntatt fil. Testene her passer på begge sider
av det.
"""

from __future__ import annotations

import pytest

from tfm_sjekk.config import FagmodellOppsett, Konfigurasjon, OppsettFeil

ARK = "Snowdon Towers Sample Electrical-Snowdon Towers Sample Architectural.ifc"
RIE = "Snowdon Towers Sample Electrical.ifc"


def oppsett(**fagmodell: list[str]) -> Konfigurasjon:
    return Konfigurasjon(
        fagmodell={m: FagmodellOppsett(ifc_klasser=k) for m, k in fagmodell.items()}
    )


# --- Oppslaget ---


def test_uten_seksjon_gjelder_toppnivaaet():
    """Uten den nye nøkkelen skal alt være som før — bit for bit."""
    k = Konfigurasjon()

    assert k.omfang_for(ARK) == k.ifc_klasser
    assert not k.er_unntatt(ARK)


def test_monsteret_treffer_paa_filnavn():
    k = oppsett(**{"*Architectural*": []})

    assert k.omfang_for(ARK) == []
    assert k.omfang_for(RIE) == k.ifc_klasser


def test_det_mest_spesifikke_monsteret_vinner():
    """«*» og «*Architectural*» treffer begge ARK. Det lengste skal gjelde.

    Rekkefølgen i en dict er innsettingsrekkefølgen, og den er et tilfelle av
    hvordan noen skrev TOML-en. Å velge det første ville gjort resultatet
    avhengig av linjerekkefølge uten at noe sa fra.
    """
    k = oppsett(**{"*": ["IfcWall"], "*Architectural*": []})

    assert k.omfang_for(ARK) == []
    assert k.omfang_for(RIE) == ["IfcWall"]


def test_to_like_spesifikke_monstre_stopper():
    """Det finnes ikke noe riktig svar, og verktøyet skal ikke late som.

    Eksemplet er ikke oppdiktet. Revit navngir lenkede eksporter etter verten,
    så ARK-fila heter «…Electrical-…Architectural.ifc» — den inneholder BEGGE
    fagnavnene. Et prosjekt som skriver «*Elec*» for RIE og «*Arch*» for ARK
    treffer da samme fil med begge, og de er like lange.
    """
    k = oppsett(**{"*Arch*": [], "*Elec*": ["IfcWall"]})

    with pytest.raises(OppsettFeil, match="Flere like spesifikke"):
        k.omfang_for(ARK)


def test_meldingen_navngir_begge_monstrene():
    k = oppsett(**{"*aaaa*": [], "*bbbb*": ["IfcWall"]})

    with pytest.raises(OppsettFeil) as feil:
        k.omfang_for("x-aaaa-bbbb.ifc")

    assert "*aaaa*" in str(feil.value)
    assert "*bbbb*" in str(feil.value)


# --- Unntaket ---


def test_tom_liste_er_et_bevisst_unntak():
    k = oppsett(**{"*Architectural*": []})

    assert k.er_unntatt(ARK)
    assert not k.er_unntatt(RIE)


def test_en_fil_uten_treff_er_ikke_unntatt():
    """Tomt omfang ved et uhell er ikke det samme som et unntak.

    D1 kan ikke se forskjellen på tallene — begge gir null i omfanget — så
    dette skillet er det eneste som finnes.
    """
    k = oppsett(**{"*Architectural*": []})

    assert not k.er_unntatt("Uteglemt.ifc")


def test_et_monster_med_klasser_unntar_ikke():
    k = oppsett(**{"*Architectural*": ["IfcWall"]})

    assert not k.er_unntatt(ARK)
    assert k.omfang_for(ARK) == ["IfcWall"]


# --- Konteksten ---


def kontekst(tmp_path, filer: dict[str, list], config: Konfigurasjon):
    """Én Kontekst av flere fagmodeller, bygget slik CLI-en gjør det."""
    from fixtures.syntetisk import lag_modell

    from tfm_sjekk.ifc import les_modeller
    from tfm_sjekk.kontekst import Kontekst

    stier = [lag_modell(objekter, tmp_path / navn) for navn, objekter in filer.items()]
    return Kontekst.bygg(les_modeller(stier, config, parallelt=False), config)


def test_to_filer_med_ulikt_omfang_i_samme_kjoring(tmp_path):
    k = kontekst(
        tmp_path,
        {"ARK.ifc": [("IfcFlowTerminal", None)] * 3, "RIE.ifc": [("IfcFlowTerminal", None)] * 2},
        oppsett(**{"*ARK*": []}),
    )

    assert k.dekning()["ARK.ifc"] == (0, 3)
    assert k.dekning()["RIE.ifc"] == (2, 2)
    assert k.unntatte_filer() == ["ARK.ifc"]


def test_unntaket_rorer_ikke_med_tfm_og_objekter(tmp_path):
    """Dette er det som holder K6 i live på tvers av en unntatt fil.

    `med_tfm()` har aldri filtrert på klasse, og K3–K8 leser den. Rydder noen i
    det ved å la unntaket gjelde alt, forsvinner duplikatkontrollen på tvers —
    som er hele grunnen til å federere.
    """
    from fixtures.syntetisk import GYLDIG

    k = kontekst(
        tmp_path,
        {"ARK.ifc": [("IfcFlowTerminal", GYLDIG)], "RIE.ifc": [("IfcFlowTerminal", GYLDIG)]},
        oppsett(**{"*ARK*": []}),
    )

    assert len(k.objekter) == 2
    assert len(k.med_tfm()) == 2
    assert [o.kildefil for o in k.relevante_objekter()] == ["RIE.ifc"]


# --- D1 og kontrollene ---


def kjor_alt(tmp_path, filer, config):
    from tfm_sjekk.kontroller import kjor_alle

    funn, _ = kjor_alle(kontekst(tmp_path, filer, config))
    return funn


def test_unntatt_fil_gir_ingen_d1(tmp_path):
    funn = kjor_alt(
        tmp_path,
        {"ARK.ifc": [("IfcWall", None)] * 3, "RIE.ifc": [("IfcFlowTerminal", None)]},
        oppsett(**{"*ARK*": []}),
    )

    assert not [f for f in funn if f.kontroll == "D1"]


def test_uteglemt_fil_gir_d1_som_for(tmp_path):
    """Fila er ikke nevnt i oppsettet, og omfanget ble tomt av seg selv."""
    funn = kjor_alt(
        tmp_path,
        {"ARK.ifc": [("IfcWall", None)] * 3, "RIE.ifc": [("IfcFlowTerminal", None)]},
        Konfigurasjon(),
    )

    d1 = [f for f in funn if f.kontroll == "D1"]
    assert [f.kildefil for f in d1] == ["ARK.ifc"]


def test_k1_gir_ingen_funn_i_en_unntatt_fil(tmp_path):
    """De 675 armaturene i arkitektmodellen — det som utløste hele endringen."""
    funn = kjor_alt(
        tmp_path,
        {"ARK.ifc": [("IfcFlowTerminal", None)] * 5, "RIE.ifc": [("IfcFlowTerminal", None)]},
        oppsett(**{"*ARK*": []}),
    )

    k1 = [f for f in funn if f.kontroll == "K1"]
    assert [f.kildefil for f in k1] == ["RIE.ifc"]


def test_k6_finner_duplikat_paa_tvers_av_en_unntatt_fil(tmp_path):
    """Kravet hele endringen finnes for.

    Å unnta en fagmodell betyr at den ikke måles mot merkekravene, ikke at den
    er usynlig for resten. Et duplikat mellom ARK og RIE er nettopp det
    federeringen skal finne.
    """
    from fixtures.syntetisk import GYLDIG

    funn = kjor_alt(
        tmp_path,
        {"ARK.ifc": [("IfcFlowTerminal", GYLDIG)], "RIE.ifc": [("IfcFlowTerminal", GYLDIG)]},
        oppsett(**{"*ARK*": []}),
    )

    k6 = [f for f in funn if f.kontroll == "K6"]
    assert len(k6) == 2
    assert {f.kildefil for f in k6} == {"ARK.ifc", "RIE.ifc"}
    assert "ARK.ifc" in k6[0].melding and "RIE.ifc" in k6[0].melding


def test_k8_paa_en_unntatt_fil_er_uendret(tmp_path):
    """Omfanget styrer ikke `med_tfm()`, og det skal feile hvis noen endrer det.

    K8 melder elektroobjekter uten kursnummer. Et slikt objekt i en unntatt fil
    meldes fortsatt: unntaket sier at fila ikke måles mot merkeKRAVENE, ikke at
    innholdet er usynlig. Ryker denne, har noen latt unntaket gjelde alt — og da
    er K6 på tvers borte uten at noe annet sier fra.
    """
    uten_kurs = "++115080=4310.001.00-QLF001"

    funn = kjor_alt(
        tmp_path,
        {"ARK.ifc": [("IfcFlowTerminal", uten_kurs)], "RIE.ifc": [("IfcFlowTerminal", None)]},
        oppsett(**{"*ARK*": []}),
    )

    k8 = [f for f in funn if f.kontroll == "K8" and f.kildefil == "ARK.ifc"]
    assert k8, "K8 skal fortsatt se objektet i en unntatt fil"
