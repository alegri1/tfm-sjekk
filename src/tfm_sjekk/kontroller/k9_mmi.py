"""K9 (valgfri) — Prosesstatus/MMI.

«Er MMI-verdien satt, og er den konsistent innenfor et system? SIMBA stiller
krav til prosesstatuskode.» (§4)

Tre spørsmål, i den rekkefølgen de er nyttige:

**K9a — er MMI satt?** Bare stilt når fagmodellen faktisk bruker MMI. En fil
der ingen objekter har prosesstatus bruker det ikke, og da er hvert eneste
objekt et falskt funn. Har noen det, er de som mangler det den ekte luka.
Vurderingen gjøres per fil, ikke per kjøring: RIE kan ha kommet til 300 mens
RIV ikke har begynt, og ved federering skal ikke den ene fila dømme den
andre. Prosjekter som *krever* MMI på alt setter `krev_pa_alle` og får
spørsmålet stilt uansett.

**K9b — er verdien i skalaen?** Skalaen står i `tfm-sjekk.toml`, ikke i
koden: MMI-nivåene varierer mellom byggherrer, og §14 er tydelig på at
regelsettet leveres som data. «MMI 300», «300» og «mmi300» er samme verdi.

**K9c — er den konsistent innenfor systemet?** Objekter i samme system bør
ha kommet like langt. Avvikene rapporteres mot den verdien flertallet i
systemet har — ikke omvendt — for at meldingen skal peke på de få objektene
noen har glemt å oppdatere.

Graden er info som standard. Sprikende MMI er en observasjon om hvor
prosjektet står, ikke nødvendigvis en feil: et system *skal* ha objekter på
ulike nivåer midt i en prosjekteringsfase. Sett `alvorlighet` under
`[kontroller.K9]` hvis prosjektet vil ha det strengere.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from tfm_sjekk.kontekst import Kontekst
from tfm_sjekk.kontroller.base import Kontroll, registrer
from tfm_sjekk.modell import Alvorlighet, Funn, IfcObjekt


@registrer
class K9Mmi(Kontroll):
    id = "K9"
    tittel = "MMI/prosesstatus er satt og konsistent innenfor systemet"
    standard_alvorlighet = Alvorlighet.INFO

    def kjor(self, k: Kontekst) -> list[Funn]:
        return self._a_mangler(k) + self._b_ugyldig_verdi(k) + self._c_inkonsistent(k)

    def _a_mangler(self, k: Kontekst) -> list[Funn]:
        # Spørsmålet stilles per fagmodell, ikke per kjøring. Om MMI er i
        # bruk er en egenskap ved den enkelte fila: RIE kan ha kommet til 300
        # mens RIV ikke har begynt å sette prosesstatus i det hele tatt, og
        # ved federering (§3) skal ikke den ene fila dømme den andre.
        per_fil: dict[str, list[IfcObjekt]] = defaultdict(list)
        for objekt in k.relevante_objekter():
            per_fil[objekt.kildefil].append(objekt)

        funn = []
        for fil, i_omfang in sorted(per_fil.items()):
            mangler = [o for o in i_omfang if not normaliser_mmi(o.mmi)]
            if not mangler:
                continue

            if len(mangler) == len(i_omfang):
                # Ingen i denne fila har MMI. Enten brukes det ikke — og da er
                # ett funn per objekt ren støy — eller så mangler det overalt,
                # og da er ett samlet funn like presist.
                if k.config.mmi.krev_pa_alle:
                    funn.append(
                        self.funn(
                            k,
                            f"Ingen av de {len(i_omfang)} objektene i omfanget i "
                            f"{fil} har MMI/prosesstatus. Konfigurasjonen krever "
                            f"det på alle.",
                            kildefil=fil,
                        )
                    )
                continue

            funn.extend(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"Objektet mangler MMI/prosesstatus. Andre objekter i {fil} "
                    f"har det, så feltet er i bruk i denne fagmodellen.",
                    objekt,
                )
                for objekt in mangler
            )
        return funn

    def _b_ugyldig_verdi(self, k: Kontekst) -> list[Funn]:
        gyldige = k.config.mmi.gyldige_verdier
        if not gyldige:
            return []

        funn = []
        for objekt in k.objekter:
            verdi = normaliser_mmi(objekt.mmi)
            if verdi is None or verdi in gyldige:
                continue
            funn.append(
                Funn.for_objekt(
                    self.id,
                    self.alvorlighet(k),
                    f"MMI-verdien «{objekt.mmi}» er ikke i skalaen prosjektet "
                    f"bruker ({', '.join(gyldige)}).",
                    objekt,
                    verdi=objekt.mmi,
                )
            )
        return funn

    def _c_inkonsistent(self, k: Kontekst) -> list[Funn]:
        per_system: dict[str, list[tuple[IfcObjekt, str]]] = defaultdict(list)
        for objekt, tfm in k.med_tfm():
            verdi = normaliser_mmi(objekt.mmi)
            if verdi is not None:
                # Grupperingen går på systemet (4310.001), ikke på
                # systemforekomsten (4310.001.12). Undernummeret er kurs eller
                # tur/retur — en modenhetsgrad hører til systemet som helhet,
                # og per forekomst blir gruppene for små til å si noe.
                per_system[tfm.system].append((objekt, verdi))

        funn = []
        for system, medlemmer in sorted(per_system.items()):
            teller = Counter(verdi for _, verdi in medlemmer)
            if len(teller) < 2:
                continue

            # Flertallsverdien, med alfabetisk tiebreak så rapporten er
            # deterministisk (§7) selv når to nivåer er like vanlige.
            vanligst = min(teller.items(), key=lambda par: (-par[1], par[0]))[0]
            andre = ", ".join(f"{verdi} ({antall})" for verdi, antall in sorted(teller.items()))

            for objekt, verdi in medlemmer:
                if verdi == vanligst:
                    continue
                funn.append(
                    Funn.for_objekt(
                        self.id,
                        self.alvorlighet(k),
                        f"MMI «{verdi}» avviker fra resten av systemet "
                        f"{system}, der de fleste står på «{vanligst}» "
                        f"(fordeling: {andre}).",
                        objekt,
                        verdi=objekt.mmi,
                    )
                )
        return funn


def normaliser_mmi(verdi: str | None) -> str | None:
    """«MMI 300», «mmi300» og «300» er samme nivå.

    Sifrene er det som betyr noe; alt annet er skrivemåte. En verdi helt uten
    siffer beholdes som den er, i store bokstaver — da bruker prosjektet en
    skala vi ikke skal late som vi forstår.
    """
    if verdi is None:
        return None
    tekst = verdi.strip()
    if not tekst:
        return None
    siffer = re.sub(r"\D", "", tekst)
    return siffer or tekst.upper()
