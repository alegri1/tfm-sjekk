"""Kommandolinjegrensesnitt.

    tfm-sjekk modell.ifc --master tfm-master.xlsx --ut rapport/

Exit-koder (§5): 0 = ingen feil, 1 = minst én feil. Advarsler og info
påvirker ikke exit-koden — verktøyet skal kunne stå som port i en
leveranseprosess uten å blokkere på anbefalinger.
"""

from __future__ import annotations

import atexit
import contextlib
import os
import sys
from pathlib import Path
from typing import Annotated

import typer

from tfm_sjekk.config import Konfigurasjon, OppsettFeil, finn_oppsett
from tfm_sjekk.ifc import les_modeller
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import alle_kontroller, kjor_alle
from tfm_sjekk.modell import Alvorlighet
from tfm_sjekk.oppsett import til_toml, utled
from tfm_sjekk.rapport import (
    normaliser_tidsstempel,
    skriv_bcf,
    skriv_csv,
    skriv_html,
    skriv_xlsx,
)
from tfm_sjekk.tabeller import les_kodetabell, les_master

app = typer.Typer(
    add_completion=False,
    help="Validerer TFM-merking i IFC-modeller mot NS 3457-serien og prosjektets TFM-master.",
)


@app.callback()
def _for_hver_kommando() -> None:
    """Kjøres før kommandoene under."""
    _tal_konsollens_kodeside()


def _tal_konsollens_kodeside() -> None:
    """Sørger for at utskrift aldri kan velte kjøringen.

    Windows-konsoller står ofte i cp1252, og «→» finnes ikke der. Uten dette
    kaster den avsluttende `typer.echo` UnicodeEncodeError *etter* at
    rapportene er skrevet, og prosessen ender på exit-kode 1 uansett hva
    kontrollene fant. Exit-koden er porten i leveranseprosessen (§5) — den
    skal aldri avhenge av kodesida i terminalen.

    `errors="replace"` er med som belte-og-bukseseler: en filsti eller en
    konfigurasjonsverdi kan inneholde tegn selv UTF-8-konsollen ikke tegner.
    """
    for strom in (sys.stdout, sys.stderr):
        rekonfigurer = getattr(strom, "reconfigure", None)
        if rekonfigurer is None:  # ombrutt strøm i test eller pipe
            continue
        with contextlib.suppress(OSError, ValueError):
            rekonfigurer(encoding="utf-8", errors="replace")


def _les_oppsett(
    config: Path | None, modeller: list[Path], til_stderr: bool = False
) -> Konfigurasjon:
    """Finner og leser konfigurasjonen, og sier hvilken fil det ble.

    Meldingslinja er ikke pynt. Automatisk oppslag betyr at en fil brukeren ikke
    visste om kan endre resultatet; uten en linje som sier hvilken, kan to
    kjøringer av samme kommando gi ulikt svar uten at noe forklarer hvorfor.
    Det er samme feil som en kontroll som hopper over i stillhet.

    `til_stderr` fordi «oppsett» skriver ren TOML til stdout. En diagnoselinje
    der ville gjort «tfm-sjekk oppsett modell.ifc > tfm-sjekk.toml» til en fil
    som ikke lar seg lese — og omdirigeringen er dokumentert i README.
    """
    valgt = config or finn_oppsett(modeller)
    if valgt is None:
        typer.echo("Oppsett: ingen funnet, bruker standardverdiene", err=til_stderr)
        return Konfigurasjon()

    typer.echo(f"Oppsett: {valgt}", err=til_stderr)
    try:
        return Konfigurasjon.les(valgt)
    except OppsettFeil as feil:
        # Samme utgang som en sti i oppsettet som peker feil: exit 2, og ingen
        # rapport. En nøkkel verktøyet ikke forsto ville ellers gitt en rapport
        # laget med andre regler enn brukeren ba om — og den ser like ren ut.
        raise typer.BadParameter(str(feil), param_hint="--config") from feil


def _fra_oppsett(flagg: Path | None, oppsett: Konfigurasjon, felt: str, hva: str) -> Path | None:
    """Flagget vinner over fila. En sti fra fila som ikke finnes er en feil.

    Uten den siste regelen ville en skrivefeil gitt «K7: hoppet over» — nøyaktig
    det samme som når du bevisst kjørte uten master. Brukeren ville trodd hun
    kjørte med, og fått en rapport uten K7-funn som ser ren ut.
    """
    if flagg is not None:
        return flagg
    løst = oppsett.sti(felt)
    if løst is None:
        return None
    if not løst.is_file():
        raw = getattr(oppsett, felt)
        raise typer.BadParameter(
            f"{hva} i oppsettet finnes ikke: «{raw}» → {løst}",
            param_hint=felt,
        )
    return løst


def _modellene(flagg: list[Path] | None, oppsett: Konfigurasjon) -> list[Path]:
    """Modellene kjøringen skal lese. Kommandolinjen vinner over oppsettet.

    Samme regel som for tabellene og mastera, og av samme grunn: den faste ruten
    er for den gjentatte kjøringen, og en enkeltfil skal kunne sjekkes uten å
    røre prosjektets oppsett.

    En oppføring uten treff er en feil. Ruten skrives én gang og leses aldri
    igjen; en eksport som havnet i feil mappe ville ellers gitt en tom, grønn
    rapport hver eneste runde, og ingenting i den ville sagt at den handlet om
    null objekter.

    Samme fil telles én gang. To mønstre som overlapper ville lest den to
    ganger, og K6 ville meldt hver eneste TFM-verdi som duplisert — en rapport
    som ser alvorlig ut og handler om oppsettet, ikke om modellen.
    """
    if flagg:
        return list(flagg)

    if not oppsett.modeller:
        raise typer.BadParameter(
            "ingen modell oppgitt. Oppgi IFC-filer på kommandolinjen, eller sett "
            "«modeller» i tfm-sjekk.toml.",
            param_hint="modeller",
        )

    funnet: list[Path] = []
    tomme: list[str] = []
    for rå, løst, treff in oppsett.stier("modeller"):
        if not treff:
            tomme.append(f"«{rå}» → {løst}")
            continue
        for fil in treff:
            if fil not in funnet:
                funnet.append(fil)

    if tomme:
        raise typer.BadParameter(
            "modeller i oppsettet finnes ikke: " + ", ".join(tomme),
            param_hint="modeller",
        )
    return funnet


@app.command()
def sjekk(
    modeller: Annotated[
        list[Path] | None,
        typer.Argument(
            help=(
                "Én eller flere IFC-filer. Flere filer federeres. "
                "Uten disse leses «modeller» fra oppsettet."
            ),
            exists=True,
        ),
    ] = None,
    ut: Annotated[
        Path | None,
        typer.Option(
            "--ut", help="Katalog for rapporter. Standard: «ut» i oppsettet, ellers «rapport»"
        ),
    ] = None,
    config: Annotated[
        Path | None, typer.Option("--config", help="tfm-sjekk.toml", exists=True)
    ] = None,
    systemtabell: Annotated[
        Path | None,
        typer.Option("--systemtabell", help="CSV med NS 3451 tabell 8 (din egen)", exists=True),
    ] = None,
    komponenttabell: Annotated[
        Path | None,
        typer.Option("--komponenttabell", help="CSV med NS 3457-8 (din egen)", exists=True),
    ] = None,
    master: Annotated[
        Path | None, typer.Option("--master", help="TFM-master, XLSX eller CSV", exists=True)
    ] = None,
    opprettet: Annotated[
        str | None,
        typer.Option(
            "--opprettet",
            help=(
                "ISO 8601-tidsstempel i BCF-fila, f.eks. 2026-01-01T12:00:00Z. "
                "Fast verdi gjør fila byte-identisk mellom kjøringer — bruk det "
                "når rapporten skal sammenlignes i CI. Uten flagget brukes klokka nå."
            ),
        ),
    ] = None,
    sekvensielt: Annotated[
        bool, typer.Option("--sekvensielt", help="Ikke les filene parallelt (feilsøking)")
    ] = False,
) -> None:
    """Kjører kontrollene K1–K9 på modellen(e)."""
    oppsett = _les_oppsett(config, list(modeller or []))
    modeller = _modellene(modeller, oppsett)
    ut = ut or oppsett.sti("ut") or Path("rapport")
    systemtabell = _fra_oppsett(systemtabell, oppsett, "systemtabell", "Systemtabellen")
    komponenttabell = _fra_oppsett(komponenttabell, oppsett, "komponenttabell", "Komponenttabellen")
    master = _fra_oppsett(master, oppsett, "tfm_master", "TFM-mastera")

    # Valideres før modellene leses: en skrivefeil her skal ikke koste en full
    # kjøring før den oppdages.
    try:
        opprettet = normaliser_tidsstempel(opprettet)
    except ValueError as feil:
        raise typer.BadParameter(str(feil), param_hint="--opprettet") from feil

    typer.echo(f"Leser {len(modeller)} modell(er)…")
    objekter = les_modeller(list(modeller), oppsett, parallelt=not sekvensielt)
    typer.echo(f"  {len(objekter)} objekter")

    kontekst = Kontekst.bygg(
        objekter,
        oppsett,
        systemtabell=les_kodetabell(systemtabell, "NS 3451 tabell 8") if systemtabell else None,
        komponenttabell=les_kodetabell(komponenttabell, "NS 3457-8") if komponenttabell else None,
        master=les_master(master, oppsett.master) if master else None,
    )

    funn, hoppet_over = kjor_alle(kontekst)
    dekning = kontekst.dekning()

    # Et unntak står på dekningslinja, ikke i en egen bolk lenger nede. Den som
    # leser dekningen leser den for å vite hva som ble sett på, og en fil som
    # mangler fra lista er verre enn en som står der med en forklaring.
    unntatt = set(kontekst.unntatte_filer())
    for fil, (i_omfang, lest) in dekning.items():
        if fil in unntatt:
            typer.echo(f"  {fil}: unntatt — kontrolleres ikke for TFM ({lest} objekter lest)")
            continue
        merke = "  <- ingenting kontrollert" if not i_omfang else ""
        typer.echo(f"  {fil}: {i_omfang} av {lest} objekter i omfanget{merke}")

    antall_feil = sum(1 for f in funn if f.alvorlighet is Alvorlighet.FEIL)
    antall_advarsler = sum(1 for f in funn if f.alvorlighet is Alvorlighet.ADVARSEL)

    for kontroll in hoppet_over:
        grunn = "ikke implementert ennå" if not kontroll.implementert else "hoppet over"
        typer.echo(f"  {kontroll.id}: {grunn}")

    tittel = ", ".join(m.name for m in modeller)
    skriv_html(
        funn,
        ut / "rapport.html",
        tittel,
        len(objekter),
        [k.id for k in hoppet_over],
        dekning,
    )
    skriv_csv(funn, ut / "funn.csv")
    skriv_xlsx(funn, ut / "funn.xlsx")
    skriv_bcf(funn, ut / "funn.bcfzip", opprettet)

    typer.echo(
        f"\n{antall_feil} feil, {antall_advarsler} advarsler → {ut}/rapport.html, {ut}/funn.bcfzip"
    )
    raise typer.Exit(code=1 if antall_feil else 0)


@app.command()
def kontroller() -> None:
    """Lister kontrollene og statusen deres."""
    for k in alle_kontroller():
        status = "" if k.implementert else "  (ikke implementert)"
        typer.echo(f"{k.id}  [{k.standard_alvorlighet.value:9}] {k.tittel}{status}")


@app.command()
def oppsett(
    modeller: Annotated[
        list[Path],
        typer.Argument(help="Én eller flere IFC-filer.", exists=True),
    ],
    ut: Annotated[
        Path | None,
        typer.Option("--ut", help="Skriv til fil i stedet for skjermen"),
    ] = None,
    config: Annotated[
        Path | None,
        typer.Option("--config", help="Oppsettet forslaget måles mot", exists=True),
    ] = None,
    overskriv: Annotated[
        bool, typer.Option("--overskriv", help="Tillat at --ut skriver over en fil som finnes")
    ] = False,
    sekvensielt: Annotated[
        bool, typer.Option("--sekvensielt", help="Ikke les filene parallelt (feilsøking)")
    ] = False,
) -> None:
    """Foreslår et tfm-sjekk.toml ut fra hvor verdiene faktisk lå.

    Kjører ingen kontroller, og trenger verken master eller kodetabeller. Dette
    er førstegangsmøtet med et prosjekt: du har en fagmodell og ingenting annet.
    """
    gjeldende = _les_oppsett(config, list(modeller), til_stderr=True)

    typer.echo(f"Leser {len(modeller)} modell(er)…", err=True)
    objekter = les_modeller(list(modeller), gjeldende, parallelt=not sekvensielt)
    kontekst = Kontekst.bygg(objekter, gjeldende)
    forslag = utled(kontekst)
    innhold = til_toml(forslag, gjeldende)

    if not forslag.har_noe():
        # Tomheten betyr to helt ulike ting, og de ser like ut. Se
        # `Oppsettforslag.fant_grunnlag`.
        if forslag.fant_grunnlag():
            typer.echo(
                f"Oppsettet dekker modellene som de er: alle "
                f"{forslag.med_tfm} TFM-verdier lå der det sa.",
                err=True,
            )
        else:
            typer.echo(
                f"Fant ingen TFM-verdier å utlede noe av. Leste "
                f"{forslag.lest} objekter i {len(forslag.kildefiler)} fagmodell(er).",
                err=True,
            )

    if ut is None:
        typer.echo(innhold)
        return

    # Fila forslaget er nærmest å hete er `tfm-sjekk.toml` — den samme fila
    # prosjektet allerede har lagt arbeid i.
    if ut.exists() and not overskriv:
        typer.echo(
            f"{ut} finnes fra før, og er ikke rørt. Kjør med --overskriv for å bytte den ut.",
            err=True,
        )
        raise typer.Exit(code=1)

    ut.parent.mkdir(parents=True, exist_ok=True)
    ut.write_text(innhold, encoding="utf-8")
    typer.echo(f"skrev {ut}", err=True)


BRUK_VED_DOBBELTKLIKK = """
tfm-sjekk validerer TFM-merking i IFC-modeller.

Verktøyet kjøres fra kommandolinja, men du kan også dra én eller flere
IFC-filer rett oppå denne fila i Utforskeren. Da legges rapportene i en
mappe som heter «rapport» ved siden av modellene.

Fra PowerShell, med kodetabellene dine:

    .\\tfm-sjekk.exe sjekk modell.ifc ^
        --systemtabell min-ns3451.csv ^
        --komponenttabell min-ns3457-8.csv ^
        --ut rapport

    .\\tfm-sjekk.exe --help        alle valg
    .\\tfm-sjekk.exe kontroller    hvilke kontroller som finnes
"""

KOMMANDOER = {"sjekk", "kontroller", "oppsett"}


def _med_standardkommando(argumenter: list[str]) -> list[str]:
    """Lar filstier stå først, uten «sjekk» foran.

    Det gjør at dra-og-slipp av IFC-filer oppå exe-en virker: Utforskeren
    sender filstiene som argumenter, og uten dette svarer Typer «No such
    command».

    «sjekk» settes bare inn når det første argumentet faktisk er en fil som
    finnes. En skrivefeil i kommandonavnet skal fortsatt gi «No such command
    'kontrolller'» og ikke den langt mer forvirrende «Path does not exist».
    """
    if not argumenter or argumenter[0].startswith("-") or argumenter[0] in KOMMANDOER:
        return argumenter
    if not Path(argumenter[0]).exists():
        return argumenter
    return ["sjekk", *argumenter]


def _med_rapportmappe(argumenter: list[str]) -> list[str]:
    """Legger rapportene ved siden av modellene ved dra-og-slipp.

    Standard `--ut` er «rapport» relativt til arbeidskatalogen, og den er
    exe-ens egen mappe når Utforskeren starter oss. Da ville rapportene havnet
    i nedlastingsmappa ved siden av programmet i stedet for hos modellen, og
    det er ikke der noen leter etter dem.

    Røres ikke når brukeren selv har oppgitt `--ut`.
    """
    if not argumenter or argumenter[0] != "sjekk" or "--ut" in argumenter:
        return argumenter
    modell = next((a for a in argumenter[1:] if not a.startswith("-")), None)
    if modell is None:
        return argumenter
    return [*argumenter, "--ut", str(Path(modell).resolve().parent / "rapport")]


def _startet_fra_utforsker() -> bool:
    """Sant når konsollvinduet ble laget for oss, altså ved dobbeltklikk.

    Windows gir en prosess startet fra Utforskeren sitt eget konsollvindu og
    lukker det i samme øyeblikk prosessen avslutter — utskriften rekker ikke å
    bli lest. Fra et skall som allerede har en konsoll skal ingenting pauses.

    Her sto det først en telling av prosessene på konsollen, med «alene = ble
    dobbeltklikket». Den var feil på to måter: PyInstaller i onefile-modus
    kjører en bootloader *og* selve programmet, så vi er aldri alene, og
    antallet avhenger dessuten av hvor mange ledd skallet består av — målt til
    seks i ett tilfelle. Derfor spør vi i stedet hvem som startet oss.

    Sett `TFM_SJEKK_KONSOLL_DEBUG=1` for å skrive ut kjeden av foreldre. Den
    finnes fordi dette bare kan reproduseres ved å faktisk dobbeltklikke, og
    da er en utskrift lettere å be om enn en feilsøkingsøkt.
    """
    if sys.platform != "win32":
        return False

    kjede = _foreldrekjede()
    if os.environ.get("TFM_SJEKK_KONSOLL_DEBUG"):
        print(f"[tfm-sjekk] foreldrekjede: {' <- '.join(kjede) or '(tom)'}", file=sys.stderr)

    eget = Path(sys.executable).name.lower()
    for navn in kjede:
        if navn == eget:
            continue  # PyInstaller-bootloaderen; samme fil som oss
        return navn == "explorer.exe"
    return False


def _foreldrekjede(maks: int = 6) -> list[str]:
    """Navnene på prosessene over oss, nærmeste først."""
    import ctypes
    import ctypes.wintypes as w

    class Oppforing(ctypes.Structure):
        _fields_ = [
            ("dwSize", w.DWORD),
            ("cntUsage", w.DWORD),
            ("th32ProcessID", w.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", w.DWORD),
            ("cntThreads", w.DWORD),
            ("th32ParentProcessID", w.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", w.DWORD),
            ("szExeFile", ctypes.c_wchar * 260),
        ]

    kjede: list[str] = []
    try:
        kernel = ctypes.windll.kernel32
        snapshot = kernel.CreateToolhelp32Snapshot(2, 0)  # TH32CS_SNAPPROCESS
        if snapshot == -1:
            return kjede
        try:
            oppforing = Oppforing()
            oppforing.dwSize = ctypes.sizeof(Oppforing)
            prosesser: dict[int, tuple[int, str]] = {}
            fant = kernel.Process32FirstW(snapshot, ctypes.byref(oppforing))
            while fant:
                prosesser[oppforing.th32ProcessID] = (
                    oppforing.th32ParentProcessID,
                    oppforing.szExeFile.lower(),
                )
                fant = kernel.Process32NextW(snapshot, ctypes.byref(oppforing))
        finally:
            kernel.CloseHandle(snapshot)

        pid = os.getpid()
        for _ in range(maks):
            oppslag = prosesser.get(pid)
            if oppslag is None:
                break
            pid = oppslag[0]
            forelder = prosesser.get(pid)
            if pid == 0 or forelder is None:
                break
            kjede.append(forelder[1])
    except Exception:
        return kjede
    return kjede


def _vent_pa_enter() -> None:
    with contextlib.suppress(Exception):  # stdin kan være lukket
        input("\nTrykk Enter for å lukke …")


def main() -> None:
    """Inngangspunkt for både konsollskriptet og PyInstaller-binæren."""
    fra_utforsker = _startet_fra_utforsker()

    if fra_utforsker:
        # Registreres før app() kjører, slik at pausen også gjelder når
        # kommandoen avslutter med typer.Exit — altså etter en vellykket
        # kjøring via dra-og-slipp.
        atexit.register(_vent_pa_enter)
        if len(sys.argv) == 1:
            _tal_konsollens_kodeside()
            typer.echo(BRUK_VED_DOBBELTKLIKK)
            return

    argumenter = _med_standardkommando(sys.argv[1:])
    if fra_utforsker:
        argumenter = _med_rapportmappe(argumenter)
    sys.argv[1:] = argumenter
    app()


if __name__ == "__main__":
    main()
