"""Bygger demomappa av repoet, med tall målt av kjøringene den beskriver.

    uv run python verktoy/lag_demomappe.py --mappe <sti> --versjon 0.7.0

Demomappa så lenge ut som en samling innhold. Den var det ikke: femten av
tjueto filer var byte-identiske kopier av repofiler, og bare tre var ekte
unikater. Den var en byggeartefakt som ble vedlikeholdt for hånd, og derfor drev
den — tre ganger i samme runde 24. august 2026:

    avsnittet ba deg finne stien «rapport-2x3\\funn.csv» i Dynamo-grafen,
        og den stien fantes ikke i fila
    «tidligfase.toml» var beskrevet og lå ikke i mappa
    «4 funn» for foringsvei.ifc var målt med tabellene i oppsettet;
        uten dem er det 2. Tallet var skrevet en time tidligere

Ingen av dem kunne en test fange. Alle tre ble funnet ved å kjøre kommandoene i
dokumentet og sammenligne for hånd — som er nøyaktig det denne fila gjør nå.

DET BÆRENDE VALGET: tallene måles ved å kjøre BINÆREN i mappa, ikke ved å
importere tfm_sjekk og telle funn. Det er forskjellen på å prøve koden og å prøve
leveransen. En binær kan være en annen generasjon enn kilden, og det er nettopp
den forskjellen mappa finnes for å vise.

Prisen er at byggingen tar minutter — Snowdon alene er 2439 objekter, og den
kjøres to ganger. Det er riktig pris for noe som kjøres når en utgivelse er ny.

FILENE FRA REVIT-RUNDEN RØRES IKKE. De fire under kan ikke lages av et skript —
de krever Revit, en modell og et menneske. Byggingen stopper om en av dem
mangler, og den sletter aldri noe: den skriver over det den eier og lar resten
være.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
MAL = ROT / "verktoy" / "demomappe-LES-MEG.mal.txt"

# Filene byggingen eier: de kopieres fra repoet, og en endring gjort i mappa går
# tapt ved neste kjøring. Det er meningen — kilden er repoet.
KOPIER = {
    "FIKTIV-komponentkoder.csv": "eksempler/FIKTIV-komponentkoder.csv",
    "FIKTIV-systemkoder.csv": "eksempler/FIKTIV-systemkoder.csv",
    "FIKTIV-tfm-master.csv": "eksempler/FIKTIV-tfm-master.csv",
    "demo-rie.ifc": "eksempler/demo-rie.ifc",
    "demo-riv.ifc": "eksempler/demo-riv.ifc",
    "demo-elektro.ifc": "eksempler/demo-elektro.ifc",
    "avveie.ifc": "eksempler/avveie.ifc",
    "blindsone.ifc": "eksempler/blindsone.ifc",
    "tidligfase.ifc": "eksempler/tidligfase.ifc",
    "tidligfase.toml": "eksempler/tidligfase.toml",
    "foringsvei.ifc": "eksempler/foringsvei.ifc",
    "foringsvei.toml": "eksempler/foringsvei.toml",
    "tfm-sjekk-tfm-fra-revit.dyn": "dynamo/tfm-sjekk-tfm-fra-revit.dyn",
    "tfm-sjekk-tfm-til-revit.dyn": "dynamo/tfm-sjekk-tfm-til-revit.dyn",
}

# Resultatet av en runde gjennom Revit. Kan ikke gjenskapes, og skal derfor
# finnes fra før. En bygging som ryddet mappa ville tatt med seg det eneste i
# den som ikke lot seg lage på nytt.
FRA_REVIT = [
    "snowdon-tfm.ifc",
    "snowdon-eksport.ifc",
    "eksport.ifc",
]

# «Snowdon Towers Sample Electrical.rvt» sto her til 25. august 2026. Den er
# 39 MB, byggingen leser den aldri, og en demomappe er noe man sender til en
# RIE — Revit-modellene hører hjemme et annet sted. Kjeden de inngår i står
# fortsatt beskrevet i malen, med en linje om hvor filene ligger.

# Blokkene i repoets tfm-sjekk.toml som byttes ut når mappa bygges. Begge er
# kommentert ut der: malen er en oversikt over alle nøklene, ikke et oppsett.
# Står de her og ikke som en regex, ser en endring i malen ut som det den er —
# byggingen stopper med «malen har endret form» framfor å skrive en fil der
# halve forklaringen mangler.
LF = chr(10)
CRLF = chr(13) + chr(10)


def linjer_til_tekst(linjer: list[str]) -> str:
    """Linjer til én tekst med avsluttende linjeskift."""
    return LF.join(linjer) + LF


TABELLER_I_MALEN = """# tfm_master = "TFM-master.xlsx"
# systemtabell = "tabeller/min-ns3451.csv"
# komponenttabell = "tabeller/min-ns3457-8.csv"
"""

RUTEN_I_MALEN = """# modeller = ["eksport/*.ifc"]
# ut = "rapport"
"""

TABELLFLAGG = [
    "--systemtabell",
    "FIKTIV-systemkoder.csv",
    "--komponenttabell",
    "FIKTIV-komponentkoder.csv",
    "--master",
    "FIKTIV-tfm-master.csv",
]


class Byggefeil(Exception):
    """Byggingen kan ikke stå inne for resultatet, og leverer det derfor ikke.

    En mappe som mangler én fil ser ut som en ferdig mappe. Det er samme
    tvetydighet som «ingen funn» mot «ingenting sjekket», og her er den verre:
    mappa sendes til noen som ikke kan se hva som skulle vært der.
    """


# --- Kjøring ---------------------------------------------------------------


def kjor(exe: Path, argumenter: list[str], mappe: Path) -> subprocess.CompletedProcess:
    """Kjører binæren i mappa, med mappa som arbeidskatalog.

    `sjekk` gir exit 1 når den finner feil, og det er ikke en feilet kommando —
    det er hele poenget med verktøyet. Exit 2 og oppover er derimot noe galt med
    selve kjøringen, og da skal byggingen stoppe framfor å måle på en rapport
    som ikke ble laget.
    """
    resultat = subprocess.run(
        [str(exe), *argumenter],
        cwd=str(mappe),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultat.returncode > 1:
        raise Byggefeil(
            "kommandoen «{}» ga exit {}:\n{}".format(
                " ".join(argumenter), resultat.returncode, resultat.stdout + resultat.stderr
            )
        )
    return resultat


def funn(mappe: Path, ut: str) -> list[dict[str, str]]:
    """Radene i funn.csv, lest slik verktøyet skrev dem."""
    sti = mappe / ut / "funn.csv"
    if not sti.is_file():
        raise Byggefeil(f"ingen funn.csv i {ut}/ — kjøringen skrev ingen rapport")
    with sti.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def i_omfang(resultat: subprocess.CompletedProcess, navn: str) -> str:
    """«3 av 4» ut av dekningslinja for én modell.

    Leses av utskriften og ikke regnet ut på nytt, fordi det er utskriften
    dokumentet gjengir. Regnet ut en annen vei kunne de to blitt uenige.
    """
    for linje in resultat.stdout.splitlines():
        if navn in linje and "i omfanget" in linje:
            treff = re.search(r"(\d+) av (\d+)", linje)
            if treff:
                return f"{treff.group(1)} av {treff.group(2)}"
    raise Byggefeil(f"fant ingen dekningslinje for {navn} i utskriften")


def objekttall(resultat: subprocess.CompletedProcess) -> str:
    for linje in resultat.stdout.splitlines():
        treff = re.match(r"\s+(\d+) objekter\s*$", linje)
        if treff:
            return treff.group(1)
    raise Byggefeil("fant ingen objekttelling i utskriften")


# --- Stegene ---------------------------------------------------------------


def sjekk_revitfilene(mappe: Path) -> None:
    mangler = [n for n in FRA_REVIT if not (mappe / n).is_file()]
    if mangler:
        raise Byggefeil(
            "disse kommer fra en runde gjennom Revit og kan ikke bygges:\n  "
            + "\n  ".join(mangler)
            + "\nLegg dem i mappa først."
        )


def kopier_kildene(mappe: Path) -> None:
    for navn, kilde in KOPIER.items():
        sti = ROT / kilde
        if not sti.is_file():
            raise Byggefeil(f"kilden finnes ikke: {kilde}")
        shutil.copy2(sti, mappe / navn)


def lag_modellene() -> None:
    """Kaller generatoren i eksempler/, som eier hvordan modellene ser ut."""
    resultat = subprocess.run(
        [sys.executable, str(ROT / "eksempler" / "lag_demomodell.py")],
        cwd=str(ROT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultat.returncode != 0:
        raise Byggefeil("lag_demomodell.py feilet:\n" + resultat.stdout + resultat.stderr)


def hent_binaeren(mappe: Path, versjon: str) -> Path:
    """Binæren fra utgivelsen, ikke en bygget her.

    Mappa skal inneholde nøyaktig den fila en bruker ville lastet ned. En lokal
    PyInstaller-bygging gir noe som ligner og som røyktesten i CI aldri har sett.
    """
    if shutil.which("gh") is None:
        raise Byggefeil("«gh» finnes ikke på maskinen, og binæren kan ikke hentes")

    exe = mappe / "tfm-sjekk.exe"
    resultat = subprocess.run(
        [
            "gh",
            "release",
            "download",
            f"v{versjon}",
            "-R",
            "alegri1/tfm-sjekk",
            "-p",
            "tfm-sjekk-windows.exe",
            "-O",
            str(exe),
            "--clobber",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if resultat.returncode != 0 or not exe.is_file():
        raise Byggefeil(f"kunne ikke hente binæren for v{versjon}:\n{resultat.stderr}")
    return exe


def bekreft_versjonen(exe: Path, versjon: str, mappe: Path) -> None:
    """Binæren skal si det samme som dokumentet kommer til å si.

    Mappa er ikke i versjonskontroll og er den eneste kilden mottakeren har.
    Sier dokumentet én versjon og binæren en annen, er hvert tall i dokumentet
    ubekreftet — og en BCF laget av en eldre utgave ser helt riktig ut.
    """
    kjor(exe, ["sjekk", "demo-rie.ifc", "--ut", "versjonsprove"], mappe)
    bcf = mappe / "versjonsprove" / "funn.bcfzip"
    if not bcf.is_file():
        raise Byggefeil("fikk ingen BCF å lese versjonen av")

    import zipfile

    with zipfile.ZipFile(bcf) as z:
        markup = next((n for n in z.namelist() if n.endswith("markup.bcf")), None)
        if markup is None:
            raise Byggefeil("BCF-en har ingen emner å lese forfatteren av")
        treff = re.search(
            r"<CreationAuthor>tfm-sjekk ([^<]+)</CreationAuthor>", z.read(markup).decode("utf-8")
        )
    shutil.rmtree(mappe / "versjonsprove")

    if treff is None:
        raise Byggefeil("BCF-en oppgir ingen versjon i CreationAuthor")
    if treff.group(1) != versjon:
        raise Byggefeil(
            f"binæren sier {treff.group(1)}, men mappa skal være v{versjon}. "
            "Da er det ikke den utgivelsen dokumentet påstår."
        )


def skriv_oppsettet(mappe: Path) -> None:
    """tfm-sjekk.toml med ruten, og kjor.cmd med tabellene.

    Bygges av repoets egen mal, så en ny nøkkel der havner her uten at noen må
    huske det. To blokker byttes ut, og begge er kommentert ut i malen:

        tabellstiene    ->  forklaringen på hvorfor de IKKE står her
        ruten           ->  ruten, levende

    Tabellene står bevisst i kjor.cmd og ikke i oppsettet. Mappa er ikke ett
    prosjekt; den er flere uavhengige demoer, og snowdon-tfm.ifc skal med vilje
    kjøre uten tabeller — med dem gir den over fem tusen funn i stedet for under
    to hundre. Et oppsett med tabellene ville gjeldt for hver kjøring i mappa.

    Forklaringen skrives inn i fila og står ikke bare her, fordi det er fila
    mottakeren leser når hun lurer på hvorfor de mangler.
    """
    mal = (ROT / "tfm-sjekk.toml").read_text(encoding="utf-8")

    tabeller_ut = linjer_til_tekst(
        [
            "# I ET EKTE PROSJEKT staar tabellene her:",
            "#",
            '#     tfm_master = "FIKTIV-tfm-master.csv"',
            '#     systemtabell = "FIKTIV-systemkoder.csv"',
            '#     komponenttabell = "FIKTIV-komponentkoder.csv"',
            "#",
            "# I DENNE MAPPA staar de i kjor.cmd i stedet. Mappa er ikke ett prosjekt,",
            "# den er flere uavhengige demoer, og noen skal med vilje kjoere UTEN",
            "# tabellene - snowdon-tfm.ifc er den viktigste. Tabeller i oppsettet ville",
            "# gjeldt for hver eneste kjoering her.",
        ]
    )

    # Prosaen over de to linjene staar allerede i malen og forklarer exit 2.
    # Her legges bare det som er sant for denne mappa.
    rute_inn = linjer_til_tekst(
        [
            "# I DENNE MAPPA er ruten satt, og kjor.cmd bruker den.",
            "# Skrevet av verktoy/lag_demomappe.py - endringer her gaar tapt.",
            'modeller = ["demo-rie.ifc", "demo-riv.ifc", "demo-elektro.ifc"]',
            'ut = "rapport"',
        ]
    )

    for merke, erstatning in ((TABELLER_I_MALEN, tabeller_ut), (RUTEN_I_MALEN, rute_inn)):
        if merke not in mal:
            raise Byggefeil(
                "fant ikke denne blokka i tfm-sjekk.toml, malen har endret form: "
                + merke.splitlines()[0]
            )
        mal = mal.replace(merke, erstatning, 1)

    (mappe / "tfm-sjekk.toml").write_text(mal, encoding="utf-8")

    q = chr(34)
    kommandoen = q + "%~dp0tfm-sjekk.exe" + q + " sjekk " + " ".join(TABELLFLAGG)
    cmd = [
        "@echo off",
        "rem Den faste ruten: modellene og rapportmappa staar i tfm-sjekk.toml,",
        "rem saa filnavn og --ut trengs ikke. Tabellene staar her framfor i",
        "rem oppsettet, fordi de andre demoene i mappa skal kjore uten dem.",
        "rem",
        "rem Skrevet av verktoy/lag_demomappe.py. Endringer her gaar tapt.",
        "cd /d " + q + "%~dp0" + q,
        kommandoen,
        "echo.",
        "pause",
    ]
    (mappe / "kjor.cmd").write_bytes(CRLF.join(cmd).encode("ascii") + CRLF.encode("ascii"))


def mal_tall(exe: Path, mappe: Path, versjon: str) -> dict[str, str]:
    """Hvert tall dokumentet oppgir, målt av kommandoen dokumentet viser."""
    verdier: dict[str, str] = {"versjon": versjon}

    kjor(exe, ["sjekk", *TABELLFLAGG], mappe)
    verdier["demo_funn"] = str(len(funn(mappe, "rapport")))

    ut = kjor(exe, ["sjekk", "avveie.ifc", "--ut", "a1"], mappe)
    verdier["avveie_for"] = i_omfang(ut, "avveie.ifc")
    kjor(exe, ["oppsett", "avveie.ifc", "--ut", "forslag.toml"], mappe)
    ut = kjor(exe, ["sjekk", "avveie.ifc", "--config", "forslag.toml", "--ut", "a2"], mappe)
    verdier["avveie_etter"] = i_omfang(ut, "avveie.ifc")

    kjor(exe, ["sjekk", "blindsone.ifc", "--ut", "bs"], mappe)
    verdier["blindsone_funn"] = str(len(funn(mappe, "bs")))

    kjor(exe, ["sjekk", "tidligfase.ifc", "--ut", "tf1"], mappe)
    verdier["tidligfase_for"] = str(len(funn(mappe, "tf1")))
    kjor(exe, ["sjekk", "tidligfase.ifc", "--config", "tidligfase.toml", "--ut", "tf2"], mappe)
    verdier["tidligfase_etter"] = str(len(funn(mappe, "tf2")))

    kjor(exe, ["sjekk", "foringsvei.ifc", "--ut", "fv1"], mappe)
    verdier["foringsvei_for"] = str(len(funn(mappe, "fv1")))
    kjor(exe, ["sjekk", "foringsvei.ifc", "--config", "foringsvei.toml", "--ut", "fv2"], mappe)
    verdier["foringsvei_etter"] = str(len(funn(mappe, "fv2")))

    # Her skiller dokumentet feil fra info, og da må målingen gjøre det også.
    # Totalen ville gjort setningen «3 funn ... pluss 2 info-linjer», som
    # teller de samme radene to ganger.
    kjor(exe, ["sjekk", "eksport.ifc", "--ut", "ut-eksport"], mappe)
    rader = funn(mappe, "ut-eksport")
    verdier["eksport_feil"] = str(sum(1 for r in rader if r["alvorlighet"] == "feil"))
    verdier["eksport_info"] = str(sum(1 for r in rader if r["alvorlighet"] == "info"))

    # Snowdon: den store, og den eneste der fordelingen skrives ut.
    ut = kjor(exe, ["sjekk", "snowdon-tfm.ifc", "--ut", "snowdon-rapport"], mappe)
    rader = funn(mappe, "snowdon-rapport")
    verdier["snowdon_objekter"] = objekttall(ut)
    verdier["snowdon_funn"] = str(len(rader))
    verdier.update(_snowdon_fordeling(rader))

    kjor(exe, ["sjekk", "snowdon-eksport.ifc", "--ut", "ut-snowdon"], mappe)
    verdier["snowdon_eksport_funn"] = str(len(funn(mappe, "ut-snowdon")))

    kjor(exe, ["sjekk", "snowdon-tfm.ifc", *TABELLFLAGG, "--ut", "s-tabeller"], mappe)
    verdier["snowdon_med_tabeller"] = str(len(funn(mappe, "s-tabeller")))

    for midlertidig in ("a1", "a2", "bs", "tf1", "tf2", "fv1", "fv2", "s-tabeller"):
        shutil.rmtree(mappe / midlertidig, ignore_errors=True)
    (mappe / "forslag.toml").unlink(missing_ok=True)

    return verdier


TEKST = {
    "K1": "mangler TFM",
    "K2": "feil i grammatikken",
    "K6": "samme komponentforekomst to steder",
    "K8": "elektroobjekt uten kursnummer",
}


def _snowdon_fordeling(rader: list[dict[str, str]]) -> dict[str, str]:
    """Tabellen over hvilke kontroller som slo ut, og hvilke klasser K8 traff."""
    per_kontroll = Counter(r["kontroll"] for r in rader)
    bredde = max((len(str(a)) for a in per_kontroll.values()), default=1)
    linjer = [
        "    {}  {:>{}}    {}".format(k, a, bredde, TEKST.get(k, ""))
        for k, a in sorted(per_kontroll.items())
    ]

    k8 = [r for r in rader if r["kontroll"] == "K8"]
    per_klasse = Counter(r.get("ifc_klasse") or r.get("klasse") or "ukjent" for r in k8)
    klasser = " og ".join(f"{navn} ({antall})" for navn, antall in per_klasse.most_common())

    return {
        "snowdon_fordeling": "\n".join(linjer),
        "snowdon_ekte": str(len(k8)),
        "snowdon_tilsiktet": str(len(rader) - len(k8)),
        "snowdon_klasser": klasser or "ingen klasse oppgitt",
    }


def skriv_les_meg(mappe: Path, verdier: dict[str, str]) -> None:
    """Fyller malen, og nekter å skrive om noe ikke ble målt.

    `str.format` kaster på en plassholder uten verdi, men ikke på en verdi uten
    plassholder. Legger noen til et tall i malen uten å måle det, ville teksten
    blitt skrevet med «{nytt_tall}» stående midt i — det ser ut som en skrivefeil
    og ikke som en manglende måling, og mottakeren kan ikke vite hvilken.
    """
    if not MAL.is_file():
        raise Byggefeil(f"malen finnes ikke: {MAL}")
    mal = MAL.read_bytes().decode("utf-8").replace("\r\n", "\n")

    try:
        tekst = mal.format(**verdier)
    except KeyError as feil:
        raise Byggefeil(f"malen har en plassholder byggingen ikke måler: {feil}") from feil

    igjen = sorted(set(re.findall(r"\{[a-z_]+\}", tekst)))
    if igjen:
        raise Byggefeil("plassholdere som ikke ble fylt ut: " + ", ".join(igjen))

    # BOM, CRLF og ingen tabulator: fila åpnes i Notisblokk på en norsk
    # Windows-maskin, og alle tre er sett gå galt der før.
    if chr(9) in tekst:
        raise Byggefeil("teksten inneholder tabulator, og Notisblokk viser den ulikt")
    (mappe / "LES-MEG.txt").write_bytes(("﻿" + tekst.replace("\n", "\r\n")).encode("utf-8"))


def si_fra_om_fremmede(mappe: Path) -> list[str]:
    """Filer byggingen ikke kjenner. Nevnes, aldri slettes.

    En fil ingen har plassert der med vilje er verdt et blikk, men ikke verdt å
    slette uten å spørre — og mappa er ikke i versjonskontroll, så en sletting
    her er endelig.
    """
    kjente = (
        set(KOPIER)
        | set(FRA_REVIT)
        | {
            "tfm-sjekk.exe",
            "tfm-sjekk.toml",
            "kjor.cmd",
            "LES-MEG.txt",
            "rapport",
            "snowdon-rapport",
            "ut-snowdon",
            "ut-eksport",
        }
    )
    return sorted(n for n in os.listdir(mappe) if n not in kjente)


# --- Skallet ---------------------------------------------------------------


def bygg(mappe: Path, versjon: str) -> dict[str, str]:
    if not mappe.is_dir():
        raise Byggefeil(f"mappa finnes ikke: {mappe}")

    print("  Revit-filene…")
    sjekk_revitfilene(mappe)
    print("  modellene…")
    lag_modellene()
    print("  kildene…")
    kopier_kildene(mappe)
    print("  oppsettet…")
    skriv_oppsettet(mappe)
    print(f"  binæren v{versjon}…")
    exe = hent_binaeren(mappe, versjon)
    bekreft_versjonen(exe, versjon, mappe)
    print("  måler tallene (dette tar noen minutter)…")
    verdier = mal_tall(exe, mappe, versjon)
    print("  LES-MEG.txt…")
    skriv_les_meg(mappe, verdier)
    return verdier


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mappe", required=True, type=Path, help="demomappa som skal bygges")
    ap.add_argument("--versjon", required=True, help="utgivelsen binæren hentes fra, f.eks. 0.7.0")
    args = ap.parse_args()

    try:
        verdier = bygg(args.mappe, args.versjon)
    except Byggefeil as feil:
        print(f"\nSTOPPET: {feil}", file=sys.stderr)
        return 1

    print("\n  målt:")
    for navn, verdi in sorted(verdier.items()):
        if "\n" not in verdi:
            print(f"    {navn:24} {verdi}")

    fremmede = si_fra_om_fremmede(args.mappe)
    if fremmede:
        print("\n  ligger i mappa og eies ikke av byggingen:")
        for navn in fremmede:
            print(f"    {navn}")

    print(f"\n  ferdig: {args.mappe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
