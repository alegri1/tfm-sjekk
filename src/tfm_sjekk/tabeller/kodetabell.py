"""Kodetabeller (NS 3451 tabell 8, NS 3457-8) lest fra brukerens egen CSV."""

from __future__ import annotations

import csv
from pathlib import Path

from pydantic import BaseModel

from tfm_sjekk.feil import FilFeil


class Kodetabell(BaseModel):
    """Kode → beskrivelse, med nok hierarkiforståelse til K4."""

    navn: str
    koder: dict[str, str] = {}

    def finnes(self, kode: str) -> bool:
        return kode in self.koder

    def beskrivelse(self, kode: str) -> str | None:
        return self.koder.get(kode)

    def barn(self, kode: str) -> list[str]:
        """Mer spesifikke koder under `kode`.

        NS 3451 er posisjonelt hierarkisk: 2 → 23 → 230 → 2310. En kode med
        etterfølgende nuller er et nivå over kodene som fyller ut de samme
        posisjonene. «2300 Ytterveggsystemer» har altså 2310/2320/2330 som
        barn — eksempelet PA 0805 selv bruker (§4, K4).

        Returnerer også barnebarn. For en advarsel er det godt nok: poenget
        er «det finnes noe mer spesifikt», ikke nøyaktig hvilket nivå.
        """
        prefiks = kode.rstrip("0")
        if not prefiks:
            # Koden er bare nuller — ville matchet hele tabellen.
            return []
        return sorted(
            k
            for k in self.koder
            if k != kode and k.startswith(prefiks) and k.rstrip("0") != prefiks
        )


def les_kodetabell(sti: Path, navn: str | None = None) -> Kodetabell:
    """Leser CSV med kolonnene ``kode`` og ``beskrivelse``.

    Aksepterer både komma og semikolon som skilletegn — norske Excel-eksporter
    bruker semikolon.
    """
    try:
        tekst = sti.read_text(encoding="utf-8-sig")
    except OSError as feil:
        raise FilFeil(sti, f"kunne ikke leses: {feil.strerror or feil}.") from feil

    linjer = tekst.splitlines()
    if not linjer:
        # Sto som `splitlines()[0]` og ga IndexError — en traceback fra en
        # tabellfil, med exit 1, som betyr at modellen er underkjent.
        raise FilFeil(sti, "er tom. Kodetabellen skal ha en overskriftsrad med «kode».")

    skilletegn = ";" if linjer[0].count(";") > linjer[0].count(",") else ","

    koder: dict[str, str] = {}
    leser = csv.DictReader(linjer, delimiter=skilletegn)
    if leser.fieldnames is None:
        raise FilFeil(sti, "er tom. Kodetabellen skal ha en overskriftsrad med «kode».")

    felt = {f.strip().lower(): f for f in leser.fieldnames}
    kode_felt = felt.get("kode")
    beskr_felt = felt.get("beskrivelse") or felt.get("navn")
    if kode_felt is None:
        # Meldingen var god fra før — den nådde bare aldri fram som en melding.
        raise FilFeil(
            sti,
            f"mangler kolonnen «kode». Fant {leser.fieldnames}. "
            f"Kodetabellen skal ha «kode» og gjerne «beskrivelse».",
        )

    for rad in leser:
        kode = (rad.get(kode_felt) or "").strip()
        if not kode:
            continue
        koder[kode] = (rad.get(beskr_felt) or "").strip() if beskr_felt else ""

    return Kodetabell(navn=navn or sti.stem, koder=koder)
