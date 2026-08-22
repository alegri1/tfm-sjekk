## 1. Konfigurasjonen

- [x] 1.1 `ElektroOppsett.foring_klasser` med standardlista, og en kommentar om
      hvorfor IFC4-bare klasser er ufarlige å liste
- [x] 1.2 `tfm-sjekk.toml` i repoet får feltet med samme forklaring

## 2. Kontrollen

- [x] 2.1 `Kontekst.er_foringsvei(objekt)`, samme form som `er_fordeling`
- [x] 2.2 K8a hopper over føringsvei, med en kommentar som knytter unntaket til
      det som allerede gjelder fordelinger — det er samme argument
- [x] 2.3 Slå fast at K8b og K8c er urørt: føringsveien er nettopp det som
      knytter utstyr til en fordeling i koblingsgrafen

## 3. Tester

- [x] 3.1 Lampe uten kursnummer meldes, lampe med kursnummer meldes ikke
- [x] 3.2 Kabelrør uten kursnummer meldes ikke
- [x] 3.3 Fordeling uten kursnummer meldes ikke, som før
- [x] 3.4 Objekt i et ikke-elektro-system er upåvirket
- [x] 3.5 En klasse lagt til i oppsettet regnes som føringsvei
- [x] 3.6 Et klassenavn som ikke finnes i skjemaet gir ingen feil
- [x] 3.7 K8b/K8c: en lampe koblet til en fordeling **gjennom et kabelrør**
      regnes fortsatt som matet fra den fordelingen

## 4. Demo

- [x] 4.1 `demo-elektro.ifc` får et kabelrør uten kursnummer, som ikke skal
      meldes — uten det finnes tilfellet ikke i noen modell i repoet
- [x] 4.2 Kjør demoen og slå fast at antallet funn er uendret: kabelrøret skal
      ikke legge til et funn, og ikke fjerne et

## 5. Prøving mot en ekte modell

- [x] 5.1 Kjør `verktoy/legg_til_tfm.py` på Snowdon Towers og deretter
      `tfm-sjekk` — antallet skal falle fra 1029 til omtrent 179
- [x] 5.2 Slå fast at de gjenværende K8-funnene er utstyr, ikke føringsvei
- [x] 5.3 `verktoy/legg_til_tfm.py`: en linje i docstringen om hva kjøringen mot
      den modellen avdekket, så neste person vet hvorfor skriptet finnes
