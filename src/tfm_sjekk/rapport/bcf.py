"""BCF 2.1 — det viktigste utdataformatet (§5).

«BCF er bare en zip med XML per emne (markup.bcf, viewpoint.bcfv, valgfri
snapshot.png). IfcOpenShell har BCF-støtte, men formatet er enkelt nok til å
skrive selv om du vil unngå avhengigheten.»

Poenget: funn åpnes direkte i Solibri, Catenda, Dalux og BIMcollab. Uten
viewpoint er saken ikke klikkbar, og da mister formatet hele hensikten — så
hvert funn med en GlobalId får en `viewpoint.bcfv` som velger nettopp det
objektet. Funn uten objekt (samlefunnene fra K7 og K8c) blir emner uten
viewpoint; de peker på modellen som helhet, ikke på noe å zoome til.

**Determinisme.** Hele fila skal være byte-identisk for samme funn, ellers
er den ubrukelig som golden file (§7) og støyer i diff-er. Tre kilder til
tilfeldighet er lukket:

- *GUID-ene* er ikke tilfeldige, men utledet fra innholdet i funnet med
  `uuid5`. Samme funn gir samme emne-GUID i går og i morgen, og et emne som
  allerede er importert i en viewer beholder identiteten sin.
- *Tidsstempelet* sendes inn, ikke `datetime.now()` internt.
- *Zip-en* får fast tidsstempel på hver oppføring. Uten det ligger
  klokkeslettet i selve arkivbyte-ene.

Avvik fra notatet i stubben, med vilje: kontroll-ID-en havner i `Labels` og i
tittelen framfor i `Topic/@TopicType`. `TopicType` og `TopicStatus` skal
etter BCF-skjemaet komme fra prosjektets utvidelser, og en viewer som er
streng kan avvise «K6» der. `Labels` er fritekst, og det er nettopp der
viewerne filtrerer.

GJENSTÅR: åpne en generert fil i en ekte viewer (Catenda har gratis konto)
før dette kalles ferdig. Strukturen er verifisert mot skjemaet, ikke mot en
faktisk importrutine.
"""

from __future__ import annotations

import uuid
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tfm_sjekk.modell import Funn

BCF_VERSJON = "2.1"
FORFATTER = "tfm-sjekk"

# Fast navnerom for uuid5. Verdien betyr ingenting i seg selv; den må bare
# aldri endres, ellers bytter alle emner identitet.
NAVNEROM = uuid.uuid5(uuid.NAMESPACE_URL, "urn:tfm-sjekk:bcf")

# Zip-oppføringer får fast tidsstempel. Se determinisme i moduldocstringen.
FAST_TIDSSTEMPEL = (1980, 1, 1, 0, 0, 0)

MAKS_TITTEL = 100


def skriv_bcf(
    funn: list[Funn],
    sti: Path,
    opprettet: str | None = None,
    forfatter: str = FORFATTER,
) -> Path:
    """Skriver funnene som en BCF 2.1-fil.

    `opprettet` er ISO 8601-tidsstempel; sendes inn for at utdata skal være
    reproduserbart i tester.
    """
    opprettet = opprettet or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sti.parent.mkdir(parents=True, exist_ok=True)

    brukte: set[str] = set()
    with zipfile.ZipFile(sti, "w", zipfile.ZIP_DEFLATED) as arkiv:
        _skriv(arkiv, "bcf.version", _versjonsfil())
        for f in sorted(funn, key=Funn.sorteringsnokkel):
            emne = _emne_guid(f, brukte)
            _skriv(arkiv, f"{emne}/markup.bcf", _markup(f, emne, opprettet, forfatter))
            if f.global_id:
                _skriv(arkiv, f"{emne}/viewpoint.bcfv", _viewpoint(f, emne))
    return sti


def _skriv(arkiv: zipfile.ZipFile, navn: str, element: ET.Element) -> None:
    oppforing = zipfile.ZipInfo(navn, date_time=FAST_TIDSSTEMPEL)
    oppforing.compress_type = zipfile.ZIP_DEFLATED
    ET.indent(element)
    arkiv.writestr(
        oppforing,
        ET.tostring(element, encoding="utf-8", xml_declaration=True),
    )


def _emne_guid(f: Funn, brukte: set[str]) -> str:
    """GUID utledet fra innholdet, ikke trukket tilfeldig.

    To identiske funn ville fått samme GUID og kollidert i zip-en, så da
    legges det på en teller. Rekkefølgen er allerede deterministisk (§7), så
    telleren blir det også.
    """
    nokkel = f"{f.kontroll}|{f.kildefil or ''}|{f.global_id or ''}|{f.melding}"
    guid = str(uuid.uuid5(NAVNEROM, nokkel))
    teller = 1
    while guid in brukte:
        teller += 1
        guid = str(uuid.uuid5(NAVNEROM, f"{nokkel}#{teller}"))
    brukte.add(guid)
    return guid


def _under_guid(emne: str, rolle: str) -> str:
    """Kommentarer og viewpoints trenger egne GUID-er, avledet av emnets."""
    return str(uuid.uuid5(NAVNEROM, f"{emne}|{rolle}"))


def _versjonsfil() -> ET.Element:
    rot = ET.Element("Version", {"VersionId": BCF_VERSJON})
    ET.SubElement(rot, "DetailedVersion").text = BCF_VERSJON
    return rot


def _markup(f: Funn, emne: str, opprettet: str, forfatter: str) -> ET.Element:
    rot = ET.Element("Markup")

    if f.kildefil:
        hode = ET.SubElement(rot, "Header")
        fil = ET.SubElement(hode, "File", {"isExternal": "true"})
        ET.SubElement(fil, "Filename").text = f.kildefil
        ET.SubElement(fil, "Date").text = opprettet

    # Rekkefølgen på barna under er den BCF 2.1-skjemaet krever.
    topic = ET.SubElement(
        rot, "Topic", {"Guid": emne, "TopicType": "Issue", "TopicStatus": "Open"}
    )
    ET.SubElement(topic, "Title").text = _tittel(f)
    ET.SubElement(topic, "Priority").text = f.alvorlighet.value
    ET.SubElement(topic, "Labels").text = f.kontroll
    ET.SubElement(topic, "CreationDate").text = opprettet
    ET.SubElement(topic, "CreationAuthor").text = forfatter
    ET.SubElement(topic, "Description").text = f.melding

    kommentar = ET.SubElement(rot, "Comment", {"Guid": _under_guid(emne, "kommentar")})
    ET.SubElement(kommentar, "Date").text = opprettet
    ET.SubElement(kommentar, "Author").text = forfatter
    ET.SubElement(kommentar, "Comment").text = _detaljer(f)

    if f.global_id:
        viewpoints = ET.SubElement(
            rot, "Viewpoints", {"Guid": _under_guid(emne, "viewpoint")}
        )
        ET.SubElement(viewpoints, "Viewpoint").text = "viewpoint.bcfv"

    return rot


def _viewpoint(f: Funn, emne: str) -> ET.Element:
    rot = ET.Element("VisualizationInfo", {"Guid": _under_guid(emne, "viewpoint")})
    komponenter = ET.SubElement(rot, "Components")
    # Selection før Visibility — skjemaet krever den rekkefølgen.
    utvalg = ET.SubElement(komponenter, "Selection")
    ET.SubElement(utvalg, "Component", {"IfcGuid": f.global_id or ""})
    ET.SubElement(komponenter, "Visibility", {"DefaultVisibility": "true"})
    return rot


def _tittel(f: Funn) -> str:
    """Kort nok til å leses i en emneliste; hele meldinga står i Description."""
    tekst = f"{f.kontroll}: {f.melding}"
    if len(tekst) <= MAKS_TITTEL:
        return tekst
    return tekst[: MAKS_TITTEL - 1].rstrip() + "…"


def _detaljer(f: Funn) -> str:
    deler = [f"Kontroll: {f.kontroll}", f"Alvorlighet: {f.alvorlighet.value}"]
    if f.kildefil:
        deler.append(f"Fil: {f.kildefil}")
    if f.ifc_klasse:
        deler.append(f"IFC-klasse: {f.ifc_klasse}")
    if f.verdi:
        deler.append(f"TFM-verdi: {f.verdi}")
    return " · ".join(deler)
