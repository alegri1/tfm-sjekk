## Context

Se proposal.md — Why.

`Kontekst.er_foringsvei(objekt)` ser i dag bare på objektets arvekjede:

```python
def er_foringsvei(self, objekt: IfcObjekt) -> bool:
    return any(objekt.er_av_type(k) for k in self.config.elektro.foring_klasser)
```

K8a er eneste bruker, og der finnes den parsede TFM-ID-en allerede — sløyfa går
over `k.med_tfm()`, som gir `(objekt, tfm)`.

Verdt å merke seg: K8 leser allerede systemkoden. `TfmId.er_elektro` ser på om
den starter med 4 eller 5, og det er den avlesningen som avgjør om kontrollen
gjelder objektet i det hele tatt.

## Goals / Non-Goals

**Goals:**

- Et objekt prosjektet har merket som føringsvei skal ikke få spørsmål om
  kursnummer, uansett hva eksporten gjorde med IFC-klassen.
- Oppførselen uten konfigurasjon skal være uendret.

**Non-Goals:**

- Å gjette. Et objekt er unntatt fordi prosjektet har oppgitt koden, ikke fordi
  verktøyet syntes den så ut som en føringsvei.
- Å legge NS 3451-koder inn i verktøyet. Se avgjørelsen under.
- Å utvide `foring_klasser` med `IfcBuildingElementProxy`. Det ville unntatt
  hver eneste proxy i modellen — 934 i Snowdon — og dermed slått av K8 for
  nesten alt utstyret.
- Å røre K8b og K8c. Unntaket gjelder bare kravet om kursnummer, som før.

## Decisions

### Systemkoden, ikke komponentkoden

Komponentkoden sier mer presist hva et objekt *er* — `QLK` er kabelforing
uansett hvilket system den ligger i. Den ble likevel valgt bort.

K8 leser systemkoden fra før, og gjør allerede nøyaktig denne slags vurdering
med den: «starter den med 4 eller 5, gjelder kontrollen». Å legge til «står den
i denne lista, gjelder unntaket» er ett steg til på samme sti. Komponentkoden
ville vært et nytt felt å ta stilling til, med sin egen tolkning og sine egne
grensetilfeller.

Prisen er at et objekt med riktig komponentkode i feil system ikke blir unntatt.
Det er akseptabelt: da er merkingen feil, og K3 eller K7 har allerede noe å si om
den.

### Tom standardliste

`foring_klasser` har en standardliste som virker uten konfigurasjon, og
spesifikasjonen begrunner det: «Første kjøring er der inntrykket dannes.» Denne
lista får ikke det samme.

Grunnen er §8, ikke pedagogikk. `IfcFlowSegment` er et navn fra IFC-skjemaet,
som er åpent. `4360` er innholdet i NS 3451, som er en betalt standard fra
Standard Norge, og som ikke skal ligge i dette repoet i noen form.

Konsekvensen må vi ta med åpne øyne: den som ikke konfigurerer noe, ser ingen
forskjell. Derfor hører nøkkelen hjemme i `tfm-sjekk.toml` med et utfylt
eksempel i kommentaren — kommentaren er der brukeren leter, og en tom liste uten
forklaring er en nøkkel ingen finner.

### `er_foringsvei` tar TFM-ID-en med

Signaturen blir `er_foringsvei(objekt, tfm)`. Alternativet var å slå opp TFM-en
inne i metoden, men `Kontekst` har den allerede parset, og K8a har den i hånden.
Å slå den opp på nytt ville vært å gjøre samme arbeid to ganger for å slippe et
argument.

`er_fordeling` får ikke samme behandling. Den har ikke det samme problemet i
dag, og en endring «for symmetriens skyld» er en endring uten en grunn.

## Risks / Trade-offs

**Et objekt kan bli unntatt på grunn av feil merking** → Merker noen en lampe
som `4360`, blir den unntatt fra K8a. Men da er merkingen gal på en måte K3 og
K7 allerede fanger — systemkoden må finnes i kodetabellen og i mastera. Unntaket
kan gjøre et objekt taust for K8a, ikke for verktøyet.

**Tom standardliste betyr at ingen får glede av dette uten å lese** → Reell.
Motvekten er kommentaren i `tfm-sjekk.toml` og at `oppsett`-kommandoen finnes
for nettopp det å komme i gang. Alternativet — å skrive `4360` inn i verktøyet —
er ikke et alternativ (§8).

**To kjennetegn er vanskeligere å forklare enn ett** → Meldingen fra K8a sier i
dag hvorfor et objekt meldes. Den sier ikke hvorfor et annet ikke ble det, og
det skal den heller ikke: et funn som ikke finnes er ikke noe å forklare. Den
som lurer, finner begge listene i `tfm-sjekk.toml`.
