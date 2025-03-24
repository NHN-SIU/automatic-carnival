#!/usr/bin/env python3
import json
import time

import requests

# Configuration - UPDATED URLs
BASE_URL = "http://localhost:8080/api"  # Base API URL
CREATE_API_URL = f"{BASE_URL}/plugins/praksis-nhn-nautobot/samband/"  # For creation
UPDATE_API_URL = f"{BASE_URL}/plugins/praksis-nhn-nautobot/samband/"  # Base for updates

API_TOKEN = "0123456789abcdef0123456789abcdef01234567"
DATA_FILE = "test-data.json"
HEADERS = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json", "Accept": "application/json"}


def two_phase_import():
    """Import data in two phases to avoid parent relationship issues"""
    print("Loading data file...")
    with open(DATA_FILE, "r") as f:
        records = json.load(f)

    # Store original parent relationships for phase 2
    parent_relationships = {}
    name_to_uuid = {}  # Map names to their UUIDs for lookups
    for record in records:
        if "id" in record and "parents" in record and record["parents"]:
            parent_relationships[record["id"]] = record["parents"]
            # Clear parents for phase 1
            record["parents"] = []
        if "id" in record and "name" in record:
            name_to_uuid[record["name"]] = record["id"]

    # Phase 1: Create all records without parent relationships
    print(f"\nPhase 1: Creating {len(records)} records without parent relationships")
    created_ids = {}  # Store mapping of our UUIDs to API's internal IDs
    failures = 0

    for i, record in enumerate(records, 1):
        record_id = record.get("id", "Unknown")
        record_name = record.get("name", "Unknown")

        try:
            print(f"  [{i}/{len(records)}] Creating '{record_name}' (ID: {record_id})")
            response = requests.post(CREATE_API_URL, json=record, headers=HEADERS)

            if response.status_code in [200, 201]:
                print("    ✓ Success")

                # Store the API's returned ID for this record if available
                try:
                    resp_data = response.json()
                    if "id" in resp_data:
                        created_ids[record_id] = resp_data["id"]
                        print(f"    API assigned ID: {resp_data['id']}")
                    elif "uuid" in resp_data:
                        created_ids[record_id] = resp_data["uuid"]
                        print(f"    API assigned UUID: {resp_data['uuid']}")
                    else:
                        # If no ID in response, we'll retrieve all records later to match by name
                        created_ids[record_id] = record_id  # Temporarily use our UUID
                except:
                    pass  # Skip if can't parse JSON
            else:
                print(f"    ✗ Failed: Status {response.status_code}")
                print(f"      Response: {response.text}")
                failures += 1

        except Exception as e:
            print(f"    ✗ Exception: {str(e)}")
            failures += 1

    print(f"\nPhase 1 complete: {len(created_ids)} created, {failures} failed")

    # Fetch all records to get their actual IDs by name if needed
    print("\nRetrieving current records to map names to actual IDs...")
    try:
        response = requests.get(UPDATE_API_URL, headers=HEADERS)
        if response.status_code == 200:
            api_records = response.json()
            if isinstance(api_records, dict) and "results" in api_records:
                api_records = api_records["results"]

            name_to_api_id = {}
            for record in api_records:
                if "name" in record and ("id" in record or "uuid" in record):
                    record_id = record.get("uuid", record.get("id"))
                    name_to_api_id[record["name"]] = record_id
                    print(f"  Found: '{record['name']}' with ID: {record_id}")

            # Update our ID mappings where needed
            for uuid, name in [(uuid, name) for name, uuid in name_to_uuid.items()]:
                if name in name_to_api_id:
                    created_ids[uuid] = name_to_api_id[name]
    except Exception as e:
        print(f"  ✗ Error retrieving records: {str(e)}")

    # Phase 2: Update records with parent relationships
    if parent_relationships:
        print(f"\nPhase 2: Updating {len(parent_relationships)} records with parent relationships")
        update_failures = 0

        # Optional: Add a longer delay before starting Phase 2
        print("Waiting for database to synchronize...")
        time.sleep(5)

        # Convert parent UUIDs to API IDs
        updated_relationships = {}
        for record_id, parents in parent_relationships.items():
            if record_id in created_ids:
                api_record_id = created_ids[record_id]
                api_parents = []
                for parent_id in parents:
                    if parent_id in created_ids:
                        api_parents.append(created_ids[parent_id])
                if api_parents:
                    updated_relationships[api_record_id] = api_parents

        print(f"Mapped {len(updated_relationships)} records with their API IDs")

        # Try updating with API IDs
        for i, (api_record_id, api_parents) in enumerate(updated_relationships.items(), 1):
            try:
                print(f"  [{i}/{len(updated_relationships)}] Updating record {api_record_id} with parents")

                # Prepare update data with only the parents field
                update_data = {"parents": api_parents}

                # Try different methods to update
                # Method 1: Standard Django REST update
                update_url = f"{UPDATE_API_URL}{api_record_id}/"
                print(f"    Method 1: Sending PATCH to: {update_url}")
                response = requests.patch(update_url, json=update_data, headers=HEADERS)

                if response.status_code in [200, 201, 204]:
                    print("    ✓ Success with PATCH")
                    continue
                else:
                    print(f"    ✗ PATCH failed: Status {response.status_code}")
                    if response.text:
                        print(f"      Response: {response.text}")

                # Try with a bulk update endpoint
                bulk_update_url = f"{BASE_URL}/plugins/praksis-nhn-nautobot/samband/bulk_update/"
                print(f"    Method 2: Trying bulk update to: {bulk_update_url}")
                bulk_data = {"id": api_record_id, "parents": api_parents}
                response = requests.post(bulk_update_url, json=bulk_data, headers=HEADERS)

                if response.status_code in [200, 201, 204]:
                    print("    ✓ Success with bulk update")
                    continue
                else:
                    print(f"    ✗ Bulk update failed: Status {response.status_code}")
                    update_failures += 1

            except Exception as e:
                print(f"    ✗ Exception: {str(e)}")
                update_failures += 1

            # Add a small delay to prevent overwhelming the API
            time.sleep(0.2)

        print(f"\nPhase 2 complete: {len(updated_relationships) - update_failures} updated, {update_failures} failed")

    print("\nImport complete!")


if __name__ == "__main__":
    two_phase_import()
