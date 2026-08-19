"""Syntetiske IFC-modeller for testing (§7).

«Generer minimale modeller programmatisk med IfcOpenShell — ett objekt med
korrekt TFM, ett med feil sifferantall, ett uten pset.»

Disse er små nok til å ligge i repoet, og de inneholder ingen prosjektdata.
"""

from __future__ import annotations

from pathlib import Path

import ifcopenshell
import ifcopenshell.guid as guid
import ifcopenshell.template

GYLDIG = "++115080=3600.001.04-JVZ001%JVZ.001.008"


def lag_modell(
    objekter: list[tuple[str, str | None]],
    sti: Path,
    schema: str = "IFC4",
    pset_navn: str = "TFM11_Forekomst",
    egenskapsnavn: str = "TFM",
) -> Path:
    """Skriver en minimal IFC-fil.

    `objekter` er (ifc_klasse, tfm_verdi). tfm_verdi=None gir et objekt helt
    uten egenskapssett — tilfellet K1 skal fange.
    """
    f = ifcopenshell.file(schema=schema)

    for klasse, tfm in objekter:
        element = f.create_entity(klasse, GlobalId=guid.new(), Name=f"{klasse}-{tfm or 'utenTFM'}")
        if tfm is None:
            continue
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name=egenskapsnavn,
            NominalValue=f.create_entity("IfcLabel", tfm),
        )
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name=pset_navn, HasProperties=[egenskap]
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )

    sti.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(sti))
    return sti


def lag_modell_pa_avveie(sti: Path, schema: str = "IFC4") -> Path:
    """Skriver en modell der TFM-verdiene ligger utenfor standardoppsettet.

    De tre tilfellene `tfm-sjekk oppsett` finnes for, ett objekt hver:

    1. Riktig feltnavn (`TFM`) i et egenskapssett ingen har konfigurert (`Data`)
       — verdiuttrekket finner den, men bare gjennom et gjenkjent feltnavn.
    2. Ukjent feltnavn (`Merking`) i det konfigurerte egenskapssettet — en
       gjetning, godtatt fordi verdien er gjenkjennelig som en TFM-ID.
    3. En merket `IfcBuildingElementProxy`, altså utstyr eksportert i en klasse
       som ligger utenfor omfanget.

    I tillegg et objekt med et fabrikatnavn i det konfigurerte egenskapssettet.
    Det skal forkastes, og forkastelsen skal ikke bli til et forslag: å foreslå
    feltet ville gjort en riktig avvisning til varig konfigurasjon.
    """
    f = ifcopenshell.file(schema=schema)

    def lag(klasse: str, navn: str, pset_navn: str, felt: str, verdi: str):
        element = f.create_entity(klasse, GlobalId=guid.new(), Name=navn)
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name=felt,
            NominalValue=f.create_entity("IfcLabel", verdi),
        )
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name=pset_navn, HasProperties=[egenskap]
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )
        return element

    lag("IfcFlowTerminal", "Riktig felt, ukjent pset", "Data", "TFM", GYLDIG)
    lag(
        "IfcFlowTerminal",
        "Ukjent felt, riktig pset",
        "TFM11_Forekomst",
        "Merking",
        "++115080=3600.001.04-JVZ002%JVZ.001.008",
    )
    lag(
        "IfcBuildingElementProxy",
        "Merket proxy",
        "TFM11_Forekomst",
        "TFM",
        "++115080=3600.001.04-JVZ003%JVZ.001.008",
    )
    lag("IfcFlowTerminal", "Fabrikat i TFM-settet", "TFM11_Forekomst", "Fabrikat", "Systemair")

    sti.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(sti))
    return sti


def lag_modell_i_blindsonen(sti: Path, schema: str = "IFC4", antall: int = 40) -> Path:
    """Skriver en modell verktøyet ikke ser TFM-verdiene i i det hele tatt.

    Verdiene er velformede TFM-ID-er, men de ligger i et egenskapssett ingen har
    konfigurert *og* i et felt ingen har konfigurert. Verdiuttrekket har tre
    strategier, og alle trenger minst ett kjent holdepunkt: konfigurert sett og
    felt, konfigurert feltnavn hvor som helst, eller ukjent felt i et konfigurert
    sett. Ingen av dem leter etter en TFM-lignende verdi hvor som helst.

    Utfallet er at «tfm-sjekk oppsett» ikke kan foreslå noe, og at «tfm-sjekk
    sjekk» melder at hvert eneste objekt mangler TFM. Modellen er merket helt
    korrekt; det er verktøyet som ikke finner fram.

    Fila finnes for å gjøre den grensen synlig og prøvbar. Lukkes den en dag,
    er det denne modellen som skal begynne å gi forslag.
    """
    f = ifcopenshell.file(schema=schema)

    for i in range(antall):
        element = f.create_entity("IfcFlowTerminal", GlobalId=guid.new(), Name=f"Terminal {i + 1}")
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name="Anleggskode",
            NominalValue=f.create_entity(
                "IfcLabel", f"++115080=3600.001.04-JVZ{i + 1:03d}%JVZ.001.008"
            ),
        )
        pset = f.create_entity(
            "IfcPropertySet",
            GlobalId=guid.new(),
            Name="AnleggsData",
            HasProperties=[egenskap],
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )

    sti.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(sti))
    return sti


def _punkt(f, x: float = 0.0, y: float = 0.0, z: float = 0.0):
    return f.create_entity("IfcCartesianPoint", Coordinates=(x, y, z))


def _plassering(f, x: float = 0.0, y: float = 0.0, z: float = 0.0, forelder=None):
    akse = f.create_entity("IfcAxis2Placement3D", Location=_punkt(f, x, y, z))
    return f.create_entity("IfcLocalPlacement", PlacementRelTo=forelder, RelativePlacement=akse)


def _romlig_struktur(f) -> dict:
    """Prosjekt → tomt → bygg → etasje, slik en viewer forventer det.

    Uten denne kjeden nekter de fleste viewere å åpne fila i det hele tatt:
    et objekt som ikke ligger i noen etasje finnes ikke i modelltreet, og da
    er det heller ikke noe å velge når BCF-en peker på det.
    """
    prosjekt = f.by_type("IfcProject")[0]
    kontekst = prosjekt.RepresentationContexts[0]

    # Egen underkontekst for «Body». Det er den viewerne ser etter når de
    # skal tegne noe; den overordnede Model-konteksten er bare rammen.
    kropp = f.create_entity(
        "IfcGeometricRepresentationSubContext",
        ContextIdentifier="Body",
        ContextType="Model",
        ParentContext=kontekst,
        TargetView="MODEL_VIEW",
    )

    rot = _plassering(f)
    tomt = f.create_entity(
        "IfcSite",
        GlobalId=guid.new(),
        Name="FIKTIV tomt",
        ObjectPlacement=rot,
        CompositionType="ELEMENT",
    )
    bygg = f.create_entity(
        "IfcBuilding",
        GlobalId=guid.new(),
        Name="FIKTIVT bygg 115080",
        ObjectPlacement=_plassering(f, forelder=rot),
        CompositionType="ELEMENT",
    )
    etasje = f.create_entity(
        "IfcBuildingStorey",
        GlobalId=guid.new(),
        Name="Plan 1",
        ObjectPlacement=_plassering(f, forelder=bygg.ObjectPlacement),
        CompositionType="ELEMENT",
    )

    for forelder, barn in ((prosjekt, tomt), (tomt, bygg), (bygg, etasje)):
        f.create_entity(
            "IfcRelAggregates",
            GlobalId=guid.new(),
            RelatingObject=forelder,
            RelatedObjects=[barn],
        )

    return {"kropp": kropp, "etasje": etasje, "innhold": []}


def _gi_kropp(f, rom: dict, element, x: float) -> None:
    """Gir elementet en boks å vises som, og plasserer det i etasjen."""
    profil = f.create_entity(
        "IfcRectangleProfileDef",
        ProfileType="AREA",
        Position=f.create_entity(
            "IfcAxis2Placement2D",
            Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0)),
        ),
        XDim=0.4,
        YDim=0.4,
    )
    boks = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profil,
        Position=f.create_entity("IfcAxis2Placement3D", Location=_punkt(f)),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=0.6,
    )
    element.ObjectPlacement = _plassering(f, x=x, forelder=rom["etasje"].ObjectPlacement)
    element.Representation = f.create_entity(
        "IfcProductDefinitionShape",
        Representations=[
            f.create_entity(
                "IfcShapeRepresentation",
                ContextOfItems=rom["kropp"],
                RepresentationIdentifier="Body",
                RepresentationType="SweptSolid",
                Items=[boks],
            )
        ],
    )
    rom["innhold"].append(element)


def lag_elektromodell(
    fordelinger: list[dict],
    sti: Path,
    schema: str = "IFC4",
    pset_navn: str = "TFM11_Forekomst",
    egenskapsnavn: str = "TFM",
    geometri: bool = False,
) -> Path:
    """Skriver en modell med fordelinger, tilkoblede objekter og kurser (K8b/K8c).

    Hver fordeling er en dict::

        {"navn": "Fordeling 1", "tfm": "++115080=4310.001.00-QLF001",
         "klasse": "IfcElectricDistributionBoard", "mmi": "300",
         "objekter": [{"klasse": "IfcLamp", "tfm": "...", "kurs": "Kurs 12",
                       "mmi": "300"}]}

    Objektene kobles til fordelingen slik en ekte eksport gjør det: hver ende
    har en `IfcDistributionPort` festet med `IfcRelNests`, og portene knyttes
    sammen med `IfcRelConnectsPorts`. `kurs` grupperer objektet i en
    `IfcDistributionCircuit` med det navnet.

    `geometri=True` gir i tillegg prosjekt, enheter, romlig struktur og en
    boks per objekt — alt en viewer trenger for å åpne fila og faktisk vise
    noe. Kontrollene bryr seg ikke om noe av det, så testene bruker
    standardverdien: en modell uten geometri er raskere å lage og like god
    til å teste `Kontekst` med. Det er BCF-en som trenger den tunge varianten,
    fordi et viewpoint uten en modell å peke i ikke kan prøves.
    """
    if geometri:
        f = ifcopenshell.template.create(
            schema_identifier=schema,
            project_name="FIKTIVT demoprosjekt 115080",
            # Fast tidsstempel: fila skal kunne sammenlignes mellom kjoringer.
            timestring="2026-01-01T12:00:00",
        )
        rom = _romlig_struktur(f)
    else:
        f = ifcopenshell.file(schema=schema)
        rom = None

    kretser: dict[str, list] = {}
    plassnummer = [0]

    def sett_pset(element, sett_navn: str, felt: str, verdi: str) -> None:
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name=felt,
            NominalValue=f.create_entity("IfcLabel", verdi),
        )
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=guid.new(), Name=sett_navn, HasProperties=[egenskap]
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=guid.new(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )

    def lag(
        klasse: str,
        navn: str,
        tfm: str | None,
        mmi: str | None = None,
        typefelt: str | None = None,
    ):
        element = f.create_entity(klasse, GlobalId=guid.new(), Name=navn)
        if tfm is not None:
            sett_pset(element, pset_navn, egenskapsnavn, tfm)
        if mmi is not None:
            sett_pset(element, "MMI", "MMI", mmi)
        if typefelt is not None:
            sett_pset(element, "TFM11_Type", "TFMType", typefelt)
        if rom is not None:
            # Objektene settes på rekke med to meters mellomrom. Ingen
            # arkitektur i det — poenget er at de skal være til å skille fra
            # hverandre når et BCF-emne velger ett av dem.
            _gi_kropp(f, rom, element, x=2.0 * plassnummer[0])
            plassnummer[0] += 1
        return element

    def port_for(element):
        port = f.create_entity("IfcDistributionPort", GlobalId=guid.new())
        f.create_entity(
            "IfcRelNests", GlobalId=guid.new(), RelatingObject=element, RelatedObjects=[port]
        )
        return port

    for nummer, spesifikasjon in enumerate(fordelinger, start=1):
        tavle = lag(
            spesifikasjon.get("klasse", "IfcElectricDistributionBoard"),
            spesifikasjon.get("navn", f"Fordeling {nummer}"),
            spesifikasjon.get("tfm"),
            spesifikasjon.get("mmi"),
            spesifikasjon.get("typefelt"),
        )
        for indeks, objekt_spek in enumerate(spesifikasjon.get("objekter", []), start=1):
            objekt = lag(
                objekt_spek.get("klasse", "IfcFlowTerminal"),
                objekt_spek.get("navn", f"Objekt {nummer}.{indeks}"),
                objekt_spek.get("tfm"),
                objekt_spek.get("mmi"),
                objekt_spek.get("typefelt"),
            )
            f.create_entity(
                "IfcRelConnectsPorts",
                GlobalId=guid.new(),
                RelatingPort=port_for(tavle),
                RelatedPort=port_for(objekt),
            )

            kurs = objekt_spek.get("kurs")
            if kurs is None:
                continue
            if kurs not in kretser:
                krets = f.create_entity("IfcDistributionCircuit", GlobalId=guid.new(), Name=kurs)
                kretser[kurs] = [krets, []]
            kretser[kurs][1].append(objekt)

    for krets, objekter in kretser.values():
        f.create_entity(
            "IfcRelAssignsToGroup",
            GlobalId=guid.new(),
            RelatedObjects=objekter,
            RelatingGroup=krets,
        )

    if rom is not None:
        # Én relasjon for hele etasjen, ikke én per objekt. Portene holdes
        # utenfor: de er koblinger, ikke noe som står i en etasje.
        f.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=guid.new(),
            RelatedElements=rom["innhold"],
            RelatingStructure=rom["etasje"],
        )

    sti.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(sti))
    return sti
