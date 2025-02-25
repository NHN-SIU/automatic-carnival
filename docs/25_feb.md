# Møtenotater - Migrasjon fra Junta til Nautobot

## Utfordringer med dagens løsning
- **Junta** brukes i dag for å vise sambånd, men avvikles snart.
- **Monolittisk applikasjon** basert på Ruby on Rails, vanskelig å vedlikeholde.
- **Endringer i funksjonalitet** kan føre til uforutsette feil i andre deler av systemet.
- **Sentralisert database** for ulike sluttbrukere (leveransedrift, support, osv.), ønskes splittet opp.

## Om brukerne
- **Leverandører av samband (internt)**
- **Drift** som skal ha oversikt over sambåndenes status, leveransemetoder osv.
- **Begrenset tilgang** til testdata – kun nødvendig informasjon.

## Dagens løsning
- **Tabellvisning av sambånd**, med mulighet for å gå inn i et spesifikt sambånd og se ulike faner:
  - Generelt
  - Utstyr
  - Avvik
- **Synkronisering** av data fra en masterdatabase.

## Ønsker med Nautobot
- **Synkronisert med masterdatabase**
  - Brukeren kan kun gjøre begrensede endringer (f.eks. legge til en hendelse, endre status).
- **Automatisert migrasjonsprosess** fra Junta
  - Junta eksponerer et API-endepunkt med data i samme format som testdata.
- **Utforske mulighetene i Nautobot:**
  - Oversikt over leveranser til kunder.
  - Informasjon om type, fra A til B, hastighet, involvert utstyr osv.
  - Hierarkisk visning av sambånd.
  - Automatisk genererte navn basert på type og PoP.
- **Fornuftig visualisering** av data fra masterdatabase.

## Hva er et sambånd? (basert på testdata)
- Flere **sambåndstyper**, som har utviklet seg over tid.
- Overgangen fra **sambånd** til **linjeleveranser**.
- Kunden får levert et **sambånd** av NHN, som kan bestå av flere **linjeleveranser** (interne/eksterne).
- **Underleverandører** kan være involvert (kostnad inn/ut).
- **Hierarkisk struktur**, hvor et sambånd kan ha overordnede eller underordnede forbindelser.

## Dashboard-ønsker
- **Filtrering basert på datoer**.
- **Visning av:**
  - Status
  - Region
  - Dato
  - Hierarki

---
**Målet:** Bygge et dashboard i Nautobot som gir raskt overblikk over sambånd, med automatisert migrasjon fra Junta og en bedre organisering av data.

