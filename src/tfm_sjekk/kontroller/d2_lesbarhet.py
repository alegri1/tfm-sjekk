"""D2 — Lesbarhet: falt alt ut på grammatikken?

Som D1 kontrollerer denne *kjøringen*, ikke modellen, og står derfor utenfor
nummerserien K1–K9 i §4.

En TFM-verdi som ikke lar seg tolke gjør objektet usynlig for sju kontroller.
`med_tfm()` returnerer bare det som parset, og K3, K4, K5, K6, K7, K8 og K9
leser den. K2 melder at syntaksen er gal; ingenting melder hva det koster.

Ett objekt med skrivefeil er en detalj K2 dekker. Faller *alt* ut, er det noe
annet: en merkekonvensjon som ikke stemmer med grammatikken i oppsettet. Et
prosjekt med fem siffer i plasseringen der oppsettet venter seks får hvert
eneste objekt til å falle ut — og rapporten viser da en haug K2-funn og
ingenting annet, som om syntaks var det eneste problemet.

De to krever motsatt handling: rett objektene, eller rett oppsettet. Derfor er
dette et eget funn og ikke bare flere K2-er.

EGEN KONTROLL, IKKE EN UTVIDELSE AV D1. D1 svarer på om noe var i omfanget;
denne på om det var lesbart nok til å bli kontrollert. To spørsmål, to
alvorlighetsgrader å styre hver for seg, og D1s melding er lang nok fra før.

Graden er advarsel, av samme grunn som D1: verktøyet står som port i en
leveranseprosess (§5), og et prosjekt med en annen grammatikk skal ikke stenge
døra på et funn som handler om oppsettet. De enkelte K2-funnene er fortsatt
feil, og de avgjør exit-koden.
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn


@registrer
class D2Lesbarhet(Kontroll):
    id = "D2"
    tittel = "TFM-verdiene lot seg tolke"
    standard_alvorlighet = Alvorlighet.ADVARSEL

    def kjor(self, k: Kontekst) -> list[Funn]:
        med_verdi = k.med_tfm_verdi()
        uleselige = k.uleselige()

        funn = []
        for fil, antall in sorted(med_verdi.items()):
            # Grensen er ALLE, ikke en terskel. En terskel ville vært et tall
            # uten begrunnelse; «alle» er den ene grensen som ikke trenger
            # forsvares. Faller 90 % ut, står de 10 % igjen som ekte funn, og
            # K2 sier fortsatt hva som er galt med hver enkelt.
            if not antall or uleselige.get(fil, 0) != antall:
                continue

            funn.append(
                Funn(
                    kontroll=self.id,
                    alvorlighet=self.alvorlighet(k),
                    melding=(
                        f"Ingen av de {antall} TFM-verdiene i {fil} lot seg tolke. "
                        f"Da er objektene usynlige for kontrollene som krever en "
                        f"tolket ID, og forklaringen ligger sannsynligvis i "
                        f"merkekonvensjonen framfor i hvert enkelt objekt — se "
                        f"«[grammatikk]» i tfm-sjekk.toml. "
                        f"Første avvik: {self._forste_avvik(k, fil)}"
                    ),
                    kildefil=fil,
                )
            )
        return funn

    def _forste_avvik(self, k: Kontekst, fil: str) -> str:
        """Én parsefeil ordrett, som bevis.

        Et tall sier at noe er galt; meldingen sier hva. Uten den må leseren
        finne et K2-funn selv for å forstå hvilken del av grammatikken det
        gjelder — og det er nettopp den koblingen funnet finnes for å gjøre.
        """
        for objekt in k.relevante_objekter():
            if objekt.kildefil == fil and objekt.global_id in k.parsefeil:
                return f"«{k.parsefeil[objekt.global_id]}»"
        return "«ukjent»"
