# Overview of Standard Nautobot Models for Circuit Import
Importing circuits into Nautobot requires understanding several core models and their relationships. Before you can successfully import circuit records, you must ensure that all dependent objects (providers, circuit types, statuses, locations, etc.) are created. Below is an overview of the primary Circuit model, its required fields, and its dependencies on other models like Provider, Circuit Type, Status, Location, and Circuit Termination. A summary diagram/table of these relationships is also provided for clarity.

## Circuit (Primary Model)
The Circuit model represents a physical point-to-point link (a circuit) connecting two endpoints (commonly referred to as the A and Z terminations)​
Each Circuit object in Nautobot has several required fields and links to other models:

### Circuit ID 
– A unique identifier for the circuit (must be unique per provider)​
This is usually an ID or number given by the provider.
### Provider 
– The service provider that delivers the circuit (ForeignKey to a Provider object)​

Every circuit must be associated with a provider, and the combination of provider + circuit ID must be unique​


### Circuit Type 
A user-defined type/classification for the circuit (ForeignKey to a CircuitType)​
This describes the kind of service (e.g. Internet, MPLS, backhaul) and must be created in advance.
### Status 
The operational status of the circuit (ForeignKey to a Status object). Each circuit must be assigned a status (e.g. Planned, Active, Decommissioned, etc.)​ to indicate its state in its lifecycle.
### (Other Fields) 
Circuits have additional optional fields such as description, install_date (installation date), and commit_rate (bandwidth)​, and may be associated with a Tenant (to denote customer or internal tenant ownership)​.
These are not required for basic import but can be included if relevant.
### Relationships: 
The Circuit model ties into its dependencies via foreign-key relationships. For example, the Circuit has a foreign key to Provider (meaning one provider can have many circuits)​. It also links to a CircuitType and a Status in a similar one-to-many fashion. Each Circuit can further be associated with up to two Circuit Terminations (A and Z) which define where the circuit ends. Below, we detail each of these related models and what needs to be set up before importing circuits.



## Provider (Circuit Provider Dependency)
A Provider represents the organization or carrier that provides the circuit service. In Nautobot, a Provider must exist before you can assign it to a Circuit. Each circuit is associated with a single provider​, and you cannot import a circuit without referencing a valid Provider.
### Key Fields: 
At minimum, a Provider has a name (which should be unique). Providers may also have details like an ASN (Autonomous System Number), account number, and contact info, but these are optional metadata​.
### Relationship: 
One Provider can be linked to many Circuit records (one-to-many). The Circuit model stores a foreign key to the Provider​, meaning the provider is the “one” side and circuits are the “many” side of the relationship. In database terms, the Provider’s primary key is referenced on each Circuit​. Before importing circuits, make sure to create all necessary Provider objects (e.g. ISP or carrier names) that will be referenced by your circuits.

## Circuit Type (Type Dependency)
Circuit Type is an organizational model that categorizes circuits by their functional role or service type. Circuit types are completely customizable​
for example, you might define types such as Internet Transit, MPLS, Private Backhaul, Peering, etc. This model must be populated with any types you plan to use prior to importing circuits.
### Key Fields: 
CircuitType typically has a name (e.g. "Internet", "MPLS") and possibly a description. The name is what you use to assign a type to each circuit.
### Relationship: 
One CircuitType can classify many circuits (one-to-many relationship). Each Circuit holds a foreign key to a CircuitType​. This means the circuit “belongs” to that type category. Ensure that all required CircuitType entries are created in Nautobot before import. If a circuit in your import data has a type that doesn’t exist in Nautobot, you’ll need to add that type first.

## Status (Status Dependency)
Status in Nautobot represents the state of an object. Circuits use the Status model to indicate their operational state or lifecycle stage. By default, Nautobot provides a set of common circuit statuses​, including: Planned, Provisioning, Active, Offline, Deprovisioning, and Decommissioned. Each circuit must be assigned a status value​.
### Key Fields: 
A Status object has a name (and a slug) and is associated with a certain content type (in this case, circuits). The default statuses mentioned above are typically pre-loaded in Nautobot, but you can create custom statuses if needed.
### Relationship: 
Status is a generic model, but for circuits it works like a foreign key relationship – each Circuit references one Status (the “status” field on Circuit links to a Status record)​. This is effectively a one-to-many relationship (one status can apply to many different circuits). Usually, you won’t need to create new Status objects if the defaults suffice; just ensure you use one of the existing statuses when importing. If you have a custom workflow that requires a new status value, define it in Nautobot’s Statuses section before assigning it to circuits.


## Location (Sites/Locations for Circuit Endpoints)
A Location in Nautobot denotes a physical site or area where equipment is located (in Nautobot v2.x, the Location model encompasses what were sites/regions in earlier versions). Circuits are connections between two endpoints, so you typically have two locations involved: often referred to as POP A and POP B (Point of Presence A and B), or simply the A-side and Z-side locations of the circuit. These location objects (e.g. data center sites, campus, building, etc.) must exist to properly define the circuit endpoints.
### Key Fields: 
A Location has a name and a hierarchy (it could be a site or a child location within a site depending on your Nautobot setup). For circuit purposes, you will at least need the site or location that represents each end of the circuit.
### Relationship: 
Location itself is not directly referenced on the Circuit model; instead, it is linked through the Circuit Termination model (discussed next). Each Circuit Termination will point to a Location. In practice, this means before importing circuits (and their terminations), you should create the Location records for any site or facility that appears as an A or Z endpoint (pop_A/pop_B) in your data. For example, if a circuit goes between Site X and Site Y, both of those site locations need to be in Nautobot ahead of time.
### Provider Network (Alternative Endpoint): 
In cases where a circuit terminates not at one of your own Locations but at a provider’s network (a cloud or undefined network segment on the provider side), Nautobot uses the ProviderNetwork model to represent that “cloud” endpoint​. If your circuit’s far end is a provider network (e.g. an MPLS cloud), you should create a ProviderNetwork object for it and associate it with the Provider. A circuit can terminate to either a Location or a ProviderNetwork​. (If the import data uses a provider network as an endpoint, ensure those are created beforehand as well.)

## Circuit Termination (A and Z Endpoints)
Circuit Termination is the model that defines each endpoint of a circuit. Nautobot models circuit endpoints separately so that a Circuit can have up to two terminations, labeled A and Z​ (these correspond to what we called pop_A and pop_B). Each Circuit Termination object describes one end of the circuit: where it terminates and the characteristics of that end.
### Key Fields: A CircuitTermination includes:
#### Circuit 
– A reference to the Circuit that this termination belongs to (ForeignKey to the Circuit model).
#### Termination Side (A or Z) 
– A field indicating whether this is the A-side or Z-side of the circuit. Nautobot uses these labels to distinguish the two ends​. (In other words, one termination will be marked “A”, the other “Z”. This effectively serves as the “role” of the endpoint in the circuit’s context – one end vs the other.)
#### Site/Location or Provider Network 
– A foreign key to the Location or to a ProviderNetwork where this end is located​. (In Nautobot 2.x, this is typically a Location object. In older data models or certain contexts it could be a Site or a ProviderNetwork. Only one of these will be set for a given termination: e.g. A-side might be a Location, Z-side might be a ProviderNetwork.)
#### Port Speed 
– The capacity of the circuit at this termination (e.g. 1000 Mbps). This is required for each termination​.
#### Upstream Speed (optional) 
– If the circuit is asymmetric, an upstream speed can be recorded (optional field).
#### XConnect ID, Cable ID, etc. (optional) 
– Fields to record cross-connect or patch panel details for the physical interconnection, if applicable. These are optional and used for documentation.
### Relationship: 
Each Circuit Termination is linked to one Circuit (many terminations per circuit, though constrained to at most two). In the database, the CircuitTermination has a foreign key to the Circuit, and also a foreign key to a Location or ProviderNetwork. This effectively means:
- A Circuit can have 0, 1, or 2 related CircuitTermination objects (0 if the circuit is not yet mapped to any endpoint, 1 if only one side is known, 2 for a complete circuit with both ends modeled)​.
- A Location or ProviderNetwork can have many CircuitTerminations (for example, many circuits might terminate at the same site or the same provider network cloud).
- The two terminations on a given circuit must have distinct sides (one “A” and one “Z” – Nautobot enforces that a circuit cannot have two A-sides or two Z-sides​). This ensures a one-to-one pairing between Circuit and side label, essentially making the A/Z assignment a unique role per circuit.

When importing circuits, you may need to import or create Circuit Terminations separately (Nautobot’s import might treat circuit terminations as a separate object list). The important part is that the data for each circuit’s endpoints (site/location or provider network, and speeds) is accounted for. In practice, you will create the Circuit object first (with its provider, type, status, ID, etc.), and then create two CircuitTermination entries for it (one for each end). Ensure the endpoint Locations or ProviderNetworks referenced by those terminations exist in Nautobot. For example, to fully define a circuit between “Site A” and “Site B”, you would:
1. Create “Site A” and “Site B” as Location objects.
2. Create the Provider and Circuit Type (if not already existing).
3. Create the Circuit with a unique circuit ID, linking it to the Provider, Circuit Type, and a Status (e.g. Active).
4. Create a CircuitTermination for the A side: link it to the Circuit, assign side=A, set the site to “Site A” (and port speed).
5. Create a CircuitTermination for the Z side: link it to the same Circuit, assign side=Z, set the site to “Site B” (and port speed).
After these steps, the circuit will be fully defined connecting Site A (pop_A) to Site B (pop_B) via that provider. (If one end was a provider network, you would attach that end to a ProviderNetwork instead of a Site/Location.)

## Relationships Summary Diagram/Table
To clarify the relationships between these models, below is a summary of how the Nautobot data model ties them together. All relationships are ForeignKey (one-to-many) unless noted otherwise, which means the "one" side must exist first and can be linked to many on the "many" side​:
Model	Related Model	Relationship Type	Notes on Relationship
Provider	Circuit	One-to-Many (ForeignKey)	Provider → Circuit: One provider can have many circuits. Each Circuit references a single Provider​.
Circuit Type	Circuit	One-to-Many (ForeignKey)	CircuitType → Circuit: One circuit type can classify many circuits. Each Circuit has one type.
Status	Circuit	One-to-Many (ForeignKey)	Status → Circuit: One status value (e.g. “Active”) can apply to many circuits. Each Circuit has one status.
Circuit	CircuitTermination	One-to-Many (ForeignKey)	Circuit → CircuitTermination: A circuit can have 0–2 terminations. Each termination is linked to one Circuit. (In Nautobot’s schema, circuit terminates are separate objects referencing the circuit.)
Location (Site)	CircuitTermination	One-to-Many (ForeignKey)	Location → CircuitTermination: A location (site) can be the endpoint for many circuit terminations. Each CircuitTermination references one Location or one ProviderNetwork​.
ProviderNetwork	CircuitTermination	One-to-Many (ForeignKey)	ProviderNetwork → CircuitTermination: A provider network can serve as an endpoint for many circuits. Each CircuitTermination references either a Location or a ProviderNetwork (but not both)​.
CircuitTermination	CircuitTermination (peer)	One-to-One (A vs Z)	A–Z Pair: Within a given Circuit, there can be at most two terminations – one labeled A, one labeled Z​. This essentially forms a one-to-one pairing of two termination records per circuit (when both exist). Nautobot enforces unique A/Z per circuit​.
Diagram Note: In Nautobot’s database schema, these associations are realized via foreign keys​. For example, the Circuit table has a foreign key field for Provider (pointing to the Provider table) to indicate which provider a circuit belongs to. Similarly, the CircuitTermination table has fields for the linked Circuit and for the attached Location or ProviderNetwork. This structure means you must create the “one” side objects (Provider, CircuitType, Status, Location, etc.) before referencing them in the circuit import.By setting up the Provider(s), Circuit Type(s), and Location(s) beforehand and using the appropriate Status, you ensure that your circuit import will succeed. Each imported Circuit will then correctly link to its provider and type, have a valid status, and can be associated with termination endpoints (pop A/B) that are defined in Nautobot. Following this model hierarchy will result in a consistent and well-structured representation of circuits in Nautobot’s database, mirroring real-world connectivity in a logical way.