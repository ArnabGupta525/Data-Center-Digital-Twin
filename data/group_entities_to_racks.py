#!/usr/bin/env python3
"""
Group entities in a JSON dataset into racks.

Default behavior: group_size = 5
First 5 records -> rack-1
Next 5 records -> rack-2
...

Input:  data/oldsample.json   (single object or list)
Output: data/sample.json

It also stores the original entity id as meta_data.originalEntityId.
"""
import json
import os
import sys
from typing import List, Dict, Any

INPUT = "data/oldsample.json"
OUTPUT = "data/sample.json"

def load_input(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("Input JSON must be an object or an array of objects")

def group_entities(records: List[Dict[str, Any]], group_size: int = 5, rack_prefix: str = "rack") -> List[Dict[str, Any]]:
    out = []
    for i, rec in enumerate(records):
        group_index = (i // group_size) + 1
        rack_id = f"{rack_prefix}-{group_index}"
        # ensure meta_data exists
        meta = rec.get("meta_data") or rec.get("metadata") or {}
        # preserve original id
        orig_id = meta.get("entityId") or meta.get("entity_id")
        if orig_id:
            meta["originalEntityId"] = orig_id
        # set new entity id
        meta["entityId"] = rack_id
        # write back normalized key name (use meta_data)
        rec["meta_data"] = meta
        out.append(rec)
    return out

def save_output(records: List[Dict[str, Any]], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(records)} records to {path}")

def main(argv):
    # parse optional args: group size and input/output names
    group_size = 5
    inp = INPUT
    out = OUTPUT
    rack_prefix = "rack"
    if len(argv) >= 2:
        try:
            group_size = int(argv[1])
        except Exception:
            print("Invalid group_size argument, must be integer. Using default 5.")
    if len(argv) >= 3:
        inp = argv[2]
    if len(argv) >= 4:
        out = argv[3]
    if len(argv) >= 5:
        rack_prefix = argv[4]

    print(f"Loading input: {inp}")
    records = load_input(inp)
    print(f"Loaded {len(records)} records. Group size = {group_size}")
    grouped = group_entities(records, group_size=group_size, rack_prefix=rack_prefix)
    save_output(grouped, out)

if __name__ == "__main__":
    main(sys.argv)
