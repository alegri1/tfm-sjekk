"""Lager små demomodeller med tilsiktede feil.

    uv run python eksempler/lag_demomodell.py

Åtte filer, med hver sin jobb:

    demo-rie.ifc, demo-riv.ifc, demo-elektro.ifc   kontrollene K1-K9 og T1
    avveie.ifc                                     «tfm-sjekk oppsett»
    blindsone.ifc                                  grensen for hva oppsett ser
    tidligfase.ifc                                 merking uten plassering
    visning.ifc                                    BCF-en prøvd i en viewer
    visning-2x3.ifc                                samme, men til import i Revit

Bare de tre første er merket «demo-», og det er med vilje: globben under skal
treffe akkurat dem. De fem andre har verdier som ville forstyrret en
kontrollkjøring — avveie.ifc og blindsone.ifc ligger utenfor oppsettet,
tidligfase.ifc krever sitt eget oppsett for å gi mening, og de to visning-filene
er kopier av elektromodellen som ville gitt K6-duplikater av hver komponent.

    uv run tfm-sjekk eksempler/demo-*.ifc \
        --systemtabell eksempler/FIKTIV-systemkoder.csv \
        --komponenttabell eksempler/FIKTIV-komponentkoder.csv \
        --master eksempler/FIKTIV-tfm-master.csv

Modellene inneholder kun oppdiktede verdier. Se eksempler/LES-MEG.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tests"))

from fixtures.syntetisk import (
    lag_elektromodell,
    lag_modell,
    lag_modell_i_blindsonen,
    lag_modell_pa_avveie,
    lag_tidligfasemodell,
)

HER = Path(__file__).parent

RIE = [
    ("IfcFlowTerminal", "++115080=4310.001.12-QLF001"),  # ok
    ("IfcFlowTerminal", "++115080=4310.001.00-QLF002"),  # K8: kursnummer mangler (+ K7)
    ("IfcFlowTerminal", "++115080=9999.001.12-QLF003"),  # K3: ukjent systemkode (+ K7)
    ("IfcFlowTerminal", "++115080=2300.001.12-QLF004"),  # K4: overordnet kode
    ("IfcFlowTerminal", "++11508=4310.001.12-QLF005"),  # K2: for få siffer
    ("IfcFlowTerminal", None),  # K1: ingen TFM
]

RIV = [
    ("IfcFlowTerminal", "++115080=3600.001.04-JVZ001%JVZ.001.008"),  # ok
    ("IfcFlowTerminal", "++115080=4310.001.12-QLF001"),  # K6: duplikat av RIE
    ("IfcFlowTerminal", "++115080=3600.001.04-XXX009"),  # K5: ukjent komponentkode
]

# Fordelinger med tilkoblede objekter — det K8b og K8c leser. Tavla er
# merket «.00» med vilje: den er roten kursene går ut fra, ikke noe som
# selv ligger på en kurs.
ELEKTRO = [
    {
        "navn": "Fordeling 1",
        "tfm": "++115080=4310.001.00-QLF100",
        "mmi": "300",
        "objekter": [
            # ok: samme system som tavla, hver sin kurs
            {
                "klasse": "IfcLamp",
                "tfm": "++115080=4310.001.12-QLF101",
                "kurs": "Kurs 12",
                "mmi": "300",
            },
            {
                "klasse": "IfcLamp",
                "tfm": "++115080=4310.001.13-QLF102",
                "kurs": "Kurs 13",
                "mmi": "300",
            },
            # K8b: hører til et annet system enn fordelingen
            {
                "klasse": "IfcLamp",
                "tfm": "++115080=4320.001.12-QLF103",
                "kurs": "Kurs 12",
                "mmi": "300",
            },
            # K8c: ny kurs, men gjenbruker kursnummer 14 fra Kurs 14
            {
                "klasse": "IfcOutlet",
                "tfm": "++115080=4310.001.14-QLF104",
                "kurs": "Kurs 14",
                "mmi": "300",
            },
            # K9: ligger igjen på 200 mens resten av systemet er på 300
            {
                "klasse": "IfcOutlet",
                "tfm": "++115080=4310.001.14-QLF105",
                "kurs": "Kurs 14B",
                "mmi": "200",
            },
            # T1: TFM-ID-en og typefeltet er uenige om komponenttypen
            {
                "klasse": "IfcLamp",
                "tfm": "++115080=4310.001.13-QLF106%QLF.001.004",
                "typefelt": "QLF.001.005",
                "kurs": "Kurs 13",
                "mmi": "300",
            },
            # K7: komponenttypen står bare i typefeltet, og ikke i mastera.
            # Uten denne endringen hoppet K7 over objektet.
            {
                "klasse": "IfcLamp",
                "tfm": "++115080=4310.001.13-QLF107",
                "typefelt": "QLF.001.003",
                "kurs": "Kurs 13",
                "mmi": "300",
            },
        ],
    }
]


def _til_2x3(fordelinger):
    """Bytter IFC4-klassene mot dem som finnes i IFC 2x3.

    IfcLamp, IfcOutlet og IfcElectricDistributionBoard kom med IFC4. I 2x3 er
    alt utstyr IfcFlowTerminal, og en tavle er IfcElectricDistributionPoint.
    """
    kart = {
        "IfcLamp": "IfcFlowTerminal",
        "IfcOutlet": "IfcFlowTerminal",
        "IfcElectricDistributionBoard": "IfcElectricDistributionPoint",
    }
    ut = []
    for fordeling in fordelinger:
        ny_fordeling = dict(fordeling)
        ny_fordeling["klasse"] = kart.get(
            fordeling.get("klasse", "IfcElectricDistributionBoard"),
            "IfcElectricDistributionPoint",
        )
        ny_fordeling["objekter"] = [
            dict(o, klasse=kart.get(o.get("klasse", "IfcFlowTerminal"), "IfcFlowTerminal"))
            for o in fordeling.get("objekter", [])
        ]
        ut.append(ny_fordeling)
    return ut


ELEKTRO_2X3 = _til_2x3(ELEKTRO)


if __name__ == "__main__":
    for navn, objekter in (("demo-rie.ifc", RIE), ("demo-riv.ifc", RIV)):
        sti = lag_modell(objekter, HER / navn)
        print(f"skrev {sti}")
    print(f"skrev {lag_elektromodell(ELEKTRO, HER / 'demo-elektro.ifc')}")

    # Egen modell for «tfm-sjekk oppsett»: verdiene ligger utenfor
    # standardoppsettet, slik at kommandoen har noe å foreslå. Den holdes
    # utenfor «demo-*.ifc» med vilje — tas den med i en kontrollkjøring, er den
    # bare tre objekter med merkelige psett-navn, og det demonstrerer ingenting.
    print(f"skrev {lag_modell_pa_avveie(HER / 'avveie.ifc')}")

    # Grensen for hva «oppsett» kan hjelpe med: verdiene ligger i et
    # ukonfigurert egenskapssett OG et ukonfigurert felt samtidig. Da har
    # verdiuttrekket ingen holdepunkter, og verktøyet ser ingenting — enda
    # modellen er merket helt korrekt.
    print(f"skrev {lag_modell_i_blindsonen(HER / 'blindsone.ifc')}")

    # Merket uten plassering. Kjørt med standardoppsettet gir den fem
    # syntaksfunn om «++»-delen; med eksempler/tidligfase.toml forsvinner de.
    print(f"skrev {lag_tidligfasemodell(HER / 'tidligfase.ifc')}")

    # Samme innhold, men med prosjekt, romlig struktur og geometri, slik at
    # fila kan åpnes i en viewer. Den er til manuell prøving av BCF-en:
    # et viewpoint kan bare vises hvis modellen har noe å vise.
    #
    # Den heter bevisst ikke «demo-»: den har samme TFM-verdier som
    # elektromodellen, så tas den med i en «demo-*.ifc»-kjøring finner K6
    # hver eneste komponentforekomst i to filer. Riktig oppførsel, ubrukelig
    # demo — 39 funn i stedet for 17.
    print(f"skrev {lag_elektromodell(ELEKTRO, HER / 'visning.ifc', geometri=True)}")

    # Samme modell i IFC 2x3. Revits IFC-importør åpner 2x3 langt mer pålitelig
    # enn IFC4, så det er denne du bruker hvis du vil ha modellen inn i Revit og
    # prøve Dynamo-grafen. Klassene er byttet ut: IfcLamp, IfcOutlet og
    # IfcElectricDistributionBoard finnes ikke i 2x3.
    sti = lag_elektromodell(ELEKTRO_2X3, HER / "visning-2x3.ifc", schema="IFC2X3", geometri=True)
    print(f"skrev {sti}")
