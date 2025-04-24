# Grafvisning

Målet med denne funksjonaliteten er å visualisere relasjoner mellom objekter i et nettverk, som for eksempel foreldre-barn-relasjoner, på en intuitiv og brukervennlig måte.

## Intitiell undersøkelse

Nautobot/Django har ingen iboende funksjonalitet for å visualisere nettverk/graf.
Dermed trenger man en tredjepartsbibliotek. Arbeidet har inkludert både backend- og frontend-komponenter for å hente, prosessere og vise data i et grafisk format.

Undersøkte litt med ren Python bibliotek - der den håndterer visualiseringen. Vs. Javascript, der man må lage funksjoner for å lage nodene.
Endte opp til slutt med en Javascript bibliotek D3js (https://d3js.org/), som har stor fleksibilitet ift. datavisualisering.

Lagde først API-endepunkt (/hierarchy) som henter ut både foreldre og barn til en gitt node ID, med en spesifisert dybde.

Gikk etterhvert over til en intern servicemodul/utils som gjør det samme med Breadth First Search, og bruk av innebygd Django/Nautobot funksjonalitet (objects.filter). Dette gjorde det noe lettere med å håndtere urls og endepunktene.

- Fordel: siden testdataen/datamodellen har bare en parents-field, så trenger man ikke å anta en til field for children.

## Vekk fra D3

Etterhvert som jeg implementerte grafvisning gjennom D3, så innså jeg hvor mye jobb det er hvis man skal visualisere en gitt mengde noder
uten å fokusere på en inviduell node. For eksempel hvis man ønsket å gå fra tabellvisning med # antall noder, og bygge opp ett nettverksvisning mellom dem.
I tillegg var det litt problemer ift. å få nodene til å render korrekt under og ovenfor, eks. foreldrenes forelder.

Dermed undersøkte jeg tilbake til andre biblioteker, og kom fram til til Python biblioteket NetworkX (https://networkx.org/), og Javacript biblioteket Vis.js (https://visjs.github.io/vis-network/docs/network/index.html). Da separerer man oppbyggningen av data ift. noder og edges gjennom NetworkX. Og Vis.js håndterer layout og visualisering. Vis.js tilbyr funksjonalitet for hierarkisk layout, som er ideelt for å vise foreldre-barn-relasjoner.

## Videre arbeid

- **Tilpasning av layout:** Utforske flere layout-alternativer i Vis.js for å gjøre grafen mer oversiktlig, spesielt ved mange noder.
