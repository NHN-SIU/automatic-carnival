#!/usr/bin/env python3
"""
Generate realistic dummy connection data for testing.

This script creates a large number of simulated network connections
with realistic variations in locations, vendors, bandwidths, etc.
"""

import json
import random
import uuid
from datetime import datetime, timedelta

# Configuration
OUTPUT_FILE = "large-test-data.json"
NUM_RECORDS = 1000  # Number of records to generate

# Lists of realistic values for various fields
LOCATIONS = [
    {"name": "Oslo", "geo": ["59.91", "10.75"]},
    {"name": "Bergen", "geo": ["60.39", "5.32"]},
    {"name": "Trondheim", "geo": ["63.43", "10.39"]},
    {"name": "Stavanger", "geo": ["58.97", "5.73"]},
    {"name": "Tromsø", "geo": ["69.65", "18.96"]},
    {"name": "Kristiansand", "geo": ["58.16", "8.00"]},
    {"name": "Drammen", "geo": ["59.74", "10.20"]},
    {"name": "Fredrikstad", "geo": ["59.21", "10.94"]},
    {"name": "Sandnes", "geo": ["58.85", "5.73"]},
    {"name": "Bodø", "geo": ["67.28", "14.40"]},
    {"name": "Ålesund", "geo": ["62.47", "6.15"]},
    {"name": "Haugesund", "geo": ["59.41", "5.27"]},
    {"name": "Tønsberg", "geo": ["59.27", "10.42"]},
    {"name": "Moss", "geo": ["59.43", "10.66"]},
    {"name": "Sandefjord", "geo": ["59.13", "10.22"]}
]

VENDORS = ["Telenor", "Telia", "Broadnet", "GlobalConnect", "Ice", "NextGenTel", "Altibox", "Lyse", "Eidsiva", "NorNett"]

CONNECTION_TYPES = ["Internet", "WAN", "MPLS", "Metro Ethernet", "Dark Fiber", "SD-WAN", "VPN", "Backbone", "Point-to-point"]

TRANSPORT_TYPES = ["Fiber", "Copper", "Wireless", "Satellite", "Microwave", "Coaxial", "5G", "DSL", "Broadband"]

STATUSES = [
    {"name": "Active", "weight": 60},  # 60% chance of being Active
    {"name": "Planned", "weight": 20},  # 20% chance of being Planned
    {"name": "Decommissioned", "weight": 10},  # 10% chance of being Decommissioned
    {"name": "Under Construction", "weight": 10}  # 10% chance of being Under Construction
]

BANDWIDTHS = [
    {"up": 100, "down": 100, "string": "100 Mbps symmetrical"},
    {"up": 250, "down": 250, "string": "250 Mbps symmetrical"},
    {"up": 500, "down": 500, "string": "500 Mbps symmetrical"},
    {"up": 1000, "down": 1000, "string": "1 Gbps symmetrical"},
    {"up": 2000, "down": 2000, "string": "2 Gbps symmetrical"},
    {"up": 5000, "down": 5000, "string": "5 Gbps symmetrical"},
    {"up": 10000, "down": 10000, "string": "10 Gbps symmetrical"},
    {"up": 100, "down": 50, "string": "100/50 Mbps"},
    {"up": 250, "down": 100, "string": "250/100 Mbps"},
    {"up": 500, "down": 200, "string": "500/200 Mbps"}
]

LOCATION_TYPES = ["Data Center", "Office", "Hospital", "Clinic", "Regional Office", "Edge Site", "Branch Office"]

CATEGORIES = ["Data Center", "Primary Site", "Secondary Site", "End User", "Edge Site", "Backbone Node"]

# Functions to generate realistic values
def generate_random_date(start_date, end_date=None):
    """Generate a random date between start_date and end_date."""
    if end_date is None:
        end_date = datetime.now()
    
    # Make sure end_date is after start_date
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")
    
    if end_date < start_date:
        # Swap if dates are in wrong order
        start_date, end_date = end_date, start_date
    
    # Add at least 1 day if dates are the same
    if end_date == start_date:
        end_date = start_date + timedelta(days=1)
    
    time_diff = (end_date - start_date).days
    random_days = random.randint(0, max(0, time_diff))
    return (start_date + timedelta(days=random_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

def generate_geo_variation(base_lat, base_lon, max_delta=0.05):
    """Generate a slightly modified geo coordinate for variety."""
    lat_delta = random.uniform(-max_delta, max_delta)
    lon_delta = random.uniform(-max_delta, max_delta)
    new_lat = float(base_lat) + lat_delta
    new_lon = float(base_lon) + lon_delta
    return f"{new_lat:.4f}° N, {new_lon:.4f}° E", f"https://maps.google.com/?q={new_lat},{new_lon}"

def get_weighted_status():
    """Return a status based on weighted probability."""
    weights = [status["weight"] for status in STATUSES]
    return random.choices([status["name"] for status in STATUSES], weights=weights, k=1)[0]

def generate_connection_data():
    """Generate a single random connection record."""
    # Pick random locations for A and B ends (ensuring they're different)
    loc_a_idx = random.randrange(len(LOCATIONS))
    loc_b_idx = random.randrange(len(LOCATIONS))
    while loc_b_idx == loc_a_idx:
        loc_b_idx = random.randrange(len(LOCATIONS))
    
    loc_a = LOCATIONS[loc_a_idx]
    loc_b = LOCATIONS[loc_b_idx]
    
    # Generate unique geo coordinates for specific points within these locations
    pop_a_geo, pop_a_map = generate_geo_variation(loc_a["geo"][0], loc_a["geo"][1])
    pop_b_geo, pop_b_map = generate_geo_variation(loc_b["geo"][0], loc_b["geo"][1])
    
    # Pick a random vendor
    vendor = random.choice(VENDORS)
    
    # Pick a random connection type
    conn_type = random.choice(CONNECTION_TYPES)
    
    # Pick a random transport type
    transport_type = random.choice(TRANSPORT_TYPES)
    
    # Pick a random status with weighted probabilities
    status = get_weighted_status()
    
    # Pick a random bandwidth
    bandwidth = random.choice(BANDWIDTHS)
    
    # Generate realistic costs
    base_cost = random.uniform(5000, 50000)
    cost_in = round(base_cost, 2)
    markup = random.uniform(1.1, 1.4)
    cost_out = round(cost_in * markup, 2)
    dekningsbidrag = round(cost_out - cost_in, 2)
    dekningsgrad = round((dekningsbidrag / cost_out) * 100, 2)
    
    # Generate realistic dates
    base_date = datetime(2020, 1, 1)
    now = datetime.now()
    
    # Start with order date
    order_date = generate_random_date(base_date, now - timedelta(days=60))
    
    # Ensure desired_delivery_date is after order_date
    order_date_dt = datetime.strptime(order_date, "%Y-%m-%dT%H:%M:%SZ")
    desired_delivery_date = generate_random_date(
        order_date_dt + timedelta(days=30),
        order_date_dt + timedelta(days=90)
    )
    
    # Use different date logic based on status
    if status == "Active":
        # Ensure actually_delivery_date is between order_date and desired_delivery_date (+10 days slack)
        desired_delivery_date_dt = datetime.strptime(desired_delivery_date, "%Y-%m-%dT%H:%M:%SZ")
        actually_delivery_date = generate_random_date(
            order_date_dt + timedelta(days=20),
            desired_delivery_date_dt + timedelta(days=10)
        )
        
        # Ensure install_date is after actually_delivery_date
        actually_delivery_date_dt = datetime.strptime(actually_delivery_date, "%Y-%m-%dT%H:%M:%SZ")
        install_date = generate_random_date(
            actually_delivery_date_dt,
            actually_delivery_date_dt + timedelta(days=3)
        )
        
        # Ensure live_date is after install_date
        install_date_dt = datetime.strptime(install_date, "%Y-%m-%dT%H:%M:%SZ")
        live_date = generate_random_date(
            install_date_dt,
            install_date_dt + timedelta(days=2)
        )
        
        # Updated at is sometime between live_date and now
        live_date_dt = datetime.strptime(live_date, "%Y-%m-%dT%H:%M:%SZ")
        updated_at = generate_random_date(live_date_dt, now)
        
        created_at = order_date
        termination_date = None
        termination_order_date = None
        
    # For decommissioned connections
    elif status == "Decommissioned":
        actually_delivery_date = generate_random_date(
            datetime.strptime(order_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=20),
            datetime.strptime(desired_delivery_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=10)
        )
        install_date = generate_random_date(
            datetime.strptime(actually_delivery_date, "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime(actually_delivery_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=3)
        )
        live_date = generate_random_date(
            datetime.strptime(install_date, "%Y-%m-%dT%H:%M:%SZ"),
            datetime.strptime(install_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=2)
        )
        termination_order_date = generate_random_date(
            datetime.strptime(live_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=180),
            datetime.strptime(live_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=720)
        )
        termination_date = generate_random_date(
            datetime.strptime(termination_order_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=14),
            datetime.strptime(termination_order_date, "%Y-%m-%dT%H:%M:%SZ") + timedelta(days=30)
        )
        created_at = order_date
        updated_at = termination_date
    # For planned connections
    elif status == "Planned":
        created_at = order_date
        updated_at = generate_random_date(
            datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ"),
            now
        )
        actually_delivery_date = None
        install_date = None
        live_date = None
        termination_date = None
        termination_order_date = None
    # For under construction
    else:
        created_at = order_date
        updated_at = generate_random_date(
            datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ"),
            now
        )
        actually_delivery_date = None
        install_date = None
        live_date = None
        termination_date = None
        termination_order_date = None
    
    # Generate a believable connection name
    name_prefix = loc_a["name"][:3].upper()
    connection_purpose = random.choice(["Primary", "Backup", "Tertiary", "Core", "Edge"])
    connection_name = f"{loc_a['name']} to {loc_b['name']} {conn_type} {connection_purpose}"
    
    location_type = random.choice(LOCATION_TYPES)
    pop_a_category = random.choice(CATEGORIES)
    pop_b_category = random.choice(CATEGORIES)
    
    # Generate unique reference numbers
    samb_nr = f"NHN-{name_prefix}-{str(random.randint(1000, 9999))}"
    smbnr_nhn = f"NHN{str(random.randint(1000, 9999))}"
    smbnr_orig = random.randint(10000, 99999)
    
    # Generate random room locations
    pop_a_room = f"Room-{random.choice(['A', 'B', 'C'])}-{random.randint(100, 999)}"
    pop_b_room = f"Room-{random.choice(['X', 'Y', 'Z'])}-{random.randint(100, 999)}"
    
    # Use the record's index as part of the UUID to ensure uniqueness
    record_uuid = str(uuid.uuid4())
    
    return {
        "name": connection_name,
        "name_prefix": name_prefix,
        "type": conn_type,
        "type_id": random.randint(1, 9),
        "status": status,
        "status_id": {"Active": 1, "Planned": 2, "Decommissioned": 3, "Under Construction": 4}[status],
        "bandwidth_up": bandwidth["up"],
        "bandwidth_down": bandwidth["down"],
        "bandwidth_string": bandwidth["string"],
        "connection_url": f"https://nhn.no/connections/{name_prefix.lower()}-{random.randint(100, 999)}",
        "vendor": vendor,
        "vendor_id": VENDORS.index(vendor) + 1,
        "cost_in": cost_in,
        "cost_out": cost_out,
        "created_at": created_at,
        "updated_at": updated_at,
        "actually_delivery_date": actually_delivery_date,
        "desired_delivery_date": desired_delivery_date,
        "dekningsbidrag": dekningsbidrag,
        "dekningsgrad": dekningsgrad,
        "details_included": random.choice([True, True, True, False]),  # 75% True
        "express_cost": random.choice([0.0, 0.0, 0.0, round(random.uniform(5000, 20000), 2)]),  # 75% Zero
        "initial_cost": round(random.uniform(50000, 150000), 2),
        "install_date": install_date,
        "live_date": live_date,
        "location": loc_a["name"],
        "location_id": LOCATIONS.index(loc_a) + 1,
        "location_type": location_type,
        "order_date": order_date,
        "order_delivery_date": desired_delivery_date,
        "parents": [],  # We'll set some parent relationships later
        "pop_a_address_string": f"NHN {pop_a_category}, {random.randint(1, 999)} {loc_a['name']}",
        "pop_a_category": pop_a_category,
        "pop_a_geo_string": pop_a_geo,
        "pop_a_map_url": pop_a_map,
        "pop_a_room": pop_a_room,
        "pop_b_address_string": f"{vendor} {pop_b_category}, {random.randint(1, 999)} {loc_b['name']}",
        "pop_b_category": pop_b_category,
        "pop_b_geo_string": pop_b_geo,
        "pop_b_map_url": pop_b_map,
        "pop_b_room": pop_b_room,
        "sambandsnummer": samb_nr,
        "smbnr_nhn": smbnr_nhn,
        "smbnr_orig": smbnr_orig,
        "smbnr_prefix": "NHN",
        "start_invoice_date": live_date,  # Assuming billing starts when connection goes live
        "termination_date": termination_date,
        "termination_order_date": termination_order_date,
        "transporttype": transport_type,
        "transporttype_id": TRANSPORT_TYPES.index(transport_type) + 1,
        "id": record_uuid,
        "tags": [],
        "custom_fields": {}
    }


def main():
    """Generate a large number of connection records and save to JSON file."""
    print(f"Generating {NUM_RECORDS} connection records...")
    records = []
    
    for i in range(NUM_RECORDS):
        record = generate_connection_data()
        records.append(record)
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1} records...")
    
    # Add some parent-child relationships (for approximately 30% of records)
    potential_parents = records[:int(NUM_RECORDS * 0.3)]  # Use the first 30% as potential parents
    child_candidates = records[int(NUM_RECORDS * 0.3):]  # Use the rest as potential children
    
    for child in random.sample(child_candidates, int(NUM_RECORDS * 0.2)):  # Make 20% actual children
        # Assign 1-3 parents
        num_parents = random.randint(1, 3)
        parents = random.sample(potential_parents, min(num_parents, len(potential_parents)))
        child["parents"] = [parent["id"] for parent in parents]
    
    # Save to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)
    
    print(f"Generated {len(records)} records with {sum(1 for r in records if r['parents'])} parent relationships.")
    print(f"Data saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()