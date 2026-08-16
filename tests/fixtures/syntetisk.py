"""Syntetiske IFC-modeller for testing (§7).

«Generer minimale modeller programmatisk med IfcOpenShell — ett objekt med
korrekt TFM, ett med feil sifferantall, ett uten pset.»

Disse er små nok til å ligge i repoet, og de inneholder ingen prosjektdata.
"""

from __future__ import annotations

from pathlib import Path

import ifcopenshell
import ifcopenshell.guid as guid

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


def lag_elektromodell(
    fordelinger: list[dict],
    sti: Path,
    schema: str = "IFC4",
    pset_navn: str = "TFM11_Forekomst",
    egenskapsnavn: str = "TFM",
) -> Path:
    """Skriver en modell med fordelinger, tilkoblede objekter og kurser (K8b/K8c).

    Hver fordeling er en dict::

        {"navn": "Fordeling 1", "tfm": "++115080=4310.001.00-QLF001",
         "klasse": "IfcElectricDistributionBoard",
         "objekter": [{"klasse": "IfcLamp", "tfm": "...", "kurs": "Kurs 12"}]}

    Objektene kobles til fordelingen slik en ekte eksport gjør det: hver ende
    har en `IfcDistributionPort` festet med `IfcRelNests`, og portene knyttes
    sammen med `IfcRelConnectsPorts`. `kurs` grupperer objektet i en
    `IfcDistributionCircuit` med det navnet.
    """
    f = ifcopenshell.file(schema=schema)
    kretser: dict[str, list] = {}

    def lag(klasse: str, navn: str, tfm: str | None):
        element = f.create_entity(klasse, GlobalId=guid.new(), Name=navn)
        if tfm is not None:
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
        )
        for indeks, objekt_spek in enumerate(spesifikasjon.get("objekter", []), start=1):
            objekt = lag(
                objekt_spek.get("klasse", "IfcFlowTerminal"),
                objekt_spek.get("navn", f"Objekt {nummer}.{indeks}"),
                objekt_spek.get("tfm"),
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

    sti.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(sti))
    return sti
