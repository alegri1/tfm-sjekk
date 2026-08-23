# -*- coding: utf-8 -*-
"""Leser funn.csv og gir én avvikstekst per Revit-element, til bruk i Dynamo.

Bakgrunn: fra §11-samtalen ba en RIE om «skriving tilbake til Revit, får
schedule som man kan gå gjennom og fikse feilene fortløpende». Funnet er ikke
leveransen — rettingen er det, og den skjer i Revit.

BRUK I DYNAMO

    File Path ───────────────────────────────> IN[0]  sti til funn.csv
    Element.GetParameterValueByName(TFM) ────> IN[1]  TFM-verdien per element

    Elementene selv skal ikke inn hit. Send dem rett til
    Element.SetParameterByName sammen med OUT[0].

    OUT[0] er en liste like lang som IN[1]: avvikstekst der det finnes funn,
    tom streng ellers. Bruk en tekstparameter, f.eks. «TFM_Avvik», og lag en
    schedule som filtrerer på at den ikke er tom.

    OUT[1] er tallene. Les dem — en kobling som treffer null elementer ser
    nøyaktig ut som en modell uten avvik.

HVORFOR MATCHE PÅ TFM-VERDIEN OG IKKE PÅ GUID

Funnene bærer IFC-ens GlobalId, men den er ikke Revits UniqueId. Revits
IFC-eksportør utleder GlobalId av UniqueId på en måte som avhenger av
eksportinnstillinger, og et sammenlikningsgrunnlag som stille gir null treff er
verre enn ingen kobling i det hele tatt.

TFM-verdien har derimot begge sider garantert: den står i Revit-parameteren og
i IFC-fila, og den er nettopp det brukeren skal rette. Prisen er at objekter
uten TFM-verdi ikke kan kobles — men de trenger heller ingen kobling: i Revit
finner du dem ved å filtrere på tom TFM-parameter.

Har modellen en «IfcGUID»-parameter fra eksporten, kan du sende den som IN[1]
i stedet. Da matches det på GlobalId, og også K1-funnene treffer.

Skrevet for både IronPython 2.7 og CPython3, som er de to Dynamo kjører.
"""

# Uten denne er "..." bytes i Python 2, og alt under knekker på første «».
# I Python 3 er den et null-tiltak.
from __future__ import unicode_literals

import csv
import io

# --- Ren logikk. Ingen Revit-avhengighet, slik at den kan prøves utenfor Dynamo. ---

SKILLETEGN = ";"
BOM = "﻿"
MAKS_PER_ELEMENT = 5

PY2 = str is bytes


def les_funn(tekst):
    """Leser innholdet i funn.csv til en liste med ordbøker.

    Fila er semikolonseparert UTF-8 med BOM. BOM-en må vekk før parsing, ellers
    heter den første kolonnen «﻿kontroll» og oppslag på «kontroll» feiler
    uten at noe krasjer — den slags feil er stille og dyr.
    """
    if tekst[:1] == BOM:
        tekst = tekst[1:]
    linjer = tekst.splitlines()

    if PY2:
        # csv-modulen i Python 2 tar bytes, ikke unicode. Meldingene her er
        # fulle av «» og æøå, og uten denne omveien får du UnicodeEncodeError
        # på første rad — inne i Dynamo, der stakksporet er vondt å lese.
        # Skilletegnet må også være bytes; Python 2 godtar ikke unicode der.
        rader = csv.DictReader(
            [linje.encode("utf-8") for linje in linjer],
            delimiter=SKILLETEGN.encode("utf-8"),
        )
        return [
            dict(
                (navn.decode("utf-8"), (verdi or b"").decode("utf-8"))
                for navn, verdi in rad.items()
                if navn is not None
            )
            for rad in rader
        ]

    return list(csv.DictReader(linjer, delimiter=SKILLETEGN))


def les_fil(sti):
    """Leser funn.csv fra disk, i den kodingen verktøyet skriver den med."""
    with io.open(sti, "r", encoding="utf-8-sig") as f:
        return les_funn(f.read())


def ligner_tfm(verdi):
    """Grovsortering: er dette en TFM-ID, eller noe annet funnet handlet om?

    «verdi»-kolonnen er verdien *funnet* gjelder, ikke nødvendigvis elementets
    TFM-ID. K9 legger for eksempel MMI-verdien der, og «200» er ingen nøkkel å
    koble på. To av tre strukturmarkører er nok — samme terskel verktøyet selv
    bruker.
    """
    if not verdi:
        return False
    return sum(1 for m in ("++", "=", "-") if m in verdi) >= 2


def har_tfm_kolonne(funn):
    """Om rapporten har «tfm»-kolonnen, som alltid er elementets egen TFM-ID."""
    return bool(funn) and "tfm" in funn[0]


def tfm_per_element(funn):
    """Elementets egen TFM-ID, per global_id.

    Er «tfm»-kolonnen der, leses den rett fram. Den er garantert å være
    elementets egen verdi uansett hva funnet handler om.

    Er den ikke det — en rapport fra før kolonnen fantes — utledes nøkkelen av
    søskenrader med samme global_id: har elementet både et K2-funn (der «verdi»
    er TFM-ID-en) og et K9-funn (der den er MMI), gir K2-raden nøkkelen begge
    trenger. Det virker for de fleste, men ikke for et element som BARE har et
    K9-funn — da finnes ingen søskenrad, og funnet faller ut i stillhet.
    """
    ut = {}
    fra_kolonne = har_tfm_kolonne(funn)
    for rad in funn:
        gid = (rad.get("global_id") or "").strip()
        if not gid:
            continue
        if fra_kolonne:
            verdi = (rad.get("tfm") or "").strip()
            if verdi:
                ut[gid] = verdi
        else:
            verdi = (rad.get("verdi") or "").strip()
            if ligner_tfm(verdi):
                ut[gid] = verdi
    return ut


def grupper(funn, nokkel="verdi"):
    """Funn gruppert på TFM-ID-en elementet skal matches med.

    Funn uten nøkkel hoppes over. De hører til objekter uten TFM, og de finnes
    i Revit ved å filtrere på tom parameter — ikke ved å kobles her.
    """
    etter_gid = tfm_per_element(funn)
    ut = {}
    for rad in funn:
        gid = (rad.get("global_id") or "").strip()
        # Elementets egen TFM har forrang: den er den samme for alle rader som
        # deler global_id, og den er riktig også når funnet handler om noe annet.
        verdi = etter_gid.get(gid, "")
        if not verdi:
            kandidat = (rad.get(nokkel) or "").strip()
            verdi = kandidat if ligner_tfm(kandidat) else ""
        if not verdi:
            continue
        ut.setdefault(verdi, []).append(rad)
    return ut


def sammendrag(rader):
    """Én linje per funn, kortet ned hvis det er mange.

    Formen er «K2 feil: meldingen», slik at kontrollnummeret er det første
    øyet møter i en schedule-kolonne.
    """
    if not rader:
        return ""
    linjer = []
    for rad in rader[:MAKS_PER_ELEMENT]:
        linjer.append(
            "{0} {1}: {2}".format(
                rad.get("kontroll", "?"),
                rad.get("alvorlighet", "?"),
                (rad.get("melding") or "").strip(),
            )
        )
    resten = len(rader) - MAKS_PER_ELEMENT
    if resten > 0:
        linjer.append("… og {0} til".format(resten))
    return "\n".join(linjer)


def avvikstekster(funn, verdier):
    """Én tekst per element, i samme rekkefølge som `verdier`.

    `verdier` er TFM-verdien Dynamo leste av hvert element. Tom streng der
    elementet ikke har funn — Revit skriver da en tom parameter, og schedulen
    filtrerer dem bort.
    """
    etter_verdi = grupper(funn)
    ut = []
    for verdi in verdier:
        nokkel = (verdi or "").strip() if verdi is not None else ""
        ut.append(sammendrag(etter_verdi.get(nokkel, [])))
    return ut


def statistikk(funn, verdier):
    """Tall til å se om koblingen traff, framfor å tro at den gjorde det.

    En kobling som gir null treff ser i Dynamo ut som «ingen avvik». Uten disse
    tallene er de to umulige å skille, og det er samme feil som «ingen funn»
    kontra «ingenting sjekket».
    """
    etter_verdi = grupper(funn)
    lest = [(v or "").strip() for v in verdier if v]
    truffet = [v for v in lest if v in etter_verdi]
    ukoblede_funn = [n for n in etter_verdi if n not in set(lest)]
    ukoblede = len(funn) - sum(len(v) for v in etter_verdi.values())
    return {
        "funn_i_fila": len(funn),
        "nokkel_fra": "tfm-kolonnen" if har_tfm_kolonne(funn) else "utledet av søskenrader",
        "funn_uten_nokkel": ukoblede,
        "elementer": len(verdier),
        "elementer_med_tfm": len(lest),
        "elementer_med_avvik": len(truffet),
        "tfm_verdier_med_funn": len(etter_verdi),
        "tfm_verdier_uten_element": sorted(ukoblede_funn),
    }


# --- Dynamo-skallet. Kjøres bare inne i Dynamo. ---

# Ingen sjekk på __name__. Dynamo eksekverer noden, og hva __name__ settes til
# varierer mellom IronPython- og CPython-motoren — er den ikke «__main__», ville
# blokka aldri kjørt og Dynamo meldt at OUT ikke finnes. At «IN» er der, er det
# eneste sikre tegnet på at vi er i Dynamo. Ved import fra en test finnes den
# ikke, og blokka hoppes over.
if "IN" in globals():  # pragma: no cover - krever Dynamo
    _sti = IN[0]  # noqa: F821
    _verdier = IN[1]  # noqa: F821

    _funn = les_fil(_sti)

    # Liste, ikke tuppel: Dynamo har bare én utgangsport, så de to
    # tingene pakkes sammen og skilles av en Code Block med «x[0];» og
    # «x[1];» på hver sin linje.
    # Indeks 0 er tekstene, indeks 1 er tallene — les tallene.
    OUT = [avvikstekster(_funn, _verdier), statistikk(_funn, _verdier)]
