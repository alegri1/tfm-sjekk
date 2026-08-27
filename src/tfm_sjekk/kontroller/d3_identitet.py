"""D3 — Identitet: er funnene festet til riktig fil?

Som D1 og D2 kontrollerer denne *kjøringen*, ikke modellen, og står derfor
utenfor nummerserien K1–K9 i §4.

De tre svarer på hvert sitt spørsmål, og skal ikke blandes:

    D1  var noe i omfanget?
    D2  var det lesbart nok til å bli kontrollert?
    D3  er resultatet til å stole på?

`Kontekst` slår opp objekter på GlobalId, og `parsede` og `parsefeil` er nøklet
likt. Går samme identitet igjen i to fagmodeller, kollapser de: K2, K6 og K8
fester funnet til en vilkårlig av filene, og to objekter deler ett
parseresultat.

Prøvd med samme demomodell under to filnavn: 12 objekter lest, 6 unike
identiteter, 5 parseresultater — og tretten funn fordelt elleve/to på to
identiske filer.

Den vanligste årsaken er at samme modell er sendt inn to ganger, og da er
handlingen å fjerne den ene fila. Verktøyet velger ikke selv: hvilket av to like
objekter som er det rette, kan bare den som sendte inn filene svare på.

GRAD ADVARSEL, og grunnen er praktisk. Sendes samme modell inn to ganger, fyrer
K6 på hvert eneste merkede objekt, og exit-koden er 1 uansett fra dem. D3 trenger
ikke å endre porten — den trenger å forklare hvorfor porten stengte. En advarsel
som forklarer et titalls feil er mer verdt enn en feil til.
"""

from __future__ import annotations

from collections import defaultdict

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class D3Identitet(Kontroll):
    id = "D3"
    tittel = "Objektidentiteten er entydig på tvers av fagmodellene"
    standard_alvorlighet = Alvorlighet.ADVARSEL

    def kjor(self, k: Kontekst) -> list[Funn]:
        delt = k.delt_identitet()
        if not delt:
            return []

        # Gruppert per filkombinasjon, ikke per objekt. Deler to filer tusen
        # objekter, er det ETT problem — og tusen like funn ville skjult det.
        per_filsett: dict[tuple[str, ...], int] = defaultdict(int)
        for filer in delt.values():
            per_filsett[tuple(filer)] += 1

        funn = []
        for filer, antall in sorted(per_filsett.items()):
            funn.append(
                Funn(
                    kontroll=self.id,
                    alvorlighet=self.alvorlighet(k),
                    melding=(
                        f"{antall} objekt(er) i omfanget har samme IFC-identitet i "
                        f"{len(filer)} fagmodeller ({', '.join(filer)}). "
                        f"Vanligvis betyr det at samme modell er sendt inn to ganger. "
                        f"Funnene og tallene i rapporten er riktige, men for disse "
                        f"objektene er det tilfeldig hvilken av filene et funn "
                        f"tilskrives — og K6 kan melde duplikat på det som er ett "
                        f"objekt talt to ganger."
                    ),
                    kildefil=filer[0],
                )
            )
        return funn
