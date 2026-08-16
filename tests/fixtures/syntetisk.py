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
