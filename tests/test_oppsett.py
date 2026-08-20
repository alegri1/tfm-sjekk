"""Tester for konfigurasjonsforslaget (evnen «oppsettforslag»).

Bygger `Kontekst` i minnet, uten IFC-filer. Det er hele poenget med at
utledningen er en ren funksjon: den kan prøves på hvert enkelt tilfelle uten å
måtte konstruere en modell som tilfeldigvis får verdiuttrekket til å oppføre seg
som ønsket.
"""

from __future__ import annotations

import tomllib

import pytest

from tfm_sjekk.config import Grammatikk, Konfigurasjon, PsetOppsett
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.modell import IfcObjekt, Kilde, Verdikilde
from tfm_sjekk.oppsett import Verditype, til_toml, utled

GYLDIG = "++115080=3600.001.04-JVZ001%JVZ.001.008"


def objekt(
    global_id: str,
    *,
    klasse: str = "IfcFlowTerminal",
    supertyper: tuple[str, ...] = ("IfcProduct",),
    tfm: str | None = GYLDIG,
    kilde: Verdikilde | None = None,
    verditype: str = "forekomst",
    kildefil: str = "rie.ifc",
) -> IfcObjekt:
    return IfcObjekt(
        global_id=global_id,
        ifc_klasse=klasse,
        ifc_supertyper=list(supertyper),
        kildefil=kildefil,
        tfm_forekomst=tfm,
        kilder={verditype: kilde} if kilde else {},
    )


def kontekst(objekter: list[IfcObjekt], config: Konfigurasjon | None = None) -> Kontekst:
    return Kontekst.bygg(objekter, config or Konfigurasjon())


def konfigurert(pset: str = "TFM11_Forekomst", felt: str = "TFM") -> Verdikilde:
    return Verdikilde(kilde=Kilde.KONFIGURERT, pset=pset, felt=felt)


# --- Forslaget utledes av observasjoner, ikke av standardverdier ---


def test_modell_som_folger_oppsettet_gir_ingen_psettforslag():
    f = utled(kontekst([objekt("a", kilde=konfigurert())]))
    assert f.psett == {}
    assert f.feltnavn == {}
    assert not f.har_noe()


def test_bare_avviket_skrives():
    """Grammatikk, MMI-skala og resten skal ikke stå i fila."""
    f = utled(
        kontekst(
            [objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"))]
        )
    )
    ut = til_toml(f)
    assert "grammatikk" not in ut
    assert "mmi" not in ut.split("[pset]")[0]
    assert "plassering_siffer" not in ut


# --- Hvordan verdien ble funnet avgjør hva som foreslås ---


def test_gjenkjent_felt_i_ukjent_pset_foreslar_psettet():
    f = utled(
        kontekst(
            [objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"))]
        )
    )
    assert [x.verdi for x in f.psett[Verditype.FOREKOMST]] == ["Data"]
    assert Verditype.FOREKOMST not in f.feltnavn


def test_gjettet_felt_i_konfigurert_pset_foreslar_feltnavnet():
    f = utled(
        kontekst(
            [
                objekt(
                    "a",
                    kilde=Verdikilde(kilde=Kilde.GJETTET, pset="TFM11_Forekomst", felt="Merking"),
                )
            ]
        )
    )
    assert [x.verdi for x in f.feltnavn[Verditype.FOREKOMST]] == ["Merking"]
    assert Verditype.FOREKOMST not in f.psett


def test_verdien_la_der_den_skulle():
    f = utled(kontekst([objekt("a", kilde=konfigurert())]))
    assert not f.psett and not f.feltnavn


def test_alle_tre_verditypene_kan_foreslas():
    f = utled(
        kontekst(
            [
                objekt(
                    "a",
                    verditype="type",
                    kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Typedata", felt="TFMType"),
                ),
                objekt(
                    "b",
                    verditype="mmi",
                    kilde=Verdikilde(kilde=Kilde.GJETTET, pset="MMI", felt="Modenhet"),
                ),
            ]
        )
    )
    assert [x.verdi for x in f.psett[Verditype.TYPE]] == ["Typedata"]
    assert [x.verdi for x in f.feltnavn[Verditype.MMI]] == ["Modenhet"]


# --- En forkastet verdi skal aldri bli konfigurasjon ---


def test_forkastet_verdi_gir_ikke_forslag():
    """Å foreslå feltet ville gjort en riktig avvisning til varig konfigurasjon."""
    f = utled(
        kontekst(
            [
                objekt(
                    "a",
                    tfm=None,
                    kilde=Verdikilde(
                        kilde=Kilde.FORKASTET,
                        pset="TFM11_Forekomst",
                        felt="Fabrikat",
                        forkastet_verdi="Systemair",
                    ),
                )
            ]
        )
    )
    assert not f.har_noe()
    assert "Fabrikat" not in til_toml(f)


# --- En klasse foreslås bare når objektene er merket ---


def test_merket_proxy_utenfor_omfanget_foreslas():
    f = utled(kontekst([objekt("a", klasse="IfcBuildingElementProxy", kilde=konfigurert())]))
    assert [x.verdi for x in f.klasser] == ["IfcBuildingElementProxy"]


def test_umerkede_klasser_holdes_utenfor():
    objekter = [objekt("a", klasse="IfcBuildingElementProxy", kilde=konfigurert())]
    objekter += [objekt(f"v{i}", klasse="IfcWall", tfm=None) for i in range(200)]
    f = utled(kontekst(objekter))
    assert [x.verdi for x in f.klasser] == ["IfcBuildingElementProxy"]


def test_klasser_allerede_i_omfanget_foreslas_ikke():
    f = utled(kontekst([objekt("a", kilde=konfigurert())]))
    assert f.klasser == []


def test_klasse_treffes_via_arvekjeden():
    """IfcAirTerminal er i omfanget fordi IfcFlowTerminal er det."""
    f = utled(
        kontekst(
            [
                objekt(
                    "a",
                    klasse="IfcAirTerminal",
                    supertyper=("IfcFlowTerminal", "IfcProduct"),
                    kilde=konfigurert(),
                )
            ]
        )
    )
    assert f.klasser == []


# --- Hvert forslag skal bære sitt eget belegg ---


def test_belegget_star_i_fila():
    objekter = [
        objekt(f"a{i}", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"))
        for i in range(840)
    ]
    ut = til_toml(utled(kontekst(objekter)))
    assert "840 objekter" in ut
    assert "gjenkjent feltnavn" in ut


def test_svakt_belegg_er_synlig_som_svakt():
    objekter = [
        objekt(
            f"a{i}",
            kilde=Verdikilde(kilde=Kilde.GJETTET, pset="TFM11_Forekomst", felt="Merking"),
        )
        for i in range(2)
    ]
    ut = til_toml(utled(kontekst(objekter)))
    assert "2 objekter" in ut
    assert "gjettet feltnavn" in ut


def test_ett_objekt_boyes_i_entall():
    ut = til_toml(
        utled(
            kontekst(
                [objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"))]
            )
        )
    )
    assert "1 objekt," in ut
    assert "1 objekter" not in ut


# --- Konfigurerte verdier skal beholde sin forrang ---


def test_konfigurerte_star_forst_og_i_uendret_rekkefolge():
    config = Konfigurasjon(pset=PsetOppsett(forekomst=["Forst", "Andre"]))
    f = utled(
        kontekst(
            [objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"))],
            config,
        )
    )
    lest = tomllib.loads(til_toml(f, config))
    assert lest["pset"]["forekomst"] == ["Forst", "Andre", "Data"]


def test_fagmodeller_som_er_uenige_gir_begge_med_sterkeste_forst():
    objekter = [
        objekt(
            f"a{i}",
            kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Sjelden", felt="TFM"),
            kildefil="rie.ifc",
        )
        for i in range(2)
    ] + [
        objekt(
            f"b{i}",
            kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Vanlig", felt="TFM"),
            kildefil="riv.ifc",
        )
        for i in range(9)
    ]
    f = utled(kontekst(objekter))
    assert [x.verdi for x in f.psett[Verditype.FOREKOMST]] == ["Vanlig", "Sjelden"]


def test_like_mange_gir_stabil_rekkefolge():
    objekter = [
        objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Bravo", felt="TFM")),
        objekt("b", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Alfa", felt="TFM")),
    ]
    f = utled(kontekst(objekter))
    assert [x.verdi for x in f.psett[Verditype.FOREKOMST]] == ["Alfa", "Bravo"]


# --- Forslaget skal kunne leses tilbake av verktøyet ---


def test_utdata_er_gyldig_toml_som_konfigurasjonen_godtar(tmp_path):
    objekter = [
        objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM")),
        objekt("b", klasse="IfcBuildingElementProxy", kilde=konfigurert()),
    ]
    sti = tmp_path / "forslag.toml"
    sti.write_text(til_toml(utled(kontekst(objekter))), encoding="utf-8")

    config = Konfigurasjon.les(sti)
    assert "Data" in config.pset.forekomst
    assert "IfcBuildingElementProxy" in config.ifc_klasser


def test_ifc_klasser_havner_ikke_inne_i_pset_tabellen():
    """Toppnivånøkkel etter «[pset]» leses som «pset.ifc_klasser».

    Fila ville vært gyldig TOML og gyldig konfigurasjon, pydantic ville droppet
    den ukjente nøkkelen i stillhet, og hele klasseforslaget ville forsvunnet.
    """
    objekter = [
        objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM")),
        objekt("b", klasse="IfcBuildingElementProxy", kilde=konfigurert()),
    ]
    lest = tomllib.loads(til_toml(utled(kontekst(objekter))))
    assert "ifc_klasser" in lest
    assert "ifc_klasser" not in lest["pset"]


def test_forslaget_gjor_usikre_verdier_sikre():
    """Rundturen: forslaget skal flytte kildene til KONFIGURERT."""
    config = Konfigurasjon()
    f = utled(
        kontekst(
            [objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"))],
            config,
        )
    )
    ny = Konfigurasjon.model_validate(tomllib.loads(til_toml(f, config)))
    assert "Data" in ny.pset.forekomst


def test_forslaget_er_stabilt():
    """Andre kjøring med eget forslag som konfigurasjon skal ikke foreslå noe."""
    config = Konfigurasjon()
    objekter = [
        objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM")),
        objekt("b", klasse="IfcBuildingElementProxy", kilde=konfigurert()),
    ]
    forste = utled(kontekst(objekter, config))
    ny_config = Konfigurasjon.model_validate(tomllib.loads(til_toml(forste, config)))

    # Samme observasjoner, men nå er «Data» konfigurert, så kildene ville vært
    # KONFIGURERT ved en ny innlesing. Det etterlignes her.
    etter = [
        objekt("a", kilde=konfigurert(pset="Data")),
        objekt("b", klasse="IfcBuildingElementProxy", kilde=konfigurert()),
    ]
    assert not utled(kontekst(etter, ny_config)).har_noe()


# --- Et tomt forslag skal si hva tomheten betyr ---


def test_alt_la_der_det_skulle():
    f = utled(kontekst([objekt("a", kilde=konfigurert())]))
    assert f.fant_grunnlag()
    assert "verdiene lå der oppsettet sa" in til_toml(f)


def test_ingenting_a_bygge_pa():
    f = utled(kontekst([objekt(f"a{i}", tfm=None) for i in range(412)]))
    assert not f.fant_grunnlag()
    ut = til_toml(f)
    assert "ingen av objektene hadde TFM-verdi" in ut
    assert "412 objekter" in ut


def test_tomt_forslag_gir_ingen_tomme_tabeller():
    ut = til_toml(utled(kontekst([objekt("a", kilde=konfigurert())])))
    assert "[pset]" not in ut
    assert "ifc_klasser" not in ut
    assert tomllib.loads(ut) == {}


# --- Skriveren ---


@pytest.mark.parametrize(
    "verdi",
    ['Pset"med"hermetegn', "Pset\\med\\skraastrek"],
)
def test_skriveren_escaper_saerskilte_tegn(verdi):
    f = utled(
        kontekst(
            [objekt("a", kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset=verdi, felt="TFM"))]
        )
    )
    assert verdi in tomllib.loads(til_toml(f))["pset"]["forekomst"]


# --- Grensen: begge dimensjonene ukjente samtidig ---


def test_verdier_i_ukjent_pset_og_ukjent_felt_er_usynlige(tmp_path):
    """Blindsonen. Låser dagens oppførsel, som er en bevisst grense.

    Verdiuttrekket har tre strategier, og alle trenger minst ett kjent
    holdepunkt: konfigurert sett og felt, konfigurert feltnavn hvor som helst,
    eller ukjent felt i et konfigurert sett. Ligger verdien i et ukonfigurert
    sett *og* et ukonfigurert felt, er den usynlig — og da har `oppsett` heller
    ingenting å foreslå, enda modellen er merket helt korrekt.

    Å lukke hullet ville bety å skanne hvert felt i hvert egenskapssett og
    stole på `ligner_tfm_id` alene. Det er en større beslutning enn den
    utledningen tar i dag. Endres den, er det denne testen som skal si fra.
    """
    from fixtures.syntetisk import lag_modell_i_blindsonen

    from tfm_sjekk.ifc import les_modell

    modell = lag_modell_i_blindsonen(tmp_path / "blindsone.ifc", antall=5)
    k = Kontekst.bygg(les_modell(modell), Konfigurasjon())

    assert all(o.tfm_forekomst is None for o in k.objekter)
    assert all(o.kilder == {} for o in k.objekter)

    f = utled(k)
    assert not f.har_noe()
    assert not f.fant_grunnlag()
    assert f.lest == 5

    # Og tomheten skal si hvilken av de to slagene den er.
    ut = til_toml(f)
    assert "ingen av objektene hadde TFM-verdi" in ut
    assert "verdiene lå der oppsettet sa" not in ut


# --- Grammatikkforslag ---


def grammatikk_kontekst(verdier: list[str], config: Konfigurasjon | None = None) -> Kontekst:
    return Kontekst.bygg(
        [objekt(f"g{i}", tfm=v) for i, v in enumerate(verdier)],
        config or Konfigurasjon(),
    )


def test_tidligfase_uten_plassering_foreslas():
    f = utled(grammatikk_kontekst(["=3600.001.04-JVZ001", "=4310.001.12-QLF001"]))
    assert [(g.innstilling, g.verdi) for g in f.grammatikk] == [("krev_plassering", False)]
    assert f.har_noe()


def test_blandede_feil_gir_ingen_anvisning():
    """En innstilling som løser noen av feilene peker på merkefeil, ikke fase."""
    f = utled(
        grammatikk_kontekst(
            [
                "=3600.001.04-JVZ001",  # mangler plassering
                "++115080=36000.001.04-JVZ001",  # systemkoden har fem siffer
            ]
        )
    )
    assert f.grammatikk == []


def test_innstilling_som_allerede_er_i_bruk_foreslas_ikke():
    config = Konfigurasjon(grammatikk=Grammatikk(krev_plassering=False))
    f = utled(grammatikk_kontekst(["=3600.001.04-JVZ001"], config))
    assert f.grammatikk == []
    assert not f.har_noe()


def test_avvikende_sifferantall_foreslas_ikke():
    """Å endre et sifferantall sier hva standarden er, ikke hvilken fase vi er i."""
    f = utled(grammatikk_kontekst(["++1150800=3600.001.04-JVZ001"] * 3))
    assert f.grammatikk == []


def test_to_kandidater_kan_sla_til_samtidig():
    config = Konfigurasjon(grammatikk=Grammatikk(krev_komponenttype=True))
    f = utled(grammatikk_kontekst(["=3600.001.04-JVZ001"], config))
    assert {g.innstilling for g in f.grammatikk} == {"krev_plassering", "krev_komponenttype"}


def test_begge_tallene_star_i_fila():
    verdier = ["=3600.001.04-JVZ001"] * 3 + ["++115080=3600.001.04-JVZ002"] * 2
    ut = til_toml(utled(grammatikk_kontekst(verdier)))
    assert "3 verdier feiler" in ut
    assert "2 verdier parser" in ut


def test_forslag_med_bare_grammatikk_er_ikke_tomt():
    ut = til_toml(utled(grammatikk_kontekst(["=3600.001.04-JVZ001"])))
    assert "verdiene lå der oppsettet sa" not in ut
    assert "krev_plassering = false" in ut


def test_sammensatt_forslag_overlever_en_tur_gjennom_konfigurasjonen():
    """Alle tre delene skal være i kraft — ikke bare stå i fila.

    En toppnivånøkkel skrevet etter en tabelloverskrift havner inne i tabellen.
    Fila er da fortsatt gyldig TOML og gyldig konfigurasjon, og verdien
    forsvinner uten et ord. Prøven er derfor på utfallet, ikke på rekkefølgen.
    """
    objekter = [
        objekt("a", tfm="=3600.001.04-JVZ001"),
        objekt(
            "b",
            tfm="=3600.001.04-JVZ002",
            kilde=Verdikilde(kilde=Kilde.GJENKJENT_FELT, pset="Data", felt="TFM"),
        ),
        objekt("c", klasse="IfcBuildingElementProxy", tfm="=3600.001.04-JVZ003"),
    ]
    forslag = utled(Kontekst.bygg(objekter, Konfigurasjon()))
    assert forslag.grammatikk and forslag.psett and forslag.klasser

    lest = Konfigurasjon.model_validate(tomllib.loads(til_toml(forslag)))
    assert lest.grammatikk.krev_plassering is False
    assert "Data" in lest.pset.forekomst
    assert "IfcBuildingElementProxy" in lest.ifc_klasser


def test_grammatikken_tas_i_bruk_og_forslaget_blir_tomt():
    verdier = ["=3600.001.04-JVZ001", "=4310.001.12-QLF001"]
    forste = utled(grammatikk_kontekst(verdier))
    ny_config = Konfigurasjon.model_validate(tomllib.loads(til_toml(forste)))

    etter = Kontekst.bygg([objekt(f"g{i}", tfm=v) for i, v in enumerate(verdier)], ny_config)
    assert len(etter.parsede) == 2
    assert not utled(etter).har_noe()


def test_det_minste_settet_vinner():
    """Løser én innstilling alt, skal ikke den andre bli med på lasset."""
    config = Konfigurasjon(grammatikk=Grammatikk(krev_komponenttype=True))
    # Verdiene har komponenttype, men mangler plassering. Da holder én bryter.
    f = utled(grammatikk_kontekst(["=3600.001.04-JVZ001%JVZ.001.008"] * 3, config))
    assert [g.innstilling for g in f.grammatikk] == ["krev_plassering"]
