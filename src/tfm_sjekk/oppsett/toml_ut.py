"""Skriver et `Oppsettforslag` som TOML, med beviset i kommentarene.

Skrevet for hånd, uten TOML-bibliotek. Kommentarene bærer belegget hvert
forslag hviler på, og det er halve poenget med hele endringen: et forslag uten
bevis er en gjetning i ny innpakning. Ingen TOML-skriver for Python knytter
kommentarer til bestemte oppføringer uten at dokumentet først bygges som et
tre, og det som skal skrives her er få nok konstruksjoner til at det ikke
lønner seg — noen tabeller med lister av strenger.
"""

from __future__ import annotations

from tfm_sjekk.config import Konfigurasjon
from tfm_sjekk.modell import Kilde
from tfm_sjekk.oppsett.modell import Foreslatt, Oppsettforslag, Verditype

_HVORDAN: dict[Kilde, str] = {
    Kilde.GJENKJENT_FELT: "gjenkjent feltnavn i et egenskapssett som ikke er konfigurert",
    Kilde.GJETTET: "gjettet feltnavn i et konfigurert egenskapssett",
}


def _streng(verdi: str) -> str:
    """Siterer en TOML-streng.

    Verken pset-navn, feltnavn eller IFC-klassenavn kan i praksis inneholde et
    anførselstegn eller en omvendt skråstrek. En skriver som ikke escaper i det
    hele tatt er likevel en skriver som produserer ugyldig TOML den dagen den
    møter noe uventet, og da uten å si fra.
    """
    trygg = verdi.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{trygg}"'


def _antall(n: int, entall: str, flertall: str) -> str:
    return f"{n} {entall if n == 1 else flertall}"


def _liste(navn: str, konfigurerte: list[str], foreslatte: list[Foreslatt]) -> list[str]:
    """Én listeoppføring: konfigurerte verdier først, foreslåtte etter.

    Rekkefølgen i konfigurasjonen er forrangen verdiuttrekket bruker. Et
    forslag som satte en observert verdi først, ville gjøre en observasjon i én
    fagmodell til overstyring av prosjektets egen avtale i alle andre.
    """
    linjer = [f"{navn} = ["]
    for verdi in konfigurerte:
        linjer.append(f"    {_streng(verdi)},")
    for f in foreslatte:
        hvordan = _HVORDAN.get(f.kilde) if f.kilde else None
        merknad = _antall(f.antall, "objekt", "objekter")
        if hvordan:
            merknad += f", {hvordan}"
        linjer.append(f"    # {merknad}")
        linjer.append(f"    {_streng(f.verdi)},")
    linjer.append("]")
    return linjer


def til_toml(forslag: Oppsettforslag, config: Konfigurasjon | None = None) -> str:
    """Skriver forslaget som en `tfm-sjekk.toml`.

    `config` er konfigurasjonen forslaget er en delta mot — den som var i bruk
    under kjøringen. De konfigurerte verdiene må stå i fila sammen med de
    foreslåtte: TOML erstatter en liste i sin helhet, så en fil som bare inneholdt
    det nye ville slått av alt som virket fra før.
    """
    config = config or Konfigurasjon()
    linjer: list[str] = list(_topptekst(forslag))

    if not forslag.har_noe():
        return "\n".join(linjer) + "\n"

    # `ifc_klasser` er en toppnivånøkkel og MÅ stå før den første tabellen.
    # Står den etter «[pset]», leser TOML den som «pset.ifc_klasser», og
    # pydantic dropper den ukjente nøkkelen uten å si fra: fila er gyldig TOML
    # og gyldig konfigurasjon, og hele klasseforslaget forsvinner i stillhet.
    if forslag.klasser:
        merket = sum(f.antall for f in forslag.klasser)
        linjer += [
            "",
            f"# {_antall(merket, 'objekt', 'objekter')} utenfor omfanget har TFM-verdi.",
            "# Klassene under er derfor merket av noen som mente de skulle med.",
            "# Hele lista står her: TOML erstatter den, den utvider den ikke.",
        ]
        linjer += _liste("ifc_klasser", config.ifc_klasser, forslag.klasser)

    if forslag.psett or forslag.feltnavn:
        linjer += ["", "[pset]"]
        for verditype in Verditype:
            for attributt, hva, foreslatte in (
                (verditype.pset_attributt, "egenskapssett", forslag.psett.get(verditype, [])),
                (verditype.felt_attributt, "feltnavn", forslag.feltnavn.get(verditype, [])),
            ):
                if not foreslatte:
                    continue
                linjer.append("")
                linjer.append(f"# {verditype.omtale}: {hva}")
                linjer += _liste(attributt, getattr(config.pset, attributt), foreslatte)

    return "\n".join(linjer) + "\n"


def _topptekst(forslag: Oppsettforslag) -> list[str]:
    """Hva forslaget bygger på, og hva tomhet betyr når den inntreffer."""
    filer = _antall(len(forslag.kildefiler), "fagmodell", "fagmodeller")
    objekter = _antall(forslag.lest, "objekt", "objekter")
    linjer = [
        "# Forslag til tfm-sjekk.toml, utledet av tfm-sjekk.",
        f"# Bygger på {objekter} i {filer}, hvorav {forslag.med_tfm} har TFM-verdi.",
        "#",
        "# Dette er et utkast, ikke en beslutning. Verktøyet har gjettet seg fram til",
        "# noen av verdiene, og antallet over hver oppføring sier hvor mye som står",
        "# bak den. Les gjennom før du tar fila i bruk.",
    ]
    if forslag.har_noe():
        return linjer
    if forslag.fant_grunnlag():
        linjer.append("#")
        linjer.append("# Ingenting å foreslå: verdiene lå der oppsettet sa.")
    else:
        linjer.append("#")
        linjer.append("# Ingenting å bygge på: ingen av objektene hadde TFM-verdi.")
    return linjer
