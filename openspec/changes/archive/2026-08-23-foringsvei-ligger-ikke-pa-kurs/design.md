## Context

Se `proposal.md` for hvorfor. Det som former løsningen er at unntaket allerede
finnes, i K8a selv:

```python
if k.er_fordeling(objekt):
    # Fordelingen er roten kursene går ut fra, ikke noe som selv
    # ligger på en kurs.
    continue
```

Begrunnelsen i kommentaren er nøyaktig den som gjelder for føringsvei. Endringen
er å gjenkjenne at argumentet har to tilfeller, ikke ett.

`er_fordeling` matcher på `objekt.er_av_type(k)` for hver konfigurerte klasse —
altså mot objektets egen arvekjede, som `IfcObjekt` bærer med seg fra uttrekket.
Det er den samme formen `er_foringsvei` skal ha.

## Goals / Non-Goals

**Mål:**
- Standardlista skal virke uten at noe konfigureres. Første kjøring er der
  inntrykket dannes.
- Unntaket skal gjelde bare kravet om kursnummer, ikke resten av K8.
- Det skal være ett sted som avgjør hva som er føringsvei.

**Ikke mål:**
- Å unnta på systemkode. Det ble vurdert og forkastet: mer TFM-nativt, men det
  virker ikke før prosjektet har fylt ut lista — og en liste som må fylles ut før
  rapporten blir lesbar, blir ikke fylt ut.
- Å slå sammen de gjenværende funnene til ett per system. 168 funn i en modell
  med 2439 objekter er en lesbar rapport, og hvert objekt trenger sin egen
  BCF-sak for å kunne finnes i en viewer.
- Å endre K8b eller K8c.

## Decisions

### `er_foringsvei` ved siden av `er_fordeling`

Samme form, samme sted, samme slags konfigurasjon. To metoder på `Kontekst` som
svarer på hvert sitt spørsmål om samme objekt, og K8a spør begge.

*Vurdert og forkastet:* én metode `ligger_pa_kurs(objekt)` som slår sammen begge
unntakene. Kortere i K8a, men den ville skjult at det er to ulike ting med hver
sin konfigurasjon — og når noe ikke flagges, er spørsmålet alltid *hvilken* av
dem som slo til.

### Standardlista dekker begge skjemaer

```
IfcFlowSegment, IfcFlowFitting            finnes i både IFC4 og 2x3
IfcCableCarrierSegment, IfcCableCarrierFitting   bare IFC4
IfcCableSegment, IfcCableFitting                 bare IFC4
```

De fire siste finnes ikke i IFC 2x3. Det er ufarlig, fordi treff går mot
objektets egen arvekjede: et navn som ikke finnes i skjemaet matcher aldri noe.
Det er samme grunn til at `fordeling_klasser` kan liste både
`IfcElectricDistributionBoard` og `IfcElectricDistributionPoint`.

`IfcFlowSegment` og `IfcFlowFitting` er brede — de dekker også rør og kanaler for
VVS. Det gjør ingenting: K8a gjelder bare systemer i NS 3451 kapittel 4 og 5, så
en ventilasjonskanal er allerede utenfor.

### Unntaket gjelder bare K8a

K8b og K8c leser koblingsgrafen og kursgrupperingen, og føringsveien er nettopp
det som knytter utstyr til en fordeling. `_bygg_fordelinger` søker i bredden
gjennom kabler for å finne hva som mates av hva — utelot vi føringsveien der,
ville lampen mistet fordelingen sin.

Det er derfor unntaket ligger i K8a og ikke i `med_tfm()` eller i uttrekket.

## Risks / Trade-offs

**Utstyr eksportert som IfcFlowSegment slipper unna** → En eksport som legger et
apparat i en segmentklasse ville ikke fått kravet om kursnummer. Prisen er
akseptabel: alternativet er 850 falske funn i en modell der 850 objekter faktisk
er kabelrør. Og en modell som legger utstyr i `IfcFlowSegment` har et større
problem enn manglende kursnummer.

**Standardlista er en antakelse om norsk praksis** → Klassene er valgt av hva IFC
selv mener med dem, ikke av hva et norsk prosjekt gjør. Er den gal, er den
konfigurerbar — og det er verdt å ta med som spørsmål til en RIE: *hva eksporteres
kabelføringen deres som?*

**Tallet 168 er fra én modell** → Det er Snowdon Towers med min egen merking, ikke
et norsk prosjekt. Det som holder uansett modell er forholdet: kravet gjelder det
som mates av en kurs, og ikke det som bærer den.

## Migration Plan

Ingen. Et prosjekt får færre funn av samme kjøring; ingen konfigurasjon må
endres, og ingen tidligere gyldig oppsett slutter å virke.

## Open Questions

Ingen som kan utsettes uten å endre spesifikasjonen eller oppgavene.
