"""Leser én IFC-fil og trekker ut TFM-verdiene fra egenskapssettene."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.modell import IfcObjekt


def les_modell(sti: Path | str, config: Konfigurasjon | None = None) -> list[IfcObjekt]:
    """Åpner IFC 2x3 eller IFC4 og returnerer picklebare `IfcObjekt`.

    Ingen ifcopenshell-entiteter forlater denne funksjonen.
    """
    sti = Path(sti)
    config = config or Konfigurasjon()
    fil = ifcopenshell.open(str(sti))

    objekter: list[IfcObjekt] = []
    for produkt in fil.by_type("IfcProduct"):
        if produkt.is_a("IfcSpatialStructureElement"):
            continue
        egenskaper = _psets(produkt)
        objekter.append(
            IfcObjekt(
                global_id=produkt.GlobalId,
                ifc_klasse=produkt.is_a(),
                ifc_supertyper=_supertyper(produkt),
                navn=getattr(produkt, "Name", None),
                kildefil=sti.name,
                tfm_forekomst=_finn(
                    egenskaper, config.pset.forekomst, config.pset.egenskapsnavn_forekomst
                ),
                tfm_type=_finn(egenskaper, config.pset.type, config.pset.egenskapsnavn_type),
                mmi=_finn(egenskaper, config.pset.mmi, config.pset.egenskapsnavn_mmi),
            )
        )
    return objekter


@lru_cache(maxsize=512)
def _supertyper_for_klasse(klasse: str, skjema: str) -> tuple[str, ...]:
    """Arvekjeden over `klasse`, uten klassen selv.

    Cachet per (klasse, skjema): en modell har titusenvis av objekter, men
    sjelden mer enn hundre distinkte klasser.
    """
    deklarasjon = ifcopenshell.ifcopenshell_wrapper.schema_by_name(skjema).declaration_by_name(
        klasse
    )
    kjede: list[str] = []
    gjeldende = deklarasjon.as_entity()
    if gjeldende is None:
        return ()
    gjeldende = gjeldende.supertype()
    while gjeldende is not None:
        kjede.append(gjeldende.name())
        gjeldende = gjeldende.supertype()
    return tuple(kjede)


def _supertyper(produkt: Any) -> list[str]:
    try:
        return list(_supertyper_for_klasse(produkt.is_a(), produkt.wrapped_data.file.schema))
    except Exception:
        # Ukjent eller utvidet skjema — kontrollene faller tilbake til
        # eksakt klassematch. Ikke verdt å stoppe hele kjøringen for.
        return []


def _psets(produkt: Any) -> dict[str, dict[str, str]]:
    """Egenskapssett som ren dict.

    Håndterer både IFC4 (`IsDefinedBy`) og typeegenskaper. IfcOpenShell har
    `ifcopenshell.util.element.get_psets`, men den er tregere og drar inn
    mer enn vi trenger; her henter vi bare navn/verdi.
    """
    ut: dict[str, dict[str, str]] = {}
    for rel in getattr(produkt, "IsDefinedBy", None) or []:
        if not rel.is_a("IfcRelDefinesByProperties"):
            continue
        definisjon = rel.RelatingPropertyDefinition
        if not definisjon.is_a("IfcPropertySet"):
            continue
        verdier: dict[str, str] = {}
        for prop in definisjon.HasProperties or []:
            if not prop.is_a("IfcPropertySingleValue"):
                continue
            if prop.NominalValue is None:
                continue
            verdier[prop.Name] = str(prop.NominalValue.wrappedValue)
        if verdier:
            ut[definisjon.Name] = verdier
    return ut


def _finn(
    egenskaper: dict[str, dict[str, str]],
    pset_navn: list[str],
    egenskapsnavn: list[str],
) -> str | None:
    """Første treff på (pset, egenskap) i konfigurert prioritetsrekkefølge.

    Faller tilbake til å lete i alle psets — norske modeller er rotete nok
    til at riktig verdi ofte ligger i et pset ingen forutså (§7).
    """
    for pset in pset_navn:
        if pset not in egenskaper:
            continue
        for navn in egenskapsnavn:
            verdi = egenskaper[pset].get(navn)
            if verdi:
                return verdi.strip()
        # Pset-et finnes, men ingen av de forventede egenskapsnavnene:
        # ta første ikke-tomme verdi.
        for verdi in egenskaper[pset].values():
            if verdi and verdi.strip():
                return verdi.strip()

    for verdier in egenskaper.values():
        for navn in egenskapsnavn:
            verdi = verdier.get(navn)
            if verdi and verdi.strip():
                return verdi.strip()
    return None
