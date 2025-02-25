# Møte 25. februar
Oppklaring av prosjekt, og presentasjon om hva sambånd er
Tilstede: gruppe + Kristian og Joakim

**Utfordringer i dag:**
- Junta som man bruker i dag for å vise sambånd avvikles snart. 
- Basert på Ruby on Rails, monolitt applikasjon. Vanskelig å vedlikeholde
- Problem med når man endrer en funksjonalitet, så kan det ødelegge andre deler av systemet
- Alt er samlet opp i en database (ulike sluttbrukere leveransedrift, support...), ønsker å splitte dette opp. 

**Om brukere:**
- Leverandører av samband (internt). Drift som skal ha oversikt over sambåndene "dette sambåndet har X status", "dette sambåndet blir levert gjennom..."
- Trenger ikke å vite alt av info i testdataen

**Løsning i dag:**
- Tabellvisning av sambånd, der man kan gå inn i et spesisfikk sambånd og få ulike tabs (generelt, utstyr, avvik...)
- Opplisting av felter fra en masterdatabase - synkronisert fra andre områder.

**Ønsker med å bruke Nautobot:**
- Synkronisert med en masterdatabase, brukeren skal ikke kunne gjøre mye med å endre det (kan eks legge til en hendelse, endre status)
- Automatisert migrasjonsprosess fra Junta (Junta gir endepunkt som leverer ut data som har samme format som testdata)
- Ulike visninger, teste hva som er mulighetene innenfor Nautobot
	- Hva leverer vi til kunder
	- Type, fra A til B, hastighet...
	- Informasjon om hva som er involvert for å levere sambåndet
- "Gi meg et raskt overblikk", hvordan er sambåndet bygd opp? (hierarki, foreldre...)
- Navnet er viktig - genereres automatisk av type og PoP
- Data kommer fra master-database, Nautobot skal stå for visningen på en fornuftig måte. 

**Hva er et sambånd (testdataen)?:**
- Det finnes flere sambåndstyper, som har endret seg over tid. Over tid blitt mer moderne fra sambånd -> linjeleveranse. 
- Kunden får levert sambånd av NHN (rett og slett en tilkobling), som kan bestå av flere linjeleveranser (intern/ekstern). Kan også leveres av en underleverandør (kostnad inn, kostnad ut)
- Sambåndet er faktiske sluttpunktene A og B
- Vises hierarkisk, sambånd/underleverandør kan ha foreldre/children. 

Vi skal lage en dashboard - filtrere basert på datoer.
Nautobot viser status, region, dato, hierarki
