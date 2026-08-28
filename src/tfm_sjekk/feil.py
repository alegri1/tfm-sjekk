"""Feil som betyr at kjøringen ikke kunne gjennomføres.

Ved siden av `OppsettFeil` i config.py, og av samme grunn: begge betyr at
verktøyet ikke kom fram til et svar, ikke at modellen er underkjent. Cli-en
gjør dem til exit 2 — den samme koden som en sti som peker feil — framfor exit
1, som er porten i leveranseprosessen (§5).

EGEN MODUL, IKKE I `ifc/`. Feilen begynte der, sammen med IFC-lesingen. Men
`tabeller/` trenger den også, og en import derfra til `tfm_sjekk.ifc` ville
dratt ifcopenshell inn i en modul som leser CSV — mot regelen om at `ifc/` er
eneste sted som vet om det biblioteket. Her er den fri for avhengigheter.
"""

from __future__ import annotations

from pathlib import Path


class FilFeil(Exception):
    """En fil verktøyet skulle lese eller skrive, og ikke kunne.

    Én type for alle tre — modeller, kodetabeller og rapporter — fordi cli-en
    har nøyaktig én utgang for dem. Tre typer med samme håndtering ville vært
    tre steder å glemme én.

    `__reduce__` er ikke pynt. Unntaket krysser prosessgrensen fra en arbeider
    i federeringen, og standard oppførsel ville kalt `FilFeil(meldingen)` med
    ett argument ved utpakking — altså en TypeError i stedet for feilen den
    skulle bære. Det er den slags som virker sekvensielt og ryker i pool-en.
    """

    def __init__(self, sti: Path | str, forklaring: str) -> None:
        self.sti = Path(sti)
        self.forklaring = forklaring
        super().__init__(f"«{self.sti.name}» {forklaring}")

    def __reduce__(self):
        return (FilFeil, (self.sti, self.forklaring))
