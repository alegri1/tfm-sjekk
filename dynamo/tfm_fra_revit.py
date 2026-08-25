# -*- coding: utf-8 -*-
"""Bygger TFM-ID-er av det Revit-modellen allerede vet, til bruk i Dynamo.

Motstykket til tfm_til_revit.py. Den skriver funn tilbake til modellen; denne
skriver merkingen inn i utgangspunktet, slik at det finnes noe å kontrollere.

Bakgrunnen er praktisk. En umerket modell gir K1 på hvert eneste objekt, og en
rapport der alt er feil sier ingenting om noe. Samtidig ligger halve TFM-ID-en
allerede i modellen: familien sier hva objektet er, og kursnummeret sier hvilken
kurs det henger på. Det som mangler er formatet.

BRUK I DYNAMO

    Element.ElementType
        → GetParameterValueByName("Family Name") ──────> IN[0]  familienavn
    Element.GetParameterValueByName("Circuit Number") ─> IN[1]  kursnumre
    Code Block  "115080";  ───────────────────────────> IN[2]  plassering
                (prosjektets egen kode — grafen leveres med en plassholder)
    Element.ElementType → Element.Name ───────────────> IN[3]  typenavn, valgfri

    «Family Name» er en innebygd parameter på typen, og den virker på begge
    slags familier Revit har. FamilyType.Family gir null på systemfamilier —
    kabelrør, kabelbroer, kanaler — og Element.Name gir typenavnet, som er
    materialet framfor funksjonen: «Electrical Metallic Tubing (EMT)».

    IN[3] brukes bare der IN[0] er tom. Med «Family Name» fyrte den aldri på
    Snowdon Towers, men den koster ingenting og sier fra i sammendraget.

    Elementene selv skal ikke inn hit. Send dem rett til
    Element.SetParameterByName sammen med OUT[0].

    OUT[0] er en liste like lang som IN[0]: TFM-ID-en per element.
    OUT[1] er tallene. Les dem før du stoler på resultatet.

    Parameteren du skriver til må være Tekst og Instance, og den må hete det
    kartleggingsfila revit/TFM-egenskapssett.txt peker på — ellers kommer
    verdiene aldri ut i IFC-eksporten.

DENNE LEGGER IKKE INN FEIL MED VILJE

verktoy/legg_til_tfm.py gjør det, fordi den bygger en testfikstur av en fil.
Denne skriver inn i en ekte Revit-modell, og en modell er ikke en fikstur. Det
trengs heller ikke: en ekte modell har sine egne hull. Kjørt i Revit 2027 og
eksportert til IFC ga Snowdon Towers 177 funn, alle K8 om objekter uten
kursnummer — og ingen av dem var lagt inn av noen.

HVORFOR KURSNUMMERET KOMMER FRA REVIT OG IKKE FRA IFC

Kursen er det eneste leddet i TFM-ID-en som ikke kan utledes av objektet selv.
I IFC leses den av navnet på IfcSystem — men det navnet er nettopp Revits eget
«Circuit Number», skrevet ut ved eksport. Her leses den fra kilden i stedet for
fra avtrykket.

Det er også den ene retningen som virker. Kurser overlever eksporten ut av
Revit, men ikke importen inn igjen: et objekt som har vært innom en IFC-import
er en Generic Model uten kurs. Derfor merkes modellen der kursene finnes.

Skrevet for både IronPython 2.7 og CPython3, som er de to Dynamo kjører.
"""

# Uten denne er "..." bytes i Python 2, og alt under knekker på første «».
# I Python 3 er den et null-tiltak.
from __future__ import unicode_literals

# --- Ren logikk. Ingen Revit-avhengighet, slik at den kan prøves utenfor Dynamo. ---

PY2 = str is bytes

# Familienavn -> (systemkode, komponentkode).
#
# KODENE ER FUNNET PÅ. De er valgt så de ser plausible ut i en rapport, og de er
# konsistente med hverandre — ikke mer. NS 3451 og NS 3457-serien er betalte
# standarder, og innholdet skal aldri inn i dette repoet (§8). Skal tabellen
# brukes på et ekte prosjekt, er det prosjektets egne koder som hører hjemme her.
#
# Tabellen er den samme som i verktoy/legg_til_tfm.py, og de to skal ikke kunne
# drive fra hverandre: tests/test_merking.py sammenlikner dem.
#
# Treff skjer på begynnelsen av familienavnet, slik at «Downlight 150mm» og
# «Downlight 200mm» faller på samme kode, og «Meter» dekker både «Meter Bank» og
# «Meter Main». En nøkkel som er begynnelsen på en annen ville skygget for den;
# tests/test_merking.py passer på at ingen gjør det.
#
# Familienavnene er Autodesks, fra Snowdon Towers. En norsk modell har andre —
# det er FAMILIER du endrer da, ikke koden under.
FAMILIER = [
    # Fordelinger, inntak og vern — det kursene går ut fra
    ("Lighting and Appliance Panelboard", ("4310", "QLF")),
    ("PV Panelboard", ("4310", "QLF")),
    ("Switchboard", ("4310", "QLF")),
    ("Meter", ("4310", "QLM")),
    ("Disconnect Switch", ("4310", "QLA")),
    ("Dry Type Transformer", ("4310", "QLT")),
    ("Electrical Equipment", ("4310", "QLT")),
    # Lys
    ("Pendant-Dome", ("4320", "QLF")),
    ("Pendant Lamp", ("4320", "QLF")),
    ("Pendant Light", ("4320", "QLF")),
    ("Recessed Lamp", ("4320", "QLF")),
    ("Wall Lamp", ("4320", "QLF")),
    ("Downlight", ("4320", "QLF")),
    ("Ceiling Light", ("4320", "QLF")),
    ("Bollard Light", ("4320", "QLF")),
    ("Sconce Light", ("4320", "QLF")),
    ("Lighting-Exterior", ("4320", "QLF")),
    ("Lighting Switches", ("4320", "QLB")),
    # Uttak og tilkoblet utstyr
    ("Duplex Receptacle", ("4330", "QLS")),
    ("Quadruplex Receptacle", ("4330", "QLS")),
    ("High Voltage Receptacle", ("4330", "QLS")),
    ("Weather Proof Receptacle", ("4330", "QLS")),
    ("Electrical Fixtures", ("4330", "QLS")),
    ("Hand Dryer", ("4330", "QLU")),
    # Lokal produksjon
    ("PV Battery", ("4350", "QLP")),
    ("PV Inverter", ("4350", "QLP")),
    # Føringsveier — bærer kurser og ligger ikke på en (se K8)
    ("Conduit", ("4360", "QLK")),
    ("Wiring Pull Box", ("4360", "QLK")),
    # Tele og data
    ("Data Outlet", ("5300", "QTD")),
    # --- VVS ---
    #
    # Navnene er lest ut av Snowdon Towers' egne HVAC- og Plumbing-eksporter,
    # ikke gjettet. En gjettet rad treffer ingenting, og da faller objektet til
    # STANDARD — som er en ELEKTRO-kode. Et VVS-objekt merket 4390 er verre enn
    # et umerket: det ser riktig ut.
    #
    # Luftbehandling: kanaler og deler
    ("Round Duct", ("3600", "JVZ")),
    ("Rectangular Duct", ("3600", "JVZ")),
    ("Flex Duct", ("3600", "JVZ")),
    ("Round Elbow", ("3600", "JVZ")),
    ("Round Endcap", ("3600", "JVZ")),
    ("Round Tee", ("3600", "JVZ")),
    ("Round Transition", ("3600", "JVZ")),
    ("Rectangular to Round Transition", ("3600", "JVZ")),
    ("Rectangular Elbow", ("3600", "JVZ")),
    ("Rectangular Endcap", ("3600", "JVZ")),
    ("Rectangular Tee", ("3600", "JVZ")),
    # Luftbehandling: rister, ventiler og aggregat
    ("Supply Grille", ("3600", "JVT")),
    ("Return Grille", ("3600", "JVT")),
    ("Supply Diffuser", ("3600", "JVT")),
    ("Air Terminal-Supply Cap", ("3600", "JVT")),
    ("Air Terminal-Exhaust Cap", ("3600", "JVT")),
    ("HeatRecoveryUnit", ("3600", "JVA")),
    # Sanitær: rør og deler
    ("Pipe Types", ("3100", "JSR")),
    ("Elbow - Generic", ("3100", "JSR")),
    ("Bend - PVC", ("3100", "JSR")),
    ("Tee - Generic", ("3100", "JSR")),
    ("Tee Sanitary", ("3100", "JSR")),
    ("Transition - Generic", ("3100", "JSR")),
    ("Reducer - PVC", ("3100", "JSR")),
    ("Plug - PVC", ("3100", "JSR")),
    ("Cap - Generic", ("3100", "JSR")),
    # Sanitær: ventiler og måling
    ("Ball Valve", ("3100", "JSV")),
    ("Gate Valve", ("3100", "JSV")),
    ("Pressure Regulating Valve", ("3100", "JSV")),
    ("Water Meter Unit", ("3100", "JSV")),
    # Sanitær: utstyr. «Sink» dekker ogsaa SinkConnection
    ("Sink", ("3100", "JSU")),
    ("Hand Sink", ("3100", "JSU")),
    ("Mop Sink", ("3100", "JSU")),
    ("MopSink", ("3100", "JSU")),
    ("Toilet", ("3100", "JSU")),
    ("WaterClosetConnection", ("3100", "JSU")),
    ("Shower", ("3100", "JSU")),
    ("Urinal", ("3100", "JSU")),
    ("WasherConnection", ("3100", "JSU")),
    ("Hose Bib", ("3100", "JSU")),
    ("Water Heater", ("3100", "JSA")),
    # Sanitær: sluk, avløp og lufting
    ("Floor Drain", ("3100", "JSS")),
    ("Roof Drain", ("3100", "JSS")),
    ("Plumb_Floor Sink", ("3100", "JSS")),
    ("Air Terminal-Vent Cap", ("3100", "JSS")),
]
STANDARD = ("4390", "QLX")

# Undernummeret er to siffer. «00» betyr «ligger ikke på noen kurs» — det er en
# ekte opplysning, ikke en manglende: tavler og føringsveier har den med rette,
# og et uttak har det ikke.
UTEN_KURS = "00"


def familiekode(navn):
    """(systemkode, komponentkode) for et familienavn.

    Ukjente familier får STANDARD framfor å bli hoppet over. Et objekt uten TFM
    gir K1, og da ser modellen umerket ut der den egentlig bare er ukjent for
    denne tabellen. En kode verktøyet kan avvise er mer opplysende enn ingenting.
    """
    familie = (navn or "").split(":")[0].strip()
    for nøkkel, koder in FAMILIER:
        if familie.startswith(nøkkel):
            return koder
    return STANDARD


def kursnummer(rå):
    """Revits «Circuit Number» til to siffer.

    Revit skriver kursnummeret som fritekst, og et objekt kan ligge på flere:
    «6,8» betyr kurs 6 og kurs 8. TFM har plass til én, så den første brukes.
    Det er en forenkling, og den er verdt å vite om — men tallet er ekte, og
    det er mer enn et oppdiktet tall er.

    Alt som ikke inneholder et siffer regnes som «ingen kurs».
    """
    første = (rå or "").split(",")[0]
    sifre = "".join(c for c in første if c.isdigit())
    if not sifre:
        return UTEN_KURS
    return sifre.zfill(2)[:2]


# Verdien Code Block-noden i den ferdige grafen står med. Grafen kan ikke levere
# et brukbart resultat før noen har byttet den ut, og det skal den si fra om.
PLASSHOLDER = "SETT-PLASSERING"


# Komponentens løpenummer er tre siffer. Er bøtta full, går det videre i
# systemets løpenummer — det er der formatet er ment å gå.
MAKS_LOPENUMMER = 999


def tfm_id(plassering, systemkode, kurs, komponentkode, løpenummer, system_lopenummer=1):
    """Setter sammen ID-en slik grammatikken krever den."""
    return "++{0}={1}.{2:03d}.{3}-{4}{5:03d}".format(
        plassering, systemkode, system_lopenummer, kurs, komponentkode, løpenummer
    )


def tekst(verdi):
    """Det Dynamo sender inn, som en streng verktøyet kan regne med.

    Revit gir null for en parameter som ikke er satt, og Dynamo sender den
    videre som None. Uten dette ville «Circuit Number» på et ukoblet objekt
    blitt strengen «None» — som inneholder ingen siffer, og dermed hadde
    oppført seg riktig ved en ren tilfeldighet.

    Noen noder gir et Revit-objekt framfor en streng. str() på det gir noe
    ubrukelig, men ikke et krasj — og da sier statistikken fra, framfor at
    grafen stopper med en meldingen ingen forstår.
    """
    if verdi is None:
        return ""
    if isinstance(verdi, bytes):
        return verdi.decode("utf-8")
    if PY2 and isinstance(verdi, str):
        return verdi.decode("utf-8")
    return verdi if isinstance(verdi, type("")) else "{0}".format(verdi)


def navnet(familienavn, reservenavn, i):
    """Familienavnet, eller typenavnet der Revit ikke har noe familienavn.

    Revit har to slags familier. En lastet familie (en armatur, et uttak) har et
    familienavn, og FamilyType.Family gir det. En systemfamilie — kabelrør,
    kabelbroer, kanaler — har ikke det: den er bygget inn i Revit, og
    FamilyType.Family gir null med advarselen «Asked to convert non-convertible
    types». Da er typenavnet det som identifiserer den.

    Det er derfor IN[3] finnes. Uten den falt alle kabelrørene til
    standardkoden, og en modell med 850 rør så ut til å være 850 ukjente
    familier.
    """
    navn = familienavn[i]
    if navn:
        return navn, False
    if reservenavn and i < len(reservenavn) and reservenavn[i]:
        return reservenavn[i], True
    return "", False


def merk(familienavn, kursnumre, plassering, reservenavn=None):
    """TFM-ID per element, i samme rekkefølge som inndataene.

    Løpenummeret telles per systemforekomst — altså per kombinasjon av
    systemkode og kurs. Det er det som gjør komponentforekomsten unik, og
    dermed det som holder K6 i sjakk.

    `reservenavn` brukes der `familienavn` er tomt — se navnet().
    """
    if not plassering or plassering == PLASSHOLDER:
        # Uten dette merkes hele modellen med plassholderen, og resultatet ser
        # ut som en ferdig merket modell helt til noen leser en ID. En ekte
        # kode i grafen ville vært verre igjen: da ville en fremmed modell
        # blitt merket med et annet bygg uten at noe protesterte.
        raise ValueError(
            "IN[2] er «{0}». Bytt Code Block-noden til prosjektets "
            "plasseringskode før du kjører.".format(plassering)
        )
    if len(familienavn) != len(kursnumre):
        raise ValueError(
            "IN[0] har {0} familienavn og IN[1] har {1} kursnumre. "
            "De to listene må komme fra de samme elementene, i samme "
            "rekkefølge.".format(len(familienavn), len(kursnumre))
        )
    if reservenavn and len(reservenavn) != len(familienavn):
        raise ValueError(
            "IN[3] har {0} navn og IN[0] har {1}. De må komme fra de samme "
            "elementene, i samme rekkefølge.".format(len(reservenavn), len(familienavn))
        )

    tellere = {}
    ut = []
    for i, rå in enumerate(kursnumre):
        navn, _ = navnet(familienavn, reservenavn, i)
        systemkode, komponentkode = familiekode(navn)
        kurs = kursnummer(rå)
        forekomst = (systemkode, kurs)
        tellere[forekomst] = tellere.get(forekomst, 0) + 1
        # Over 999 i samme bøtte ruller det over i systemets løpenummer.
        # HVILKE 999 som havner i «system 1» er VILKÅRLIG — det følger
        # rekkefølgen inn, ikke noe i bygget. Les aldri «.002» som et ekte
        # anlegg nummer to. Alternativet var å utvide løpenummeret til fire
        # siffer, og da hadde prosjektet hatt en grammatikk ingen andre bruker.
        system_lop, komponent_lop = divmod(tellere[forekomst] - 1, MAKS_LOPENUMMER)
        ut.append(
            tfm_id(plassering, systemkode, kurs, komponentkode, komponent_lop + 1, system_lop + 1)
        )
    return ut


def statistikk(familienavn, kursnumre, tfm_er, reservenavn=None):
    """Tallene som avgjør om resultatet er til å stole på.

    Særlig «ukjent_familie» og «uten_kurs»: er de høye, er ikke merkingen gal,
    men den er fattig. Da er det FAMILIER-tabellen eller kursoppsettet i
    modellen som skal ses på — ikke denne grafen.
    """
    brukte = []
    fra_reserve = 0
    for i in range(len(familienavn)):
        navn, reserve = navnet(familienavn, reservenavn, i)
        brukte.append(navn)
        if reserve:
            fra_reserve += 1
    ukjent = sum(1 for n in brukte if familiekode(n) == STANDARD)
    uten_kurs = sum(1 for k in kursnumre if kursnummer(k) == UTEN_KURS)
    return {
        "elementer": len(tfm_er),
        "ukjent_familie": ukjent,
        "uten_kurs": uten_kurs,
        "unike_tfm": len(set(tfm_er)),
        "systemforekomster": len({t.split("-")[0] for t in tfm_er}),
        # Den første verdien, ordrett. Er noe feilkoblet, er dette det eneste
        # som sier HVA som kom inn — et tall kan si at noe er galt, men ikke hva.
        "forste_familie": brukte[0] if brukte else "",
        # Hvor mange som måtte bruke typenavnet. Er tallet høyt, er det
        # systemfamilier — kabelrør og kanaler — og det er som det skal.
        "fra_reserve": fra_reserve,
    }


def antall(n, entall, flertall):
    """«1 familie», ikke «1 familier».

    Sammendraget leses av en BIM-koordinator, ikke av en utvikler. Samme grep
    som _antall i tfm_sjekk/oppsett/toml_ut.py.
    """
    return "{0} {1}".format(n, entall if n == 1 else flertall)


def sammendrag(tall):
    """Én lesbar linje per tall, til en Watch-node."""
    n = tall["elementer"]
    if not n:
        return [
            "Ingen elementer inn.",
            "Sjekk at kategorivalget faktisk traff noe — en tom liste ser",
            "nøyaktig ut som en modell der alt allerede er merket.",
        ]

    linjer = [antall(n, "element", "elementer") + " merket."]
    if tall["unike_tfm"] != n:
        linjer.append(
            "ADVARSEL: bare {0} av {1} TFM-ID-er er unike. Det skal ikke "
            "kunne skje, og gir K6-funn.".format(tall["unike_tfm"], n)
        )
    linjer.append(antall(tall["systemforekomster"], "systemforekomst", "systemforekomster") + ".")
    uk = tall["uten_kurs"]
    linjer.append(
        "{0} uten kursnummer — {1} får undernummer «00».".format(uk, "den" if uk == 1 else "de")
    )
    if tall.get("fra_reserve"):
        linjer.append(
            "{0} hentet navnet fra typen — systemfamilier har ikke familienavn.".format(
                tall["fra_reserve"]
            )
        )
    if tall["ukjent_familie"] == n:
        linjer.append(
            "ADVARSEL: familienavnet står ikke i tabellen."
            if n == 1
            else "ADVARSEL: ingen av de {0} familienavnene står i tabellen.".format(n)
        )
        første = tall["forste_familie"]
        linjer.append('  Første verdi inn: "{0}"'.format(første))
        if not første:
            linjer.append(
                "  Tom. Parameternavnet i Code Block-en finnes ikke på disse "
                "elementene, eller anførselstegnene mangler."
            )
        elif ":" in første or "," in første:
            linjer.append(
                "  Det ser ut som et Revit-objekt, ikke et navn. Legg en "
                "Element.Name inn før IN[0] — og en FamilyType.Family foran den "
                "om du kom fra «Family and Type»."
            )
        else:
            linjer.append("  Legg navnet inn i FAMILIER om det er et ekte familienavn.")
    elif tall["ukjent_familie"]:
        linjer.append(
            "{0} står ikke i tabellen og fikk {1}. Legg {2} inn i FAMILIER "
            "om kodene betyr noe for deg.".format(
                antall(tall["ukjent_familie"], "familie", "familier"),
                STANDARD[0],
                "den" if tall["ukjent_familie"] == 1 else "dem",
            )
        )
    return linjer


# --- Skallet. Kjøres bare i Dynamo. ---

# Ingen sjekk på __name__ — se begrunnelsen i tfm_til_revit.py. At «IN» finnes
# er det eneste sikre tegnet på at vi kjører i Dynamo.
if "IN" in globals():  # pragma: no cover - krever Dynamo
    _familier = [tekst(n) for n in (IN[0] or [])]  # noqa: F821
    _kurser = [tekst(k) for k in (IN[1] or [])]  # noqa: F821
    _plassering = tekst(IN[2])  # noqa: F821

    # IN[3] er valgfri: en graf med tre innganger virker som før, men får da
    # ingenting å falle tilbake på for systemfamiliene.
    _reserve = [tekst(n) for n in (IN[3] or [])] if len(IN) > 3 else None  # noqa: F821

    _tfm = merk(_familier, _kurser, _plassering, _reserve)

    # Liste, ikke tuppel: Dynamo har bare én utgangsport, så de to
    # tingene pakkes sammen og skilles av en Code Block med «x[0];» og
    # «x[1];» på hver sin linje.
    # Indeks 0 er TFM-ID-ene, indeks 1 er tallene — les tallene.
    OUT = [_tfm, sammendrag(statistikk(_familier, _kurser, _tfm, _reserve))]
