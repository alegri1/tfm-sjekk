"""Syntetiske IFC-modeller for testing (§7).

«Generer minimale modeller programmatisk med IfcOpenShell — ett objekt med
korrekt TFM, ett med feil sifferantall, ett uten pset.»

Disse er små nok til å ligge i repoet, og de inneholder ingen prosjektdata.
"""

from __future__ import annotations

import itertools
import uuid
from pathlib import Path

import ifcopenshell
import ifcopenshell.guid as guid
import ifcopenshell.template

GYLDIG = "++115080=3600.001.04-JVZ001%JVZ.001.008"


# Fast navnerom for uuid5. Verdien betyr ingenting i seg selv; den må bare
# ALDRI endres, ellers bytter hver eneste entitet i hver fikstur identitet på én
# gang. Samme forbehold som i rapport/bcf.py, og av samme grunn.
NAVNEROM = uuid.uuid5(uuid.NAMESPACE_URL, "urn:tfm-sjekk:fikstur")


def guidgiver(fro: str):
    """En rekke faste GlobalId-er, utledet av «frø:løpenummer».

    Demomodellene fikk før ny identitet hver kjøring, og da pekte en BCF laget
    i går på objekter som ikke fantes i dag. Vieweren svarte «None of the
    viewpoint components are found in your project» — uten at noe annet så
    galt ut. Funntallet var det samme, og filene så like ut.

    Nøkkelen er posisjonen i fila, ikke innholdet. Innholdet er ikke unikt:
    demomodellene har med vilje to objekter med samme TFM-verdi, og det er
    K6-duplikatet. En innholdsnøkkel ville gitt dem samme identitet.

    Prisen er at et objekt satt inn midt i lista forskyver alle etter det. Det
    er greit — da har dataene endret seg, og BCF-en skal lages på nytt uansett.
    Garantien vi trenger er at samme inndata gir samme utdata.

    Lages lokalt per fil, ikke som en modulglobal teller. Fiksturen kalles fra
    tester i vilkårlig rekkefølge, og delt muterbar tilstand ville virket helt
    til to av dem kjørte samtidig.
    """
    teller = itertools.count(1)

    def ny() -> str:
        return guid.compress(uuid.uuid5(NAVNEROM, f"{fro}:{next(teller)}").hex)

    return ny


def lag_modell(
    objekter: list[tuple[str, str | None]],
    sti: Path,
    schema: str = "IFC4",
    pset_navn: str = "TFM11_Forekomst",
    egenskapsnavn: str = "TFM",
    plassering: bool = False,
) -> Path:
    """Skriver en minimal IFC-fil.

    `objekter` er (ifc_klasse, tfm_verdi). tfm_verdi=None gir et objekt helt
    uten egenskapssett — tilfellet K1 skal fange.

    `plassering=True` gir hvert objekt et punkt, spredt langs x-aksen. Uten det
    har objektene ingen posisjon, og BCF-emnene blir uten kamera: vieweren sier
    da at det ikke er noe å zoome til. Standardverdien er False fordi
    kontrollene ikke bryr seg, og fordi en test krever nettopp en modell uten
    plassering. Demomodellene ber om True — det er dem noen faktisk åpner.
    """
    f = ifcopenshell.file(schema=schema)
    ny_guid = guidgiver(sti.name)

    for nummer, (klasse, tfm) in enumerate(objekter):
        element = f.create_entity(klasse, GlobalId=ny_guid(), Name=f"{klasse}-{tfm or 'utenTFM'}")
        if plassering:
            element.ObjectPlacement = _plassering(f, x=nummer * 2.0)
        if tfm is None:
            continue
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name=egenskapsnavn,
            NominalValue=f.create_entity("IfcLabel", tfm),
        )
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=ny_guid(), Name=pset_navn, HasProperties=[egenskap]
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ny_guid(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )

    sti.parent.mkdir(parents=True, exist_ok=True)
    _fest_header(f)
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
    ny_guid = guidgiver(sti.name)

    def lag(klasse: str, navn: str, pset_navn: str, felt: str, verdi: str):
        element = f.create_entity(klasse, GlobalId=ny_guid(), Name=navn)
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name=felt,
            NominalValue=f.create_entity("IfcLabel", verdi),
        )
        pset = f.create_entity(
            "IfcPropertySet", GlobalId=ny_guid(), Name=pset_navn, HasProperties=[egenskap]
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ny_guid(),
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
    _fest_header(f)
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
    ny_guid = guidgiver(sti.name)

    for i in range(antall):
        element = f.create_entity("IfcFlowTerminal", GlobalId=ny_guid(), Name=f"Terminal {i + 1}")
        egenskap = f.create_entity(
            "IfcPropertySingleValue",
            Name="Anleggskode",
            NominalValue=f.create_entity(
                "IfcLabel", f"++115080=3600.001.04-JVZ{i + 1:03d}%JVZ.001.008"
            ),
        )
        pset = f.create_entity(
            "IfcPropertySet",
            GlobalId=ny_guid(),
            Name="AnleggsData",
            HasProperties=[egenskap],
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ny_guid(),
            RelatedObjects=[element],
            RelatingPropertyDefinition=pset,
        )

    sti.parent.mkdir(parents=True, exist_ok=True)
    _fest_header(f)
    f.write(str(sti))
    return sti


TIDLIGFASE = [
    "=3600.001.04-JVZ001%JVZ.001.008",
    "=3600.001.04-JVZ002",
    "=3600.001.05-JVZ003",
    # K6: ekte duplikat av JVZ001. Med standardoppsettet parser ingen av de to,
    # så duplikatet er usynlig — det drukner i fem syntaksfunn om en del
    # prosjektet ikke har tatt stilling til. Det er hele poenget med modellen.
    "=3600.001.04-JVZ001",
    "=4310.001.12-QLF001",
]


def lag_tidligfasemodell(sti: Path, schema: str = "IFC4") -> Path:
    """Skriver en modell merket uten plassering — tidligfase.

    Byggnummeret er ikke bestemt ennå, mens systemet og komponenten er merket.
    Fra §11-samtalen 2026-08-20: «tidlig modell har ikke krav til f.eks.
    plassering».

    Med standardoppsettet gir hvert eneste objekt et syntaksfunn om «++»-delen.
    Med `krev_plassering = false` forsvinner de, og de ekte feilene blir synlige.
    Det er hele poenget med fila: forskjellen skal kunne ses, ikke bare leses om.
    """
    return lag_modell([("IfcFlowTerminal", tfm) for tfm in TIDLIGFASE], sti, schema=schema)


# Systemkoden 4340 er FIKTIV, og står som sådan i eksempler/FIKTIV-systemkoder.csv.
# Hvilken kode som faktisk betyr føringsvei i NS 3451 skal ikke ligge i dette
# repoet (§8) — og det trengs ikke: K8 bryr seg om at koden er konfigurert, ikke
# om hvilken den er.
FORINGSVEI = [
    # Koblingsboksen: føringsvei-kode, men ingen føringsvei-KLASSE. Eksporten ga
    # den en anonym proxy. Uten oppsettet meldes den; med det er den unntatt.
    # Dette er det eneste objektet oppsettet endrer noe for.
    ("IfcBuildingElementProxy", "++115080=4340.001.00-QLK001"),
    # Kabelrøret: samme kode, men klassen sier det selv. Unntatt begge veier —
    # å konfigurere systemkoder skal ikke slå av standardlista over klasser.
    ("IfcFlowSegment", "++115080=4340.001.00-QLK002"),
    # Uttaket: mangler kursnummer og er ingen føringsvei. Meldes begge veier.
    # Uten dette objektet ville en tom rapport sett ut som en virkende regel.
    ("IfcOutlet", "++115080=4310.001.00-QLF001"),
]


def lag_foringsveimodell(sti: Path, schema: str = "IFC4") -> Path:
    """Skriver en modell der ett objekt bare kan kjennes igjen på systemkoden.

    K8 kjenner en føringsvei på to måter: IFC-klassen og systemkoden. Klassen
    sier hva eksporten fikk til; systemkoden sier hva prosjektet har bestemt.
    En ekte Revit-eksport ga seksten koblingsbokser som IfcBuildingElementProxy
    — TFM-en sa føringsvei, klassen sa ingenting.

    Med standardoppsettet gir modellen to funn. Med eksempler/foringsvei.toml
    gir den ett, og det som blir igjen er det som skal bli igjen. Forskjellen
    skal kunne ses, ikke bare leses om.
    """
    return lag_modell(list(FORINGSVEI), sti, schema=schema)


# Lengdeenheter en modell kan komme i. Faktoren er meter per enhet.
#
# Ingen fikstur hadde en annen enhet enn meter før nå, og det er nettopp derfor
# kamerafeilen overlevde: antakelsen «modellens enhet er normalt meter» var sann
# i hver eneste fil vi prøvde mot. Den var usann i den første ekte eksporten.
METER = ("METRE", None, 1.0)
MILLIMETER = ("METRE", "MILLI", 0.001)
FOT = ("FOOT", None, 0.3048)


def _sett_lengdeenhet(f, enhet: tuple) -> None:
    """Bytter modellens LENGTHUNIT til den oppgitte.

    ifcopenshell.template.create gir alltid meter og tar ingen parameter for
    det. Revit gjør nettopp dette byttet når prosjektet er imperialt: en
    IfcConversionBasedUnit med FOOT og faktoren 0.3048.
    """
    navn, prefiks, faktor = enhet
    ua = f.by_type("IfcUnitAssignment")[0]
    andre = [u for u in ua.Units if getattr(u, "UnitType", None) != "LENGTHUNIT"]

    if navn == "METRE":
        ny_enhet = f.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE", Prefix=prefiks)
    else:
        meter = f.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
        ny_enhet = f.create_entity(
            "IfcConversionBasedUnit",
            Dimensions=f.create_entity("IfcDimensionalExponents", *[1, 0, 0, 0, 0, 0, 0]),
            UnitType="LENGTHUNIT",
            Name=navn,
            ConversionFactor=f.create_entity(
                "IfcMeasureWithUnit",
                ValueComponent=f.create_entity("IfcLengthMeasure", faktor),
                UnitComponent=meter,
            ),
        )
    ua.Units = [*andre, ny_enhet]


def lag_modell_med_enhet(
    sti: Path,
    enhet: tuple = METER,
    punkt: tuple[float, float, float] = (100.0, 200.0, 3.0),
    tfm: str = "++115080=4310.001.12-QLF001",
    schema: str = "IFC4",
) -> Path:
    """Ett objekt på et kjent punkt, i den lengdeenheten som oppgis.

    `punkt` er i modellens egen enhet. Skal to modeller vise det SAMME fysiske
    objektet, må tallene skille seg: 100 meter er 328.084 fot.

    Finnes for kamerafeilen. Et BCF-viewpoint skal stå i meter, og med en
    fot-modell havnet det 969 kilometer fra objektet — vieweren flyttet seg dit
    den ble bedt om, og modellen forsvant ut av bildet.
    """
    ny_guid = guidgiver(sti.name)
    f = ifcopenshell.template.create(
        schema_identifier=schema,
        project_globalid=ny_guid(),
        project_name="FIKTIVT enhetsprosjekt",
        mvd="CoordinationView_V2.0",
        timestring=FAST_TIDSSTEMPEL,
        timestamp=FAST_EPOKE,
    )
    _sett_lengdeenhet(f, enhet)

    element = f.create_entity(
        "IfcFlowTerminal",
        GlobalId=ny_guid(),
        Name="FIKTIVT objekt",
        ObjectPlacement=_plassering(f, *punkt),
    )
    egenskap = f.create_entity(
        "IfcPropertySingleValue", Name="TFM", NominalValue=f.create_entity("IfcLabel", tfm)
    )
    pset = f.create_entity(
        "IfcPropertySet",
        GlobalId=ny_guid(),
        Name="TFM11_Forekomst",
        HasProperties=[egenskap],
    )
    f.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=ny_guid(),
        RelatedObjects=[element],
        RelatingPropertyDefinition=pset,
    )
    _sett_eierhistorikk(f)
    sti.parent.mkdir(parents=True, exist_ok=True)
    _fest_header(f)
    f.write(str(sti))
    return sti


def _punkt(f, x: float = 0.0, y: float = 0.0, z: float = 0.0):
    return f.create_entity("IfcCartesianPoint", Coordinates=(x, y, z))


def _plassering(f, x: float = 0.0, y: float = 0.0, z: float = 0.0, forelder=None):
    akse = f.create_entity("IfcAxis2Placement3D", Location=_punkt(f, x, y, z))
    return f.create_entity("IfcLocalPlacement", PlacementRelTo=forelder, RelativePlacement=akse)


FAST_TIDSSTEMPEL = "2026-01-01T12:00:00"
# Samme øyeblikk som tall. IfcOwnerHistory bærer sekunder siden epoken, og
# template.create tar den fra klokka om vi ikke sier noe — da skiller to
# kjøringer seg på ett tegn i én linje, og bare i modellene med geometri.
FAST_EPOKE = 1767268800


def _fest_header(f) -> None:
    """Fryser tidsstempelet i FILE_NAME.

    ifcopenshell skriver klokka nå, med sekundoppløsning. To kjøringer av
    generatoren ga derfor ulike filer selv med faste GlobalId-er — og en test
    som lager to filer rett etter hverandre passerte likevel, fordi begge havnet
    innenfor samme sekund. Den kunne ikke feile pålitelig.

    Determinisme er hele poenget: en BCF skal fortsatt peke på de samme
    objektene etter at modellene er laget på nytt.
    """
    f.header.file_name.time_stamp = FAST_TIDSSTEMPEL


def _sett_eierhistorikk(f) -> None:
    """Gir hver IfcRoot-entitet prosjektets eierhistorikk.

    I IFC 2x3 er `OwnerHistory` PÅKREVD på IfcRoot. IFC4 gjorde den valgfri, og
    ifcopenshell setter den ikke av seg selv når entiteter opprettes for hånd.
    Resultatet er en fil som er gyldig IFC4 og ugyldig 2x3 — og en streng
    importør, som Revits, kan avvise den uten å si hvorfor.

    Gjøres som et etterpass over hele fila framfor ved hver `create_entity`.
    Da kan ingen ny entitet gli inn uten, slik de 94 av 95 gjorde her.
    """
    prosjekt = f.by_type("IfcProject")
    if not prosjekt or prosjekt[0].OwnerHistory is None:
        return
    historikk = prosjekt[0].OwnerHistory
    for entitet in f.by_type("IfcRoot"):
        if entitet.OwnerHistory is None:
            entitet.OwnerHistory = historikk


def _romlig_struktur(f, ny_guid) -> dict:
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
        GlobalId=ny_guid(),
        Name="FIKTIV tomt",
        ObjectPlacement=rot,
        CompositionType="ELEMENT",
    )
    bygg = f.create_entity(
        "IfcBuilding",
        GlobalId=ny_guid(),
        Name="FIKTIVT bygg 115080",
        ObjectPlacement=_plassering(f, forelder=rot),
        CompositionType="ELEMENT",
    )
    etasje = f.create_entity(
        "IfcBuildingStorey",
        GlobalId=ny_guid(),
        Name="Plan 1",
        ObjectPlacement=_plassering(f, forelder=bygg.ObjectPlacement),
        CompositionType="ELEMENT",
    )

    for forelder, barn in ((prosjekt, tomt), (tomt, bygg), (bygg, etasje)):
        f.create_entity(
            "IfcRelAggregates",
            GlobalId=ny_guid(),
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
    ny_guid = guidgiver(sti.name)
    if geometri:
        f = ifcopenshell.template.create(
            schema_identifier=schema,
            project_globalid=ny_guid(),
            project_name="FIKTIVT demoprosjekt 115080",
            # CoordinationView er MVD-en Revits IFC-importor forventer.
            # Standardverdien i ifcopenshell er ReferenceView, som er en
            # lese-MVD; med den apner ikke Revit fila.
            mvd="CoordinationView_V2.0",
            # Fast tidsstempel: fila skal kunne sammenlignes mellom kjoringer.
            timestring=FAST_TIDSSTEMPEL,
            timestamp=FAST_EPOKE,
        )
        rom = _romlig_struktur(f, ny_guid)
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
            "IfcPropertySet", GlobalId=ny_guid(), Name=sett_navn, HasProperties=[egenskap]
        )
        f.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ny_guid(),
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
        element = f.create_entity(klasse, GlobalId=ny_guid(), Name=navn)
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
        port = f.create_entity("IfcDistributionPort", GlobalId=ny_guid())
        f.create_entity(
            "IfcRelNests", GlobalId=ny_guid(), RelatingObject=element, RelatedObjects=[port]
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
                GlobalId=ny_guid(),
                RelatingPort=port_for(tavle),
                RelatedPort=port_for(objekt),
            )

            kurs = objekt_spek.get("kurs")
            if kurs is None:
                continue
            if kurs not in kretser:
                # Kretsklassen heter ikke det samme i de to skjemaene, og
                # IFC4-navnet finnes rett og slett ikke i 2x3.
                krets_klasse = (
                    "IfcDistributionCircuit"
                    if schema.startswith("IFC4")
                    else "IfcElectricalCircuit"
                )
                krets = f.create_entity(krets_klasse, GlobalId=ny_guid(), Name=kurs)
                kretser[kurs] = [krets, []]
            kretser[kurs][1].append(objekt)

    for krets, objekter in kretser.values():
        f.create_entity(
            "IfcRelAssignsToGroup",
            GlobalId=ny_guid(),
            RelatedObjects=objekter,
            RelatingGroup=krets,
        )

    if rom is not None:
        # Én relasjon for hele etasjen, ikke én per objekt. Portene holdes
        # utenfor: de er koblinger, ikke noe som står i en etasje.
        f.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=ny_guid(),
            RelatedElements=rom["innhold"],
            RelatingStructure=rom["etasje"],
        )
        _sett_eierhistorikk(f)

    sti.parent.mkdir(parents=True, exist_ok=True)
    _fest_header(f)
    f.write(str(sti))
    return sti
