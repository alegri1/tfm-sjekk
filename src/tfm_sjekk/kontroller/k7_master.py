"""K7 — Referanseintegritet mot TFM-master.

«K7 sjekker at hvert system og hver komponenttype modellen bruker faktisk
står i mastera — og motsatt, hvilke oppføringer i mastera som ennå ikke er
modellert.» (§4)

De to retningene har ulik karakter, og det styrer alvorlighetsgraden:

*Modell → master* er en feil. Modellereren har funnet på et system eller en
komponenttype som ikke er omforent tverrfaglig, og det er nettopp den
avviket SIMBA-mastera finnes for å hindre.

*Master → modell* er **info**, uansett hva `alvorlighet` er satt til i
konfigurasjonen. En oppføring som ikke er modellert kan være prosjektert,
men ikke tegnet ennå; den kan tilhøre et annet fag enn fila som sjekkes; og
den kan være utgått uten at noen strøk den. Å skille «ikke ennå» fra
«utgått» krever prosesstatus (K9) — se TODO under. Inntil det er avklart med
en RIE er det uansvarlig å la denne retningen kunne bryte et CI-bygg, så
graden er låst og teller ikke mot exit-koden (§5).
"""

from __future__ import annotations

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn
from tfm_sjekk.tabeller.master import normaliser

MAKS_I_MELDING = 20


@registrer
class K7Master(Kontroll):
    id = "K7"
    tittel = "Systemer og komponenttyper finnes i prosjektets TFM-master"
    standard_alvorlighet = Alvorlighet.FEIL
    krever_master = True

    def kjor(self, k: Kontekst) -> list[Funn]:
        if k.master is None:
            return []

        funn: list[Funn] = []
        brukte_systemer: set[str] = set()
        brukte_typer: set[str] = set()

        # En master trenger ikke føre begge listene. Sjekker vi mot en tom
        # liste, flagger vi hele modellen for noe prosjektet aldri har lovet
        # å vedlikeholde — derfor sjekkes en retning bare når den har innhold.
        sjekk_systemer = bool(k.master.systemer)
        sjekk_typer = bool(k.master.komponenttyper)

        for objekt, tfm in k.med_tfm():
            brukte_systemer.add(tfm.systemforekomst)
            if sjekk_systemer and not k.master.kjenner_system(tfm.systemforekomst):
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Systemforekomsten «{tfm.systemforekomst}» står ikke i "
                        f"TFM-mastera ({k.master.kilde}).",
                        objekt,
                    )
                )

            # Komponenttypen kan stå i %-delen eller i typefeltet. Spriker de
            # to, har objektet ingen avklart type: T1 melder spriket, og et funn
            # herfra ville hvilt på et vilkårlig valg mellom to verdier.
            if k.komponenttype_spriker(objekt) is not None:
                continue
            komponenttype = k.komponenttype_for(objekt)
            if komponenttype is None:
                continue
            brukte_typer.add(komponenttype)
            if sjekk_typer and not k.master.kjenner_type(komponenttype):
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"Komponenttypen «{komponenttype}» står ikke i "
                        f"TFM-mastera ({k.master.kilde}).",
                        objekt,
                    )
                )

        funn.extend(self._umodellert(k, brukte_systemer, brukte_typer))
        return funn

    def _umodellert(
        self, k: Kontekst, brukte_systemer: set[str], brukte_typer: set[str]
    ) -> list[Funn]:
        """Motsatt retning: oppføringer i mastera modellen ikke bruker.

        Samlet til ett funn per kategori, ikke ett per oppføring. Mastera
        gjelder hele prosjektet mens en kjøring gjerne dekker én fagmodell,
        så per oppføring ville drukne de virkelige feilene i info-linjer.
        Funnene har ingen GlobalId — de peker på mastera, ikke på et objekt.

        TODO: når K9 er på plass kan «ikke modellert» krysses mot
        prosesstatus, slik at det som er prosjektert men ikke tegnet kan
        skilles fra det som er utgått. Avklar med en RIE hvilke MMI-nivåer
        som betyr hva før dette skjerpes til advarsel.
        """
        assert k.master is not None

        funn = []
        for oppforinger, brukt, entall, flertall in (
            (k.master.systemer, brukte_systemer, "system", "systemer"),
            (k.master.komponenttyper, brukte_typer, "komponenttype", "komponenttyper"),
        ):
            # Modellsiden må gjennom samme normalisering som mastera, ellers
            # ville et modellert system stått som umodellert.
            umodellert = sorted(oppforinger - {normaliser(v) for v in brukt})
            if not umodellert:
                continue

            vist = ", ".join(umodellert[:MAKS_I_MELDING])
            resten = len(umodellert) - MAKS_I_MELDING
            if resten > 0:
                vist += f" … og {resten} til"

            hva = entall if len(umodellert) == 1 else flertall
            funn.append(
                Funn(
                    kontroll=self.id,
                    alvorlighet=Alvorlighet.INFO,
                    melding=(
                        f"{len(umodellert)} {hva} i TFM-mastera "
                        f"({k.master.kilde}) er ikke brukt i modellen: {vist}."
                    ),
                )
            )
        return funn
