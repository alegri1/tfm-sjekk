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

FORBEHOLD OM DEN ENE FILA. Tilfellet «samme identitet to ganger i én fil» er
konstruert her, ved å redigere en GUID i en fikstur for hånd. Snowdon har ingen
slike, og ingen ekte eksport i dette prosjektet har vist det. At det forekommer
i praksis er lest, ikke sett — feilen i koden var ekte og konsekvensen alvorlig
(K6 meldte et duplikat som ikke fantes), men hvor ofte utløseren opptrer, vet vi
ikke.

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
        for id_ in delt.values():
            per_filsett[id_.filer] += 1

        funn = []
        for filer, antall in sorted(per_filsett.items()):
            melding = _flere_filer(filer, antall) if len(filer) > 1 else _en_fil(filer[0], antall)
            funn.append(
                Funn(
                    kontroll=self.id,
                    alvorlighet=self.alvorlighet(k),
                    melding=melding,
                    kildefil=filer[0],
                )
            )
        return funn


def _flere_filer(filer: tuple[str, ...], antall: int) -> str:
    """Samme identitet i flere fagmodeller.

    Handlingen er å fjerne den ene fila fra kjøringen.
    """
    return (
        f"{antall} objekt(er) i omfanget har samme IFC-identitet i "
        f"{len(filer)} fagmodeller ({', '.join(filer)}). "
        f"Vanligvis betyr det at samme modell er sendt inn to ganger — fjern "
        f"den ene fila fra kjøringen. Funnene og tallene i rapporten er "
        f"riktige, men for disse objektene er det tilfeldig hvilken av filene "
        f"et funn tilskrives, og K6 er slått av for dem."
    )


def _en_fil(fil: str, antall: int) -> str:
    """Samme identitet flere ganger i én fil.

    Handlingen er en helt annen: fila må eksporteres på nytt. En felles melding
    ville tvunget leseren til å finne ut selv hvilken av de to som gjelder.
    """
    return (
        f"{antall} identitet(er) i omfanget sitter på flere objekter i {fil}. "
        f"IFC krever at GlobalId er unik innenfor én fil, så fila er ødelagt av "
        f"eksporten — eksporter den på nytt. Objektene deler ett parseresultat "
        f"her, så K6 er slått av for dem, og de øvrige funnene om dem kan gjelde "
        f"feil objekt."
    )
