"""BCF 2.1 — det viktigste utdataformatet (§5).

«BCF er bare en zip med XML per emne (markup.bcf, viewpoint.bcfv, valgfri
snapshot.png). IfcOpenShell har BCF-støtte, men formatet er enkelt nok til å
skrive selv om du vil unngå avhengigheten.»

Poenget: funn åpnes direkte i Solibri, Catenda, Dalux og BIMcollab. Uten
viewpoint er saken ikke klikkbar, og da mister formatet hele hensikten — så
hvert funn med en GlobalId får et viewpoint som velger nettopp det objektet.
Funn uten objekt (samlefunnene fra K7 og K8c) blir emner uten viewpoint; de
peker på modellen som helhet, ikke på noe å zoome til.

**Et viewpoint består av tre ting, ikke én.** Skjemaet krever bare utvalget,
men en viewer trenger alle tre, og BIMcollab ZOOM svarte «this issue has no
viewpoint to zoom to» helt til de var på plass:

- *Utvalget* (`Components/Selection`) sier hvilket objekt saken gjelder.
- *Kameraet* sier hvor man skal se fra. Et utvalg er ikke en synsvinkel.
- *Snapshotet* er bildet i sakslista. Alle buildingSMARTs egne
  konformitetsfiler har ett, og BIMcollab regner viewpointet som fraværende
  uten.

Alle tre er valgfrie i XSD-en, så ingen av manglene ble fanget av validering.
De ble funnet ved å importere fila i en ekte viewer, og de er grunnen til at
det punktet sto åpent så lenge.

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

Fila er prøvd i BIMcollab ZOOM. Innholdet er i tillegg validert mot
buildingSMARTs offisielle XSD-er for 2.1, og arkivstrukturen sammenlignet med
deres egne konformitetsfiler.
"""

from __future__ import annotations

import math
import struct
import uuid
import xml.etree.ElementTree as ET
import zipfile
import zlib
from datetime import UTC, datetime
from pathlib import Path

from tfm_sjekk.modell import Alvorlighet, Funn

BCF_VERSJON = "2.1"
FORFATTER = "tfm-sjekk"
ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Fast navnerom for uuid5. Verdien betyr ingenting i seg selv; den må bare
# aldri endres, ellers bytter alle emner identitet.
NAVNEROM = uuid.uuid5(uuid.NAMESPACE_URL, "urn:tfm-sjekk:bcf")

# Zip-oppføringer får fast tidsstempel. Se determinisme i moduldocstringen.
FAST_TIDSSTEMPEL = (1980, 1, 1, 0, 0, 0)

MAKS_TITTEL = 100

# Etikett på emner som peker på modellen som helhet framfor på et objekt.
MODELLNIVA = "modellnivå"

# Kameraets plassering i forhold til objektet, i modellens enhet (normalt
# meter). Skrått ovenfra, langt nok unna til at naboobjektene er med.
KAMERAAVSTAND = 8.0
KAMERAHOYDE = 6.0

# Samme farger som i HTML-rapporten, så alvorligheten ser lik ut begge steder.
FARGER = {
    Alvorlighet.FEIL: (192, 57, 43),
    Alvorlighet.ADVARSEL: (230, 126, 34),
    Alvorlighet.INFO: (127, 140, 141),
}


def skriv_bcf(
    funn: list[Funn],
    sti: Path,
    opprettet: str | None = None,
    forfatter: str = FORFATTER,
) -> Path:
    """Skriver funnene som en BCF 2.1-fil.

    `opprettet` er ISO 8601-tidsstempel; sendes inn for at utdata skal være
    reproduserbart. Uten det brukes klokka nå, og da er fila ikke
    byte-identisk med forrige kjøring.
    """
    opprettet = normaliser_tidsstempel(opprettet)
    sti.parent.mkdir(parents=True, exist_ok=True)

    brukte: set[str] = set()
    with zipfile.ZipFile(sti, "w", zipfile.ZIP_DEFLATED) as arkiv:
        _skriv(arkiv, "bcf.version", _versjonsfil())
        for f in sorted(funn, key=Funn.sorteringsnokkel):
            emne = _emne_guid(f, brukte)
            _skriv(arkiv, f"{emne}/markup.bcf", _markup(f, emne, opprettet, forfatter))
            if not f.global_id:
                continue
            # Filnavnene følger konvensjonen i buildingSMARTs egne filer, der
            # GUID-en i navnet er den samme som Viewpoints/@Guid.
            vp = _under_guid(emne, "viewpoint")
            _skriv(arkiv, f"{emne}/Viewpoint_{vp}.bcfv", _viewpoint(f, emne))
            _legg_ved(arkiv, f"{emne}/Snapshot_{vp}.png", _snapshot(f.alvorlighet))
    return sti


def normaliser_tidsstempel(opprettet: str | None) -> str:
    """ISO 8601 i UTC, slik BCF vil ha det.

    Godtar det `datetime.fromisoformat` godtar — «2026-01-01», «2026-01-01
    12:00:00», med eller uten sone — og regner om til UTC. En verdi uten sone
    tolkes som UTC framfor lokal tid: poenget med å sende inn tidsstempelet
    er reproduserbarhet, og lokal tid ville gitt ulik fil på to maskiner.
    """
    if opprettet is None:
        return datetime.now(UTC).strftime(ISO_FORMAT)
    try:
        tid = datetime.fromisoformat(opprettet.strip())
    except ValueError as feil:
        raise ValueError(
            f"«{opprettet}» er ikke et gyldig ISO 8601-tidsstempel. "
            f"Forventet noe som «2026-01-01T12:00:00Z»."
        ) from feil
    if tid.tzinfo is None:
        tid = tid.replace(tzinfo=UTC)
    return tid.astimezone(UTC).strftime(ISO_FORMAT)


def _skriv(arkiv: zipfile.ZipFile, navn: str, element: ET.Element) -> None:
    ET.indent(element)
    _legg_ved(arkiv, navn, ET.tostring(element, encoding="utf-8", xml_declaration=True))


def _legg_ved(arkiv: zipfile.ZipFile, navn: str, innhold: bytes) -> None:
    oppforing = zipfile.ZipInfo(navn, date_time=FAST_TIDSSTEMPEL)
    oppforing.compress_type = zipfile.ZIP_DEFLATED
    arkiv.writestr(oppforing, innhold)


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
    topic = ET.SubElement(rot, "Topic", {"Guid": emne, "TopicType": "Issue", "TopicStatus": "Open"})
    ET.SubElement(topic, "Title").text = _tittel(f)
    ET.SubElement(topic, "Priority").text = f.alvorlighet.value
    ET.SubElement(topic, "Labels").text = f.kontroll
    if not f.global_id:
        # Funnet peker på modellen som helhet, ikke på et objekt — typisk
        # K7-retningen «står i mastera, men er ikke modellert». Slike emner
        # har ingenting å zoome til, og en viewer sier fra om det på en måte
        # som ser ut som en feil. Etiketten gjør det til noe man kan filtrere
        # på i stedet for noe man lurer på.
        ET.SubElement(topic, "Labels").text = MODELLNIVA
    ET.SubElement(topic, "CreationDate").text = opprettet
    ET.SubElement(topic, "CreationAuthor").text = forfatter
    ET.SubElement(topic, "Description").text = f.melding

    kommentar = ET.SubElement(rot, "Comment", {"Guid": _under_guid(emne, "kommentar")})
    ET.SubElement(kommentar, "Date").text = opprettet
    ET.SubElement(kommentar, "Author").text = forfatter
    ET.SubElement(kommentar, "Comment").text = _detaljer(f)

    if f.global_id:
        vp = _under_guid(emne, "viewpoint")
        viewpoints = ET.SubElement(rot, "Viewpoints", {"Guid": vp})
        ET.SubElement(viewpoints, "Viewpoint").text = f"Viewpoint_{vp}.bcfv"
        ET.SubElement(viewpoints, "Snapshot").text = f"Snapshot_{vp}.png"

    return rot


def _viewpoint(f: Funn, emne: str) -> ET.Element:
    rot = ET.Element("VisualizationInfo", {"Guid": _under_guid(emne, "viewpoint")})
    komponenter = ET.SubElement(rot, "Components")
    # Selection før Visibility — skjemaet krever den rekkefølgen.
    utvalg = ET.SubElement(komponenter, "Selection")
    ET.SubElement(utvalg, "Component", {"IfcGuid": f.global_id or ""})
    ET.SubElement(komponenter, "Visibility", {"DefaultVisibility": "true"})

    # Kameraet kommer etter Components, også det er skjemaets rekkefølge.
    if f.posisjon is not None:
        _kamera(rot, f.posisjon)
    return rot


def _kamera(viewpoint: ET.Element, mål: tuple[float, float, float]) -> None:
    """Et perspektivkamera som ser mot objektet.

    Et utvalg alene er ikke nok: en viewer gjenoppretter en *synsvinkel*, og
    uten kamera svarer den «this issue has no viewpoint to zoom to» — utvalget
    blir aldri brukt. Det er den delen av formatet et skjema ikke fanger,
    siden kameraet er valgfritt der.

    Kameraet settes skrått ovenfra, som en RIE ville stilt seg selv: langt nok
    unna til at nabo-objektene er med, høyt nok til å se hva som står rundt.
    """
    forskyvning = (-KAMERAAVSTAND, -KAMERAAVSTAND, KAMERAHOYDE)
    øye = tuple(m + f for m, f in zip(mål, forskyvning, strict=True))

    retning = _normaliser(tuple(m - ø for m, ø in zip(mål, øye, strict=True)))
    # Opp-vektoren må stå vinkelrett på retningen, ellers vipper bildet.
    høyre = _normaliser(_kryss(retning, (0.0, 0.0, 1.0)))
    opp = _normaliser(_kryss(høyre, retning))

    kamera = ET.SubElement(viewpoint, "PerspectiveCamera")
    for navn, vektor in (
        ("CameraViewPoint", øye),
        ("CameraDirection", retning),
        ("CameraUpVector", opp),
    ):
        element = ET.SubElement(kamera, navn)
        for akse, verdi in zip("XYZ", vektor, strict=True):
            ET.SubElement(element, akse).text = f"{verdi:.6f}"
    ET.SubElement(kamera, "FieldOfView").text = "60"


def _snapshot(alvorlighet: Alvorlighet) -> bytes:
    """Et lite PNG i alvorlighetens farge.

    BCF-skjemaet gjør snapshot valgfritt, men alle buildingSMARTs egne
    konformitetsfiler har ett, og BIMcollab bygger saksvisningen sin rundt
    bildet — uten det regnes viewpointet som fraværende.

    Vi kan ikke rendre modellen; det ville krevd en 3D-motor i et verktøy som
    med vilje ikke har noen. Et ensfarget felt er derfor ikke en dårlig
    render, det er noe annet: en fargekode som viser alvorlighet i
    sakslista. At det ikke later som å være et bilde av modellen er poenget.
    """
    return _png(320, 180, FARGER[alvorlighet])


def _png(bredde: int, høyde: int, rgb: tuple[int, int, int]) -> bytes:
    """Minste gyldige PNG for et ensfarget felt, uten bildebibliotek.

    Formatet er enkelt nok til at en avhengighet ikke lønner seg, på samme
    måte som BCF-en selv. Utdata er deterministisk: samme farge gir samme
    byte, som resten av arkivet krever (§7).
    """
    rad = b"\x00" + bytes(rgb) * bredde  # filtertype 0 foran hver rad
    piksler = zlib.compress(rad * høyde, 9)

    def blokk(merke: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + merke
            + data
            + struct.pack(">I", zlib.crc32(merke + data) & 0xFFFFFFFF)
        )

    hode = struct.pack(">IIBBBBB", bredde, høyde, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n" + blokk(b"IHDR", hode) + blokk(b"IDAT", piksler) + blokk(b"IEND", b"")
    )


def _kryss(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, float, float]:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _normaliser(v: tuple[float, ...]) -> tuple[float, float, float]:
    lengde = math.sqrt(sum(k * k for k in v))
    if lengde == 0:
        return (0.0, 0.0, 1.0)
    return (v[0] / lengde, v[1] / lengde, v[2] / lengde)


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
    if f.tfm:
        # Objektets egen TFM, ikke verdien funnet handler om. K9 melder om MMI
        # og legger MMI-verdien i «verdi»; sto den her, ville emnet hatt en
        # linje som het TFM og inneholdt «200». Verdien funnet handler om står
        # uansett i Description, som viewerne viser i sin helhet.
        deler.append(f"TFM: {f.tfm}")
    return " · ".join(deler)
