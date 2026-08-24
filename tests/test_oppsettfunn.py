"""Tester for evnen «oppsettfunn» — hvordan verktøyet finner oppsettet sitt.

Alt dette er usynlig for brukeren med mindre verktøyet sier fra. En fil som
endrer resultatet uten at noen vet at den ble lest, er verre enn ingen fil — og
en sti som peker feil må ikke kunne se ut som et bevisst valg.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tfm_sjekk.config import Konfigurasjon, OppsettFeil, finn_oppsett


def oppsett(mappe: Path, innhold: str = "") -> Path:
    mappe.mkdir(parents=True, exist_ok=True)
    sti = mappe / "tfm-sjekk.toml"
    sti.write_text(innhold, encoding="utf-8")
    return sti


def modell(mappe: Path, navn: str = "rie.ifc") -> Path:
    mappe.mkdir(parents=True, exist_ok=True)
    sti = mappe / navn
    sti.write_text("", encoding="utf-8")
    return sti


# --- Å finne fila ---


def test_oppsettet_ligger_hos_modellen(tmp_path):
    m = modell(tmp_path / "modeller")
    oppsett(tmp_path / "modeller")
    funnet = finn_oppsett([m], tmp_path / "annet")
    assert funnet.parent.name == "modeller"


def test_oppsettet_ligger_i_arbeidskatalogen(tmp_path):
    m = modell(tmp_path / "modeller")
    (tmp_path / "annet").mkdir()
    oppsett(tmp_path / "annet")
    funnet = finn_oppsett([m], tmp_path / "annet")
    assert funnet.parent.name == "annet"


def test_modellens_mappe_har_forrang(tmp_path):
    """Ved dra-og-slipp er arbeidskatalogen exe-ens egen mappe.

    Den har ikke noe med prosjektet å gjøre — samme innsikt som ligger bak at
    rapporten legges hos modellen.
    """
    m = modell(tmp_path / "modeller")
    oppsett(tmp_path / "modeller")
    oppsett(tmp_path / "annet")
    assert finn_oppsett([m], tmp_path / "annet").parent.name == "modeller"


def test_ingen_finnes(tmp_path):
    m = modell(tmp_path / "modeller")
    (tmp_path / "annet").mkdir()
    assert finn_oppsett([m], tmp_path / "annet") is None


def test_uten_modeller_letes_det_i_arbeidskatalogen(tmp_path):
    oppsett(tmp_path / "annet")
    assert finn_oppsett([], tmp_path / "annet") is not None


# --- Stier tolkes relativt til fila ---


def test_relativ_sti_loses_mot_konfigurasjonsfila(tmp_path):
    """Kjørt fra en helt annen mappe skal stien fortsatt peke riktig."""
    (tmp_path / "tabeller").mkdir()
    (tmp_path / "tabeller" / "ns3451.csv").write_text("", encoding="utf-8")
    sti = oppsett(tmp_path, 'systemtabell = "tabeller/ns3451.csv"\n')

    k = Konfigurasjon.les(sti)
    assert k.sti("systemtabell") == (tmp_path / "tabeller" / "ns3451.csv").resolve()


def test_sti_over_konfigurasjonsfila(tmp_path):
    (tmp_path / "modeller").mkdir()
    (tmp_path / "TFM-master.csv").write_text("", encoding="utf-8")
    sti = oppsett(tmp_path / "modeller", 'tfm_master = "../TFM-master.csv"\n')

    k = Konfigurasjon.les(sti)
    assert k.sti("tfm_master") == (tmp_path / "TFM-master.csv").resolve()


def test_absolutt_sti_star_urort(tmp_path):
    absolutt = (tmp_path / "et-annet-sted.csv").resolve()
    sti = oppsett(tmp_path, f'tfm_master = "{absolutt.as_posix()}"\n')
    assert Konfigurasjon.les(sti).sti("tfm_master") == absolutt


def test_uten_fil_er_det_ingen_kilde():
    k = Konfigurasjon()
    assert k.kilde is None
    assert k.sti("tfm_master") is None


def test_kilde_folger_ikke_med_i_serialisering(tmp_path):
    """`kilde` er hvor fila lå, ikke en innstilling.

    Kom den med i utdata, ville et forslag fra «oppsett» skrevet maskinstien
    til den som leste det inn i fila til den neste.
    """
    sti = oppsett(tmp_path, 'tfm_master = "m.csv"\n')
    assert "kilde" not in Konfigurasjon.les(sti).model_dump()


# --- Ikke oppgitt er fortsatt et valg ---


@pytest.mark.parametrize("felt", ["tfm_master", "systemtabell", "komponenttabell"])
def test_ikke_oppgitt_gir_ingen_sti(tmp_path, felt):
    assert Konfigurasjon.les(oppsett(tmp_path)).sti(felt) is None


# --- En ukjent nøkkel skal stoppe kjøringen ---
#
# En forkastet nøkkel betyr at kjøringen brukte andre regler enn den som skrev
# fila ba om, og rapporten ser like ren ut. Det har skjedd: «ifc_klasser»
# skrevet etter «[pset]» leses av TOML som «pset.ifc_klasser», og halve
# konfigurasjonen var borte uten et ord.


def les(mappe: Path, innhold: str) -> Konfigurasjon:
    return Konfigurasjon.les(oppsett(mappe, innhold))


def test_feilstavet_nokkel_stopper(tmp_path):
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, '[elektro]\nforing_systemkode = ["4360"]\n')
    assert "foring_systemkode" in str(e.value)
    assert "elektro" in str(e.value)


def test_feilstavet_seksjon_stopper(tmp_path):
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, '[elektrp]\nforing_systemkoder = ["4360"]\n')
    assert "elektrp" in str(e.value)


def test_gyldig_nokkel_i_feil_seksjon_stopper(tmp_path):
    """Nøyaktig feilen «oppsett» en gang skrev: ifc_klasser hører på toppnivå."""
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, '[pset]\nifc_klasser = ["IfcWall"]\n')
    assert "ifc_klasser" in str(e.value)
    assert "pset" in str(e.value)


def test_riktig_skrevet_fil_leses_som_for(tmp_path):
    c = les(tmp_path, '[elektro]\nforing_systemkoder = ["4360"]\n')
    assert c.elektro.foring_systemkoder == ["4360"]


def test_kontroll_id_er_er_ikke_en_fast_liste(tmp_path):
    """«kontroller» er en ordbok med kontroll-ID som nøkkel."""
    c = les(tmp_path, '[kontroller.K4]\nalvorlighet = "advarsel"\n')
    assert c.kontroller["K4"].alvorlighet.value == "advarsel"


def test_forslaget_kommer_naar_noe_ligner(tmp_path):
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, '[elektro]\nforing_systemkode = ["4360"]\n')
    assert "Mente du «foring_systemkoder»?" in str(e.value)


def test_meldingen_star_stott_uten_forslag(tmp_path):
    """Ligner den ingenting, skal meldingen fortsatt navngi nøkkelen."""
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, "[elektro]\nbanan = 1\n")
    assert "banan" in str(e.value)
    assert "Mente du" not in str(e.value)


def test_meldingen_navngir_seksjonen(tmp_path):
    """«Ukjent nøkkel «type»» er ubrukelig når «type» finnes i to seksjoner."""
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, "[mmi]\ntype = 1\n")
    assert "[mmi]" in str(e.value)


def test_repoets_egen_oppsettfil_leses():
    """Den er både dokumentasjon og oppsett, og brukes i CI og i demomappa.

    Den hadde «ifc_klasser» inne i [pset] fram til dette kravet kom. Verdiene
    var like standardverdiene, så ingenting oppførte seg galt — men fila
    dokumenterte en nøkkel på feil sted, og den som kopierte den og endret lista
    ville fått endringen forkastet i stillhet.
    """
    sti = Path(__file__).parent.parent / "tfm-sjekk.toml"
    oppsett = Konfigurasjon.les(sti)
    assert oppsett.ifc_klasser, "ifc_klasser havnet ikke på toppnivå"


def test_et_forslag_som_peker_galt_kommer_ikke(tmp_path):
    """«krev_plasering» hører hjemme i [grammatikk], ikke i [elektro].

    Med difflibs standardterskel traff den «krets_klasser» — et forslag som
    sender brukeren i feil retning. Ekte skrivefeil ligger på 0.96 og oppover;
    dette treffet lå på 0.67.
    """
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, "[elektro]\nkrev_plasering = false\n")
    assert "krev_plasering" in str(e.value)
    assert "krets_klasser" not in str(e.value)


# --- En nøkkel som bare står feil, skal få vite hvor den hører hjemme ---
#
# Seksjonsinndelingen i TOML er usynlig når man skriver: en nøkkel under feil
# overskrift ser ut som en nøkkel på riktig sted. Det er slik «ifc_klasser»
# havnet inne i [pset] og ble lest som «pset.ifc_klasser».


def test_toppnivanokkel_i_en_seksjon_peker_hjem(tmp_path):
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, '[pset]\nifc_klasser = ["IfcWall"]\n')
    assert "toppnivå" in str(e.value)


def test_nokkel_fra_en_annen_seksjon_peker_hjem(tmp_path):
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, "[elektro]\nkrev_plassering = false\n")
    assert "[grammatikk]" in str(e.value)


def test_enda_en_seksjon(tmp_path):
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, '[master]\ngyldige_verdier = ["300"]\n')
    assert "[mmi]" in str(e.value)


def test_nokkel_som_ikke_finnes_noe_sted_oppforer_seg_som_for(tmp_path):
    """Låser at endringen ikke tar med seg noe den ikke skal."""
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, "[elektro]\nbanan = 1\n")
    tekst = str(e.value)
    assert "banan" in tekst
    assert "hører hjemme" not in tekst


def test_a_peke_hjem_gar_foran_a_foresla_noe_som_ligner(tmp_path):
    """«krev_plassering» ligner ingenting i [elektro] etter at terskelen ble
    hevet, men skal uansett aldri få en gjetning når svaret finnes."""
    with pytest.raises(OppsettFeil) as e:
        les(tmp_path, "[elektro]\nkrev_plassering = false\n")
    assert "Mente du" not in str(e.value)


def test_kartet_kan_ikke_bli_utdatert():
    """Hvert felt i hver modell skal finnes i oppslaget.

    Legger noen til en nøkkel uten at oppslaget følger med, feiler denne. Det
    er hele poenget med å bygge kartet av model_fields framfor av en liste.
    """
    from pydantic import BaseModel

    from tfm_sjekk.config import _hvor_horer_nokkelen_hjemme

    for felt in Konfigurasjon.model_fields:
        assert "toppnivå" in _hvor_horer_nokkelen_hjemme(felt), felt
    for seksjon, spec in Konfigurasjon.model_fields.items():
        annotasjon = spec.annotation
        if isinstance(annotasjon, type) and issubclass(annotasjon, BaseModel):
            for felt in annotasjon.model_fields:
                assert f"[{seksjon}]" in _hvor_horer_nokkelen_hjemme(felt), f"{seksjon}.{felt}"


def test_flere_steder_nevnes_alle():
    """Finnes samme navn to steder, skal begge nevnes.

    Å peke på det første i en vilkårlig rekkefølge er en gjetning forkledd som
    et svar. Tilfellet finnes ikke i modellene i dag, så det prøves på
    formuleringen direkte.
    """
    from tfm_sjekk.config import _som_sted

    assert _som_sted(["toppnivå"]) == "på toppnivå"
    assert _som_sted(["[mmi]"]) == "i [mmi]"
    assert _som_sted(["[mmi]", "[elektro]"]) == "i [mmi] eller i [elektro]"


def test_bom_i_oppsettet_gir_en_melding_ikke_en_tilbakesporing(tmp_path):
    """Notisblokk og PowerShell skriver BOM. tomllib leser den som et tegn.

    Fila ser helt riktig ut i editoren, og verktøyet svarte med en Python-
    tilbakesporing. Oppsettet er nettopp fila brukeren redigerer selv — og med
    en fast rute i den, redigeres den i hvert prosjekt.
    """
    sti = tmp_path / "tfm-sjekk.toml"
    sti.write_bytes(b"\xef\xbb\xbf" + b'ifc_klasser = ["IfcFlowTerminal"]\n')

    assert Konfigurasjon.les(sti).ifc_klasser == ["IfcFlowTerminal"]


def test_ugyldig_toml_sier_hvilken_fil_og_hvor(tmp_path):
    sti = tmp_path / "tfm-sjekk.toml"
    sti.write_text("dette er ikke toml\n", encoding="utf-8")

    with pytest.raises(OppsettFeil, match=r"tfm-sjekk[.]toml"):
        Konfigurasjon.les(sti)
