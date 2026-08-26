## Context

Se proposal.md — Why. Det som avgjør formen er hvor brukeren allerede ser:

`OUT[1]` går til en Watch-node, og `dynamo/LES-MEG.md` sier «Les tallene før du
stoler på resultatet». Den linja finnes fordi en kobling som treffer null
elementer ser nøyaktig ut som en modell uten avvik. **Sammendraget er stedet
brukeren går for å avgjøre om resultatet er til å stole på**, og en gammel kopi
er nettopp et slikt spørsmål.

## Goals / Non-Goals

**Goals:**
- En gammel kopi røper seg selv der brukeren allerede leser.
- Versjonen kan ikke bli uenig med skriptet den står i.
- Demomappas kopi slutter å være et eget ledd å huske på.

**Non-Goals:**
- Ingen kontroll av at kopien i Dynamo er fersk. Det kan ikke gjøres — Dynamo
  kjører strengen, og strengen vet ikke hva den skulle vært. Vi kan bare gjøre
  alderen **synlig**.
- Ingen automatisk innliming i brukerens graf. Dynamo har ingen krok for det,
  og en `exec(open(...))` ville gjort en fil på brukerens maskin til del av
  kjøringen — verre å feilsøke enn kopien.
- Ingen endring i hva merkingen produserer.

## Decisions

### Versjonen er pakkens versjon, ikke en egen teller

`VERSJON = "0.8.1"`, satt av `oppdater-grafene.py` fra `pyproject.toml`.

En egen teller ville krevd at noen husker å øke den — samme slags regel som
allerede sviktet tre ganger. Pakkens versjon endres uansett ved hver utgivelse,
og den er det brukeren ser i `LES-MEG.txt` og i BCF-forfatteren. Ett tall å
sammenligne, ikke to systemer å holde i hodet.

*Alternativ vurdert:* en hash av skriptet. Presist, men uleselig — «a3f9c2» sier
ingenting om den er eldre eller nyere enn din. En versjon kan sammenlignes av et
menneske.

### Skriveren setter versjonen, kilden bærer en plassholder

`dynamo/tfm_fra_revit.py` har `VERSJON = "ukjent"` i repoet.
`oppdater-grafene.py` bytter den til pakkens versjon **på vei inn i `.dyn`-fila**.

Da kan de to ikke bli uenige: kilden har ingen versjon å drive fra, og kopien
får sin i samme operasjon som skriptet. Sto versjonen i kilden, måtte den
oppdateres før innliming — og rekkefølgen ville vært en ny regel å huske.

Følgen er at en bruker som limer inn direkte fra `.py`-fila får «ukjent». Det er
riktig: da *er* alderen ukjent, og linja sier det.

### Linja står alltid, ikke bare ved avvik

    Skript 0.8.1.

Ikke «ADVARSEL: gammel kopi» — skriptet kan ikke vite hva som er nytt. Det kan
bare oppgi hva det selv er, og la brukeren sammenligne med utgivelsen hun
hentet.

En linje som bare vises av og til blir ikke lest når den først dukker opp.
Denne står i hver kjøring, ved siden av tallene brukeren allerede bruker til å
avgjøre om resultatet duger.

### Skriveren tar demomappa når den finnes

`oppdater-grafene.py` skriver i dag bare til `dynamo/`. Demomappas kopi
oppdateres av `lag_demomappe.py`, som kjøres per utgivelse — og imellom kan den
være eldre enn repoet. Det var nøyaktig feilen 25. august.

Skriveren tar derfor demomappa hvis stien finnes, og sier hvilke filer den rørte.
Finnes den ikke, er det ikke en feil: mappa er ikke i git, og de fleste som
klonet repoet har den ikke.

## Risks / Trade-offs

**Brukeren leser ikke linja** → Den står blant tall hun allerede leser for å
avgjøre om koblingen traff. Det er den beste plassen som finnes; garantere kan
vi ikke.

**Versjonen sier ikke hva som er endret** → Sant. Den sier bare at kopien er
eldre enn utgivelsen. Hva som skiller dem står i utgivelsesteksten, og det er
der det hører hjemme.

**En test kan ikke vise at linja er lesbar i Dynamo** → Derfor må en bevisst
gammel kopi limes inn og kjøres. Står i proposal.md under «Prøves hos
konsumenten».
