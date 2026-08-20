"""Utleder et konfigurasjonsforslag fra en ferdig bygget `Kontekst`.

Ren funksjon, på samme form som en kontroll: `Kontekst -> Oppsettforslag`.
Det gir samme gevinst som for kontrollene — hele utledningen kan prøves med en
kontekst bygget i minnet, uten en eneste IFC-fil.

Utledningen er en avlesning, ikke en ny innsamling. `les_modell` leser TFM-verdier
for alle `IfcProduct`, ikke bare for dem som er i omfanget, og legger en
`Verdikilde` på hvert objekt for hver verdi den fant. Alt som trengs her ligger
altså allerede i konteksten.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations

from tfm_sjekk.config import Grammatikk, PsetOppsett
from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.modell import Kilde
from tfm_sjekk.oppsett.modell import (
    Foreslatt,
    ForeslattGrammatikk,
    Oppsettforslag,
    Verditype,
)
from tfm_sjekk.parser import ParseFeil, parse


def _konfigurert(pset: PsetOppsett, verditype: Verditype) -> tuple[list[str], list[str]]:
    """(konfigurerte egenskapssett, konfigurerte feltnavn) for én verditype."""
    return getattr(pset, verditype.pset_attributt), getattr(pset, verditype.felt_attributt)


def _sortert(teller: Counter[str], kilde: Kilde | None = None) -> list[Foreslatt]:
    """Foreslåtte verdier, sterkeste belegg først.

    Navnet brukes som annenprioritet, slik at to verdier med like mange
    objekter bak seg alltid kommer i samme rekkefølge. Uten det ville
    forslaget variere mellom kjøringer på samme modell.
    """
    return [
        Foreslatt(verdi=verdi, antall=antall, kilde=kilde)
        for verdi, antall in sorted(teller.items(), key=lambda p: (-p[1], p[0]))
    ]


def utled(kontekst: Kontekst) -> Oppsettforslag:
    """Utleder hva som mangler i konfigurasjonen, av det modellene viste.

    Deltaen måles mot `kontekst.config`, ikke mot standardverdiene. Kjøres
    kommandoen uten `--config` er de to det samme; kjøres den med, er forslaget
    det som mangler i *den* fila. Det er også dette som gjør at et forslag brukt
    som konfigurasjon gir et tomt forslag neste gang.
    """
    psett: dict[Verditype, list[Foreslatt]] = {}
    feltnavn: dict[Verditype, list[Foreslatt]] = {}

    for verditype in Verditype:
        konf_psett, konf_felt = _konfigurert(kontekst.config.pset, verditype)
        manglende_psett: Counter[str] = Counter()
        manglende_felt: Counter[str] = Counter()

        for objekt in kontekst.objekter:
            kilde = objekt.kilder.get(verditype.value)
            if kilde is None:
                continue

            # KONFIGURERT: verdien lå der oppsettet sa. Ingenting å foreslå.
            #
            # FORKASTET: verktøyet avviste verdien fordi den ikke var
            # gjenkjennelig som det feltet skal inneholde. En forkastelse er
            # bevis for at verdien *ikke* hører hjemme der — foreslo vi feltet,
            # ville en riktig avvisning bli varig konfigurasjon, og verktøyet
            # ville deretter lese fabrikatnavn som TFM-ID-er uten å si fra.
            if kilde.kilde is Kilde.GJENKJENT_FELT and kilde.pset not in konf_psett:
                manglende_psett[kilde.pset] += 1
            elif kilde.kilde is Kilde.GJETTET and kilde.felt not in konf_felt:
                manglende_felt[kilde.felt] += 1

        if manglende_psett:
            psett[verditype] = _sortert(manglende_psett, Kilde.GJENKJENT_FELT)
        if manglende_felt:
            feltnavn[verditype] = _sortert(manglende_felt, Kilde.GJETTET)

    return Oppsettforslag(
        psett=psett,
        feltnavn=feltnavn,
        klasser=_klasser_utenfor_omfanget(kontekst),
        grammatikk=_grammatikkforslag(kontekst),
        lest=len(kontekst.objekter),
        med_tfm=sum(1 for o in kontekst.objekter if o.tfm_forekomst),
        kildefiler=list(kontekst.kildefiler),
    )


def _klasser_utenfor_omfanget(kontekst: Kontekst) -> list[Foreslatt]:
    """Klasser som har TFM-merkede objekter, men ligger utenfor omfanget.

    At en klasse finnes i fila er ikke bevis for at den hører hjemme i omfanget
    — en arkitektmodell er full av vegger ingen skal merke. At objektene *er*
    merket, er det: noen har ment at de skulle ha TFM.

    Den konkrete klassen foreslås, ikke en supertype. Verktøyet vet at
    `IfcBuildingElementProxy` er merket; det vet ikke at hele
    `IfcBuildingElement` skal inn i omfanget.
    """
    omfang = kontekst.config.ifc_klasser
    teller: Counter[str] = Counter()

    for objekt in kontekst.objekter:
        if not objekt.tfm_forekomst:
            continue
        if any(objekt.er_av_type(klasse) for klasse in omfang):
            continue
        teller[objekt.ifc_klasse] += 1

    return _sortert(teller)


# Delene som kan gjøres valgfrie, og bryteren som gjør det. Sifferantall og
# andre formkrav står bevisst ikke her: å gjøre en del valgfri sier hvilken fase
# modellen er i, mens et endret sifferantall sier hva standarden er — og en
# systematisk feilmerking ville da blitt velsignet som konfigurasjon og aldri
# meldt igjen.
KANDIDATER = ("krev_plassering", "krev_komponenttype")


def _grammatikkforslag(kontekst: Kontekst) -> list[ForeslattGrammatikk]:
    """Det minste settet innstillinger som får hver feilende verdi til å parse.

    Settet prøves, det gjettes ikke: grammatikken bygges på nytt med
    innstillingene slått av, og hver verdi som feiler forsøkes parset igjen.

    Alternativet — å sammenligne feilmeldingene og se om de er like — ville
    bygget beslutningen på norsk brukertekst som skal kunne omformuleres uten at
    oppførselen endres. Prøven her spør dessuten om nøyaktig det vi vil vite,
    «løser dette settet problemet?», framfor et stedfortredende spørsmål om
    hvorfor det oppsto.

    Settene prøves fra minst til størst, så ingen innstilling blir med uten å
    trengs. Kravet er at *alle* verdier går igjennom: et sett som løser noen av
    feilene peker på merkefeil, ikke på fase.

    Første utkast prøvde kandidatene hver for seg. Da fikk en modell som manglet
    både plassering og komponenttype ingen anvisning i det hele tatt — den
    tidligste modellen av alle, og nettopp den dette er laget for.
    """
    feilende = [
        objekt.tfm_forekomst
        for objekt in kontekst.objekter
        if objekt.global_id in kontekst.parsefeil and objekt.tfm_forekomst
    ]
    if not feilende:
        return []

    gjeldende = kontekst.config.grammatikk
    # Er en bryter allerede av, er det ingenting å foreslå — samme regel som for
    # egenskapssett og feltnavn, og det som gjør at et forslag brukt om igjen
    # blir tomt.
    mulige = [k for k in KANDIDATER if getattr(gjeldende, k)]

    for storrelse in range(1, len(mulige) + 1):
        for sett in combinations(mulige, storrelse):
            kandidat = gjeldende.model_copy(update=dict.fromkeys(sett, False))
            if not all(_parser(verdi, kandidat) for verdi in feilende):
                continue
            return [
                ForeslattGrammatikk(
                    innstilling=innstilling,
                    verdi=False,
                    loser=len(feilende),
                    parser_alt=len(kontekst.parsede),
                )
                for innstilling in sett
            ]
    return []


def _parser(verdi: str, g: Grammatikk) -> bool:
    try:
        parse(verdi, g)
    except ParseFeil:
        return False
    return True
