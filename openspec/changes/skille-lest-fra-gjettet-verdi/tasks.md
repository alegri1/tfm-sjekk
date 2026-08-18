## 1. Formtesten

- [x] 1.1 Legg til en funksjon som avgjør om en streng er gjenkjennelig som en
      TFM-ID: høyst én av strukturmarkørene `++`, `=` og `-` mangler. Markørene
      hentes fra samme sted parseren bruker dem, ikke som en ny liste.
- [x] 1.2 Test den mot de fjorten strengene fra utforskingen — fabrikat, modell,
      vekt, kommentar, internt merke, kurstekst, bare komponent, bare system, og
      fem ødelagte TFM-former. Alt søppel forkastes, alle de ødelagte godtas.

## 2. Verdiuttrekket

- [x] 2.1 La gjetningsveien («riktig egenskapssett, ingen konfigurert felt») bare
      godta en verdi som består formtesten. Gjelder bare denne veien; en verdi i
      det konfigurerte feltet skal aldri forkastes.
- [x] 2.2 Test at `Systemair` i et egenskapssett uten konfigurert felt gir
      «mangler TFM-verdi», og at `++11508=3600.001.04-JVZ001` samme sted godtas og
      gir syntaksfunn.
- [x] 2.3 Test at rekkefølgen egenskapene har i fila ikke endrer hva som leses.
- [x] 2.4 Utvid `IfcObjekt` med proveniens: hvilken strategi som traff, og hvilket
      egenskapssett og felt verdien ble lest fra. Feltene må være picklebare.
- [x] 2.5 Før proveniensen videre til `Funn`, på samme måte som `posisjon`.
- [x] 2.6 Test at federering over prosessgrensa bevarer proveniensen.

## 3. Konfigurasjon

- [x] 3.1 Fjern `Type` fra standardverdien for `egenskapsnavn_type`.
- [x] 3.2 Test at et objekt med `Pset_ManufacturerTypeInformation/Type` og ingen
      TFM-type ikke får noen TFM-type.
- [x] 3.3 Oppdater `tfm-sjekk.toml` i repoet så eksempelet viser den nye lista, med
      en kommentar om hvorfor generiske feltnavn ikke hører hjemme der.

## 4. MMI

- [x] 4.1 Stram normaliseringen: verdien må være en nivåangivelse — et tall,
      eventuelt med `MMI` foran. Vilkårlig tekst med siffer i er ikke et nivå.
- [x] 4.2 Test at `MMI 300`, `mmi300` og `300` gir nivå 300, og at
      `sjekket av RIE 12.03` ikke blir til `1203`.
- [x] 4.3 Test at en forkastet MMI-verdi ikke teller som at fila bruker MMI, og at
      de øvrige objektene da ikke får funn om manglende MMI.

## 5. Meldinger

- [x] 5.1 La feilforklaringen bruke formtesten: en verdi som ikke er gjenkjennelig
      som TFM-ID skal beskrives som fremmed, ikke som om den mangler en bestemt del.
- [x] 5.2 Test at `Systemair` i det konfigurerte feltet ikke lenger gir «Mangler
      «++»-delen», og at `++115080-3600.001.04` fortsatt gjør det.
- [x] 5.3 La et funn som hviler på en verdi lest utenfor den konfigurerte veien
      navngi egenskapssettet og feltet verdien faktisk kom fra. Detaljen hører i
      beskrivelsen, ikke i BCF-tittelen, som kuttes på 100 tegn.
- [x] 5.4 Test at BCF-tittelen fortsatt er lesbar og at beskrivelsen bærer opphavet.

## 6. Dokumentasjon

- [x] 6.1 Beskriv i README hvordan verktøyet finner TFM-verdien, hvilke tre
      strategier som finnes, og hva som skjer når verdien ikke er gjenkjennelig.
- [x] 6.2 Noter den brytende endringen i `egenskapsnavn_type` der en bruker vil se
      den.

## 7. Prøving der det skal brukes

- [x] 7.1 Kjør verktøyet på en ekte IFC-fil med geometri og virkelige
      egenskapssett — helst en fagmodell fra et prosjekt, ellers en offentlig fil
      fra buildingSMART.
- [x] 7.2 Sammenlign hvilke verdier som ble lest, forkastet og gjettet mot hva som
      faktisk står i fila. Noter hvilke nesten-treff som forekom, som svar på det
      åpne spørsmålet i design.
