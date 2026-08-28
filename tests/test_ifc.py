"""Tester for IFC-lesing mot syntetiske modeller (§7)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fixtures.syntetisk import GYLDIG, lag_elektromodell, lag_modell

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.feil import FilFeil
from tfm_sjekk.ifc import les_modell, les_modeller
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import kjor_alle


@pytest.fixture
def modell(tmp_path):
    return lag_modell(
        [
            ("IfcFlowTerminal", GYLDIG),
            ("IfcFlowTerminal", "++11508=3600.001.04-JVZ001"),  # for få siffer
            ("IfcFlowTerminal", None),  # uten pset
        ],
        tmp_path / "test.ifc",
    )


def test_leser_alle_produkter(modell):
    objekter = les_modell(modell)
    assert len(objekter) == 3


def test_henter_tfm_fra_pset(modell):
    objekter = les_modell(modell)
    verdier = {o.tfm_forekomst for o in objekter}
    assert GYLDIG in verdier
    assert None in verdier


def test_fyller_arvekjeden(modell):
    objekt = les_modell(modell)[0]
    assert "IfcDistributionElement" in objekt.ifc_supertyper
    assert "IfcProduct" in objekt.ifc_supertyper


def test_kildefil_settes(modell):
    assert all(o.kildefil == "test.ifc" for o in les_modell(modell))


def test_ende_til_ende_gir_forventede_funn(modell):
    kontekst = Kontekst.bygg(les_modell(modell), Konfigurasjon())
    funn, _ = kjor_alle(kontekst)
    kontroller = {f.kontroll for f in funn}
    assert "K1" in kontroller  # objektet uten pset
    assert "K2" in kontroller  # objektet med feil sifferantall


def test_ifc2x3_leses(tmp_path):
    """§3 krever både IFC 2x3 og IFC4."""
    sti = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "gammel.ifc", schema="IFC2X3")
    objekter = les_modell(sti)
    assert len(objekter) == 1
    assert objekter[0].tfm_forekomst == GYLDIG


def test_federering_slar_sammen_filer(tmp_path):
    a = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "rie.ifc")
    b = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "riv.ifc")

    objekter = les_modeller([a, b], parallelt=False)
    assert len(objekter) == 2
    assert {o.kildefil for o in objekter} == {"rie.ifc", "riv.ifc"}

    # Samme komponentforekomst i to fagmodeller — dette er K6-tilfellet.
    funn, _ = kjor_alle(Kontekst.bygg(objekter, Konfigurasjon()))
    assert any(f.kontroll == "K6" for f in funn)


def test_leser_koblingsgrafen_gjennom_portene(tmp_path):
    """Porten er kanten mellom to objekter (K8b/K8c)."""
    sti = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [
                    {"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010", "kurs": "Kurs 12"}
                ],
            }
        ],
        tmp_path / "elektro.ifc",
    )
    objekter = {o.navn: o for o in les_modell(sti)}

    tavle, lampe = objekter["Fordeling 1"], objekter["Objekt 1.1"]
    assert lampe.global_id in tavle.tilkoblet
    assert tavle.global_id in lampe.tilkoblet
    assert [str(krets) for krets in lampe.kretser] == ["Kurs 12"]


def test_porter_er_ikke_objekter(tmp_path):
    """IfcDistributionPort er en IfcProduct, men skal ikke telles som et
    kontrollert objekt — den bærer ingen TFM og ville forurenset K1."""
    sti = lag_elektromodell(
        [{"navn": "F1", "tfm": None, "objekter": [{"klasse": "IfcLamp", "tfm": None}]}],
        tmp_path / "porter.ifc",
    )
    klasser = {o.ifc_klasse for o in les_modell(sti)}
    assert "IfcDistributionPort" not in klasser
    assert klasser == {"IfcElectricDistributionBoard", "IfcLamp"}


def test_fordelinger_bygges_i_konteksten(tmp_path):
    sti = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [
                    {"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010"},
                    {"klasse": "IfcLamp", "tfm": "++115080=4310.001.13-QLF011"},
                ],
            }
        ],
        tmp_path / "graf.ifc",
    )
    kontekst = Kontekst.bygg(les_modell(sti), Konfigurasjon())
    assert len(kontekst.fordelinger) == 1
    (medlemmer,) = kontekst.fordelinger.values()
    assert len(medlemmer) == 2


def test_posisjon_leses_fra_plasseringen(tmp_path):
    """Posisjonen ender i BCF-kameraet, så den må komme ut av loaderen."""
    sti = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [{"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010"}],
            }
        ],
        tmp_path / "plassert.ifc",
        geometri=True,
    )
    etter_navn = {o.navn: o for o in les_modell(sti)}
    assert etter_navn["Fordeling 1"].posisjon == (0.0, 0.0, 0.0)
    assert etter_navn["Objekt 1.1"].posisjon == (2.0, 0.0, 0.0)


def test_modell_uten_plassering_gir_ingen_posisjon(tmp_path):
    """De tynne testmodellene har ingen plassering, og det skal gå fint."""
    sti = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "tynn.ifc")
    assert les_modell(sti)[0].posisjon is None


def test_visningsmodell_kan_apnes_og_tegnes(tmp_path):
    """Modellen med geometri må ha det en viewer krever.

    Uten prosjekt, enheter og romlig struktur nekter de fleste viewere å
    åpne fila, og uten geometri er det ingenting å velge når et BCF-emne
    peker på et objekt. Da kan ikke BCF-en prøves i praksis.
    """
    import ifcopenshell
    import ifcopenshell.geom

    sti = lag_elektromodell(
        [
            {
                "navn": "Fordeling 1",
                "tfm": "++115080=4310.001.00-QLF001",
                "objekter": [{"klasse": "IfcLamp", "tfm": "++115080=4310.001.12-QLF010"}],
            }
        ],
        tmp_path / "visning.ifc",
        geometri=True,
    )

    fil = ifcopenshell.open(sti)
    assert len(fil.by_type("IfcProject")) == 1
    assert fil.by_type("IfcProject")[0].UnitsInContext is not None
    assert len(fil.by_type("IfcBuildingStorey")) == 1
    assert len(fil.by_type("IfcRelContainedInSpatialStructure")) == 1

    innstillinger = ifcopenshell.geom.settings()
    tegnbare = 0
    for produkt in fil.by_type("IfcProduct"):
        if produkt.Representation is None:
            continue
        # Formobjektet må holdes i en variabel mens hjørnene leses. Skriver
        # man `create_shape(...).geometry.verts` i én kjede, rekker det å bli
        # frigjort, og man får en tom liste i stedet for geometrien.
        form = ifcopenshell.geom.create_shape(innstillinger, produkt)
        if len(form.geometry.verts) > 0:
            tegnbare += 1

    assert tegnbare == 2  # fordelingen og lampa


def test_federering_parallelt_gir_samme_resultat(tmp_path):
    a = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "a.ifc")
    b = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "b.ifc")
    sekvensielt = les_modeller([a, b], parallelt=False)
    parallelt = les_modeller([a, b], parallelt=True)
    assert [o.global_id for o in sekvensielt] == [o.global_id for o in parallelt]


def test_typeegenskaper_leses(tmp_path):
    """TFM på typeobjektet skal leses, i begge skjemaer.

    En Revit-familietype kan bære merkingen som typeparameter, og for
    komponenttypen er det det naturlige stedet: alle forekomstene av en
    familietype ER samme komponenttype.

    Koblingen heter ikke det samme i de to skjemaene — `IsTypedBy` i IFC4, og en
    `IfcRelDefinesByType` inne i `IsDefinedBy` i 2x3 — så testen dekker begge.
    En test på bare det ene ville sagt god dag.

    Uten dette så verktøyet ingenting, og K1 meldte at hvert eneste objekt
    manglet TFM. Rapporten så da ut som en modell uten merking, ikke som et
    verktøy som ikke leste etter.
    """
    import ifcopenshell
    import ifcopenshell.guid as guid

    for schema in ("IFC4", "IFC2X3"):
        f = ifcopenshell.file(schema=schema)
        forekomst = f.create_entity("IfcFlowTerminal", GlobalId=guid.new(), Name="Uten eget pset")
        egenskap = f.create_entity(
            "IfcPropertySingleValue", Name="TFM", NominalValue=f.create_entity("IfcLabel", GYLDIG)
        )
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name="TFM11_Forekomst", HasProperties=[egenskap]
        )
        type_objekt = f.create_entity(
            "IfcFlowTerminalType", GlobalId=guid.new(), Name="Familietype", HasPropertySets=[pset]
        )
        f.create_entity(
            "IfcRelDefinesByType",
            GlobalId=guid.new(),
            RelatedObjects=[forekomst],
            RelatingType=type_objekt,
        )
        sti = tmp_path / f"type-{schema}.ifc"
        f.write(str(sti))

        objekt = next(o for o in les_modell(sti) if o.ifc_klasse == "IfcFlowTerminal")
        assert objekt.tfm_forekomst == GYLDIG, f"{schema}: typeegenskapen ble ikke lest"
        assert objekt.kilder["forekomst"].pset == "TFM11_Forekomst"


def test_modell_med_geometri_har_eierhistorikk_overalt(tmp_path):
    """I IFC 2x3 er OwnerHistory PÅKREVD på IfcRoot.

    IFC4 gjorde den valgfri, og ifcopenshell setter den ikke av seg selv når
    entiteter opprettes for hånd. Resultatet var en fil som var gyldig IFC4 og
    ugyldig 2x3 — 94 av 95 entiteter uten — og Revit avviste den uten å si
    hvorfor. Ingen feilmelding er verre enn en gal en.

    Gjelder bare modellene med geometri: det er de som skal kunne åpnes i en
    viewer eller importeres i Revit.
    """
    import ifcopenshell
    from fixtures.syntetisk import lag_elektromodell

    # Tavleklassen finnes ikke i begge skjemaene: IfcElectricDistributionBoard
    # kom med IFC4, og 2x3 har IfcElectricDistributionPoint.
    tavle = {"IFC4": "IfcElectricDistributionBoard", "IFC2X3": "IfcElectricDistributionPoint"}

    for schema in ("IFC4", "IFC2X3"):
        spek = [
            {
                "navn": "Fordeling 1",
                "klasse": tavle[schema],
                "tfm": "++115080=4310.001.00-QLF100",
                "objekter": [
                    {
                        "klasse": "IfcFlowTerminal",
                        "tfm": "++115080=4310.001.12-QLF101",
                        "kurs": "Kurs 12",
                    }
                ],
            }
        ]
        sti = lag_elektromodell(spek, tmp_path / f"g-{schema}.ifc", schema=schema, geometri=True)
        f = ifcopenshell.open(str(sti))
        uten = [r.is_a() for r in f.by_type("IfcRoot") if r.OwnerHistory is None]
        assert not uten, f"{schema}: mangler OwnerHistory på {sorted(set(uten))}"


def test_geometrimodellen_bruker_coordinationview(tmp_path):
    """ReferenceView er en lese-MVD. Revits importør forventer CoordinationView."""
    from fixtures.syntetisk import lag_elektromodell

    spek = [{"navn": "F", "tfm": "++115080=4310.001.00-QLF100", "objekter": []}]
    sti = lag_elektromodell(spek, tmp_path / "mvd.ifc", geometri=True)
    hode = sti.read_text(encoding="utf-8").splitlines()[2]
    assert "CoordinationView_V2.0" in hode
    assert "ReferenceView" not in hode


# --- En fil som ikke lar seg lese ---


def odelagt(tmp_path, navn: str, innhold: bytes):
    sti = tmp_path / navn
    sti.write_bytes(innhold)
    return sti


def test_tom_fil_sier_at_den_er_tom(tmp_path):
    with pytest.raises(FilFeil, match="tom"):
        les_modell(odelagt(tmp_path, "tom.ifc", b""))


def test_fil_som_ikke_er_ifc_sier_det(tmp_path):
    """«Unable to parse IFC SPF header» fra ifcopenshell er ikke en melding.

    Den peker på en linje i et bibliotek, og den som leser den er en
    BIM-koordinator som skal finne ut om det er modellen eller maskinen som er
    problemet.
    """
    with pytest.raises(FilFeil, match="ikke lese som IFC"):
        les_modell(odelagt(tmp_path, "sopp.ifc", b"dette er ikke IFC i det hele tatt\n"))


def test_zip_med_feil_endelse_far_et_hint(tmp_path):
    """En .ifcZIP som har fått endelsen .ifc er en ekte hendelse."""
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as arkiv:
        arkiv.writestr("modell.ifc", "ISO-10303-21;")

    with pytest.raises(FilFeil, match="zip-arkiv"):
        les_modell(odelagt(tmp_path, "pakket.ifc", buffer.getvalue()))


def test_zip_meldes_ikke_som_avkuttet(tmp_path):
    """Substrengsjekk framfor startswith meldte en .ifcZIP som avkuttet.

    Arkivet bærer teksten «ISO-10303-21;» inne i seg. Meldingen sendte da
    brukeren til å eksportere på nytt framfor til å se på hvilken fil de
    plukket — to helt ulike handlinger.
    """
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as arkiv:
        arkiv.writestr("modell.ifc", "ISO-10303-21;\nENDSEC;\n")

    with pytest.raises(FilFeil) as feil:
        les_modell(odelagt(tmp_path, "pakket.ifc", buffer.getvalue()))
    assert "avkuttet" not in str(feil.value)


def test_avkuttet_fil_leses_ikke_som_en_hel(tmp_path):
    """Det farligste utfallet av de tre, fordi det ikke ser ut som en feil.

    En avbrutt eksport gir en fil som åpner seg fint og inneholder en brøkdel
    av modellen. Verktøyet rapporterte da sant om det det så — «1 av 1 objekter
    i omfanget, alle TFM-verdiene lot seg tolke» — og hver linje var
    misvisende.
    """
    hel = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "hel.ifc")
    bytes_ = hel.read_bytes()
    assert b"END-ISO-10303-21;" in bytes_, "fiksturen skriver ikke avslutningen"

    with pytest.raises(FilFeil, match="avkuttet"):
        les_modell(odelagt(tmp_path, "halv.ifc", bytes_[: len(bytes_) // 2]))


def test_hel_fil_leses_som_for(tmp_path):
    modell = lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "hel.ifc")
    assert len(les_modell(modell)) == 1


def test_modellfeil_overlever_pickle():
    """Unntaket krysser prosessgrensen fra en arbeider i federeringen.

    Standard oppførsel ville kalt `FilFeil(meldingen)` med ett argument ved
    utpakking — altså en TypeError i stedet for feilen den skulle bære. Den
    slags virker sekvensielt og ryker i pool-en.
    """
    import pickle

    original = FilFeil(Path("a") / "b.ifc", "er tom.")
    kopi = pickle.loads(pickle.dumps(original))

    assert isinstance(kopi, FilFeil)
    assert kopi.sti == original.sti
    assert str(kopi) == str(original)


def test_federert_lesing_navngir_fila_som_feilet(tmp_path):
    """TRE filer, ikke to.

    `les_modeller` går sekvensielt under to filer, så en test med færre ville
    aldri nådd prosesspoolen — nettopp den veien feilen skal overleve.
    """
    stier = [
        lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "en.ifc"),
        odelagt(tmp_path, "to.ifc", b"ikke IFC"),
        lag_modell([("IfcFlowTerminal", GYLDIG)], tmp_path / "tre.ifc"),
    ]

    with pytest.raises(FilFeil) as feil:
        les_modeller(stier, Konfigurasjon())

    assert "to.ifc" in str(feil.value)
    assert "en.ifc" not in str(feil.value)
