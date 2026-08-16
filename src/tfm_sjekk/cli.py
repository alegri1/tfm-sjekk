"""Kommandolinjegrensesnitt.

    tfm-sjekk modell.ifc --master tfm-master.xlsx --ut rapport/

Exit-koder (§5): 0 = ingen feil, 1 = minst én feil. Advarsler og info
påvirker ikke exit-koden — verktøyet skal kunne stå som port i en
leveranseprosess uten å blokkere på anbefalinger.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.ifc import les_modeller
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller import alle_kontroller, kjor_alle
from tfm_sjekk.modell import Alvorlighet
from tfm_sjekk.rapport import skriv_bcf, skriv_csv, skriv_html
from tfm_sjekk.tabeller import les_kodetabell, les_master

app = typer.Typer(
    add_completion=False,
    help="Validerer TFM-merking i IFC-modeller mot NS 3457-serien og prosjektets TFM-master.",
)


@app.command()
def sjekk(
    modeller: Annotated[
        list[Path],
        typer.Argument(help="Én eller flere IFC-filer. Flere filer federeres.", exists=True),
    ],
    ut: Annotated[Path, typer.Option("--ut", help="Katalog for rapporter")] = Path("rapport"),
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
    sekvensielt: Annotated[
        bool, typer.Option("--sekvensielt", help="Ikke les filene parallelt (feilsøking)")
    ] = False,
) -> None:
    """Kjører kontrollene K1–K9 på modellen(e)."""
    oppsett = Konfigurasjon.les(config)

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

    antall_feil = sum(1 for f in funn if f.alvorlighet is Alvorlighet.FEIL)
    antall_advarsler = sum(1 for f in funn if f.alvorlighet is Alvorlighet.ADVARSEL)

    for kontroll in hoppet_over:
        grunn = "ikke implementert ennå" if not kontroll.implementert else "hoppet over"
        typer.echo(f"  {kontroll.id}: {grunn}")

    tittel = ", ".join(m.name for m in modeller)
    skriv_html(funn, ut / "rapport.html", tittel, len(objekter), [k.id for k in hoppet_over])
    skriv_csv(funn, ut / "funn.csv")
    skriv_bcf(funn, ut / "funn.bcfzip")

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


if __name__ == "__main__":
    app()
