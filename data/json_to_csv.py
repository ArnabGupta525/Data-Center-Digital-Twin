#!/usr/bin/env python3
"""
Convert grouped JSON telemetry data into CSV.
Input:  data/sample.json
Output: data/sample.csv
"""

import json
import csv
import os

INPUT = "data/sample.json"
OUTPUT = "data/sample.csv"

def flatten_record(record):
    """Flatten nested meta_data, payload, results into one flat dict"""
    flat = {}
    meta = record.get("meta_data", {})
    payload = record.get("payload", {})
    results = record.get("results", {})

    # Flatten all with prefixes to avoid collisions
    for k, v in meta.items():
        flat[f"meta_{k}"] = v
    for k, v in payload.items():
        flat[f"payload_{k}"] = v
    for k, v in results.items():
        flat[f"results_{k}"] = v

    return flat

def main():
    if not os.path.exists(INPUT):
        raise FileNotFoundError(f"{INPUT} not found")

    with open(INPUT, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    # Flatten
    rows = [flatten_record(rec) for rec in data]

    # Get all keys for CSV header
    fieldnames = sorted(set().union(*[row.keys() for row in rows]))

    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT}")

if __name__ == "__main__":
    main()
