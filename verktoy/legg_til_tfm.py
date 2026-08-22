"""Legger TFM-merking inn i en ekte IFC-eksport, til bruk som testmodell.

    uv run python verktoy/legg_til_tfm.py inn.ifc ut.ifc

Bakgrunn: alle demomodellene i `eksempler/` er bygget av meg, og de har den
strukturen jeg forestilte meg. En ekte eksport fra Revit har 45 familier, 3350
porter og 448 systemer med kursnumre som navn — og den avslører ting en
håndlaget modell aldri kan.

Modellen som brukes er Autodesks «Snowdon Towers Sample Electrical», eksportert
fra Revit. Den har ingen TFM fra før. Dette skriptet skriver merking inn i den,
utledet av strukturen som allerede er der:

    plassering      ett byggnummer for hele modellen
    systemkode      fra familienavnet — lys, stikk, data, føring
    undernummer     fra IfcSystem-navnet, som ER kursnummeret fra Revit
    komponentkode   fra familien
    løpenummer      fortløpende per systemforekomst

Kursnummeret er poenget. Det er ekte data fra en ekte modell, og det er første
gang K8c får noe annet enn tall jeg har funnet på.

FEIL LEGGES INN MED VILJE, men få og spredt — en ekte modell er stort sett
riktig merket, og en testmodell der annethvert objekt er galt lærer ingenting om
hvordan rapporten ser ut i praksis.

Fila som lages er ikke i repoet: den er avledet av Autodesks eksempelmodell, og
`.gitignore` stopper `*.ifc` uansett. Lag den selv når du trenger den.

HVA DEN AVDEKKET FØRSTE GANG
Kjørt gjennom tfm-sjekk ga modellen 1029 funn. Elleve av dem var lagt inn her
med vilje; 1018 var K8 som krevde kursnummer av kabelrør og bend. Føringsveier
bærer kurser og ligger ikke på en, men ingen av de åtte demomodellene i
eksempler/ har en eneste av dem — de har tre til åtte objekter hver.

Regelen er nå snevret inn, og samme modell gir 179 funn. Det er derfor dette
skriptet finnes: en modell med 2439 objekter og 45 familier avslører ting en
håndlaget fikstur ikke kan.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import ifcopenshell
import ifcopenshell.guid as guid

PLASSERING = "115080"
PSET_NAVN = "TFM11_Forekomst"
FELT = "TFM"

# Familienavn -> (systemkode, komponentkode). NS 3451 kapittel 4 er elkraft,
# 5 er tele og automatisering. Kodene her er plausible, ikke autoritative —
# innholdet i standardene skal ikke inn i dette repoet (§8).
FAMILIER: dict[str, tuple[str, str]] = {
    "Lighting and Appliance Panelboard": ("4310", "QLF"),
    "Pendant-Dome": ("4320", "QLF"),
    "Recessed Lamp": ("4320", "QLF"),
    "Wall Lamp": ("4320", "QLF"),
    "Downlight": ("4320", "QLF"),
    "Ceiling Light": ("4320", "QLF"),
    "Pendant Lamp": ("4320", "QLF"),
    "Lighting Switches": ("4320", "QLB"),
    "Duplex Receptacle": ("4330", "QLS"),
    "High Voltage Receptacle": ("4330", "QLS"),
    "Data Outlet": ("5300", "QTD"),
    "Conduit": ("4360", "QLK"),
    "Electrical Equipment": ("4310", "QLT"),
    "Electrical Fixtures": ("4330", "QLS"),
}
STANDARD = ("4390", "QLX")


def _familie(navn: str | None) -> str:
    return (navn or "").split(":")[0].strip()


def _koder(navn: str | None) -> tuple[str, str]:
    familie = _familie(navn)
    for nøkkel, koder in FAMILIER.items():
        if familie.startswith(nøkkel):
            return koder
    return STANDARD


def _kurs_per_objekt(f: ifcopenshell.file) -> dict[str, str]:
    """GlobalId -> kursnummer, lest av IfcSystem-navnet.

    Revit eksporterer hver elektriske kurs som et IfcSystem der navnet er
    kursnummeret: «1», «2», «6,8». Et objekt kan høre til flere; første treff
    brukes, og det er godt nok — poenget er at tallet er ekte.
    """
    ut: dict[str, str] = {}
    for rel in f.by_type("IfcRelAssignsToGroup"):
        gruppe = rel.RelatingGroup
        if not gruppe.is_a("IfcSystem") or not gruppe.Name:
            continue
        # «6,8» betyr to kurser. Ta den første, og bare sifre.
        tall = "".join(c for c in gruppe.Name.split(",")[0] if c.isdigit())
        if not tall:
            continue
        for objekt in rel.RelatedObjects:
            ut.setdefault(objekt.GlobalId, tall.zfill(2)[:2])
    return ut


# Klasser som skal merkes. IfcDistributionElement dekker alt teknisk utstyr —
# terminaler, ventiler, rør, kanaler — gjennom arvekjeden.
#
# IfcBuildingElementProxy er med av en annen grunn: en ekte eksport legger ofte
# utstyr der, og det er nettopp det tilfellet «tfm-sjekk oppsett» finnes for.
# 934 merkede proxyer i denne modellen gir kommandoen ekte data å foreslå på.
MERKES = ("IfcDistributionElement", "IfcBuildingElementProxy")


def _skal_merkes(produkt) -> bool:
    """Akser, dekker og vegger skal ikke ha TFM.

    Første utgave merket alt som ikke var romlig struktur eller en port, og da
    fikk elleve IfcGrid, ett IfcSlab og én IfcWallStandardCase merking de aldri
    skulle hatt. Feilen var min, ikke modellens — men den ville sett ut som
    verktøyets i en rapport.
    """
    if produkt.is_a("IfcSpatialStructureElement") or produkt.is_a("IfcPort"):
        return False
    if not produkt.Name:
        return False
    return any(produkt.is_a(k) for k in MERKES)


def _merk(f: ifcopenshell.file, produkt, verdi: str) -> None:
    egenskap = f.create_entity(
        "IfcPropertySingleValue", Name=FELT, NominalValue=f.create_entity("IfcLabel", verdi)
    )
    pset = f.create_entity(
        "IfcPropertySet",
        GlobalId=guid.new(),
        OwnerHistory=produkt.OwnerHistory,
        Name=PSET_NAVN,
        HasProperties=[egenskap],
    )
    f.create_entity(
        "IfcRelDefinesByProperties",
        GlobalId=guid.new(),
        OwnerHistory=produkt.OwnerHistory,
        RelatedObjects=[produkt],
        RelatingPropertyDefinition=pset,
    )


def legg_til_tfm(inn: Path, ut: Path) -> dict[str, int]:
    f = ifcopenshell.open(str(inn))
    kurs = _kurs_per_objekt(f)

    produkter = [p for p in f.by_type("IfcProduct") if _skal_merkes(p)]

    teller: defaultdict[str, int] = defaultdict(int)
    tall = {"merket": 0, "uten_kurs": 0}
    tidligere: list[str] = []

    for n, produkt in enumerate(produkter):
        systemkode, komponentkode = _koder(produkt.Name)
        undernummer = kurs.get(produkt.GlobalId)
        if undernummer is None:
            undernummer = "00"  # ikke på noen kurs — tavler og føringsveier
            tall["uten_kurs"] += 1

        forekomst = f"{systemkode}.001.{undernummer}"
        teller[forekomst] += 1
        løpenummer = f"{teller[forekomst]:03d}"
        verdi = f"++{PLASSERING}={forekomst}-{komponentkode}{løpenummer}"

        # Tilsiktede feil, spredt tynt. En ekte modell er stort sett riktig
        # merket, og en testmodell der annethvert objekt er galt sier ingenting
        # om hvordan rapporten ser ut i praksis.
        if n % 700 == 13:  # K1: ingen TFM
            continue
        if n % 900 == 17:  # K2: for få siffer i plasseringen
            verdi = verdi.replace(f"++{PLASSERING}", f"++{PLASSERING[:-1]}")
        if n % 1100 == 23 and tidligere:  # K6: duplikat av et tidligere objekt
            verdi = tidligere[-1]
        if n % 1300 == 29:  # K3: systemkode som ikke finnes i noen tabell
            verdi = verdi.replace(f"={systemkode}", "=9999")

        _merk(f, produkt, verdi)
        tidligere.append(verdi)
        tall["merket"] += 1

    ut.parent.mkdir(parents=True, exist_ok=True)
    f.write(str(ut))
    tall["produkter"] = len(produkter)
    tall["med_kurs"] = len(produkter) - tall["uten_kurs"]
    return tall


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__.splitlines()[2].strip())
    tall = legg_til_tfm(Path(sys.argv[1]), Path(sys.argv[2]))
    for navn, verdi in tall.items():
        print(f"  {navn:12} {verdi}")
    print(f"  skrev        {sys.argv[2]}")
