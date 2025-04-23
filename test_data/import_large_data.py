#!/usr/bin/env python3
"""
Import a large dataset of connection records efficiently.

This script imports a large number of connection records into the API,
with optimizations for handling large datasets efficiently.
"""

import concurrent.futures
import json
import time

import requests

# Configuration
BASE_URL = "http://localhost:8080/api"  # Base API URL
CREATE_API_URL = f"{BASE_URL}/plugins/praksis-nhn-nautobot/samband/"  # For creation
UPDATE_API_URL = f"{BASE_URL}/plugins/praksis-nhn-nautobot/samband/"  # Base for updates

API_TOKEN = "0123456789abcdef0123456789abcdef01234567"  # noqa: S105
DATA_FILE = "large-test-data.json"  # The file with our generated data
HEADERS = {"Authorization": f"Token {API_TOKEN}", "Content-Type": "application/json", "Accept": "application/json"}

# Concurrency settings
MAX_WORKERS = 5  # Number of parallel workers for API calls
CHUNK_SIZE = 20  # Number of records to process in each batch
RETRY_ATTEMPTS = 3  # Number of retries for failed requests
RETRY_DELAY = 1  # Delay between retries in seconds

# Progress tracking
created_ids = {}  # Store mapping of our UUIDs to API's internal IDs
failures = 0
parent_relationships = {}


def create_record(record):
    """Create a single record via API."""
    record_id = record.get("id", "Unknown")
    record_name = record.get("name", "Unknown")

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.post(CREATE_API_URL, json=record, headers=HEADERS, timeout=10)

            if response.status_code in [200, 201]:
                # Store the API's returned ID for this record if available
                try:
                    resp_data = response.json()
                    if "id" in resp_data:
                        return record_id, resp_data["id"], True
                    elif "uuid" in resp_data:
                        return record_id, resp_data["uuid"], True
                    else:
                        return record_id, record_id, True  # Use our UUID temporarily
                except Exception as e:
                    print(f"Failed to parse response JSON for {record_name}: {e}")
                    return record_id, None, False
            else:
                print(f"Failed to create {record_name} (Status {response.status_code}): {response.text[:100]}")
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return record_id, None, False

        except Exception as e:
            print(f"Exception creating {record_name}: {str(e)}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
                continue
            return record_id, None, False

    return record_id, None, False


def process_chunk(chunk):
    """Process a chunk of records in parallel."""
    results = []

    # Store parent relationships before removing them for first phase
    local_parent_relationships = {}
    for record in chunk:
        if "id" in record and "parents" in record and record["parents"]:
            local_parent_relationships[record["id"]] = record["parents"].copy()
            record["parents"] = []

    # Create records without parent relationships
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_record = {executor.submit(create_record, record): record for record in chunk}

        for future in concurrent.futures.as_completed(future_to_record):
            record = future_to_record[future]
            try:
                record_id, api_id, success = future.result()
                results.append((record_id, api_id, success))
            except Exception as e:
                print(f"Exception processing record {record.get('name', 'unknown')}: {str(e)}")
                results.append((record.get("id", "unknown"), None, False))

    return results, local_parent_relationships


def update_parent_relationship(record_id, parent_ids):
    """Update a record with its parent relationships."""
    update_data = {"parents": parent_ids}
    update_url = f"{UPDATE_API_URL}{record_id}/"

    for attempt in range(RETRY_ATTEMPTS):
        try:
            response = requests.patch(update_url, json=update_data, headers=HEADERS, timeout=10)

            if response.status_code in [200, 201, 204]:
                return True
            else:
                print(
                    f"Failed to update parents for {record_id} (Status {response.status_code}): {response.text[:100]}"
                )
                if attempt < RETRY_ATTEMPTS - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                return False

        except Exception as e:
            print(f"Exception updating parents for {record_id}: {str(e)}")
            if attempt < RETRY_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY)
                continue
            return False

    return False


def main():
    """Import data in two phases with optimizations for large datasets."""
    global created_ids, failures, parent_relationships

    print("Loading data file...")
    with open(DATA_FILE, "r") as f:
        records = json.load(f)

    print(f"\nPhase 1: Creating {len(records)} records without parent relationships")

    # Process records in chunks
    total_chunks = (len(records) + CHUNK_SIZE - 1) // CHUNK_SIZE  # Ceiling division

    for i in range(0, len(records), CHUNK_SIZE):
        chunk = records[i : i + CHUNK_SIZE]
        print(f"Processing chunk {(i//CHUNK_SIZE)+1}/{total_chunks} ({len(chunk)} records)...")

        results, chunk_parent_relationships = process_chunk(chunk)

        # Update our tracking variables
        for record_id, api_id, success in results:
            if success and api_id:
                created_ids[record_id] = api_id
            else:
                failures += 1

        # Update parent relationships tracker
        parent_relationships.update(chunk_parent_relationships)

        # Add a brief pause between chunks to avoid overwhelming the API
        time.sleep(0.5)

    print(f"\nPhase 1 complete: {len(created_ids)} created, {failures} failed")

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

        # Process parent relationship updates
        processed = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_record = {
                executor.submit(update_parent_relationship, record_id, parent_ids): record_id
                for record_id, parent_ids in updated_relationships.items()
            }

            for future in concurrent.futures.as_completed(future_to_record):
                record_id = future_to_record[future]
                processed += 1

                if processed % 50 == 0:
                    print(f"Updated {processed}/{len(updated_relationships)} parent relationships...")

                try:
                    success = future.result()
                    if not success:
                        update_failures += 1
                except Exception as e:
                    print(f"Exception updating parent relationship for {record_id}: {str(e)}")
                    update_failures += 1

        print(f"\nPhase 2 complete: {len(updated_relationships) - update_failures} updated, {update_failures} failed")

    print("\nImport complete!")


if __name__ == "__main__":
    main()
