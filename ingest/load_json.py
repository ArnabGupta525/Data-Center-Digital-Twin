# ingest/load_json.py
"""
Load JSON records (single object or list) from data/sample.json,
normalize them using ingest.normalizer, and insert into SQLite DB
using db.db_utils helpers.

Usage:
    python ingest/load_json.py
"""
import os
import sys
import json

# Ensure project root is on sys.path so imports work when run from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db.db_utils import get_conn, insert_telemetry_row
from ingest.normalizer import normalize_doc, record_tuple_from_normalized

DB_PATH = "db/telemetry.db"
INPUT = "data/sample.json"

os.makedirs("db", exist_ok=True)
os.makedirs("data", exist_ok=True)

def load_and_insert(input_path: str = INPUT, db_path: str = DB_PATH):
    if not os.path.exists(input_path):
        print(f"Input JSON not found: {input_path}")
        return

    with open(input_path, "r") as f:
        data = json.load(f)

    docs = data if isinstance(data, list) else [data]

    conn = get_conn(db_path)
    inserted = 0
    for doc in docs:
        try:
            # Normalize doc to canonical form
            normalized = normalize_doc(doc)
            # Convert normalized dict -> tuple as DB expects
            row_tuple = record_tuple_from_normalized(normalized)
            # Insert using db_utils helper
            row_id = insert_telemetry_row(conn, row_tuple)
            inserted += 1
            print(f"Inserted row id={row_id} entity={normalized.get('entity_id')} ts={normalized.get('timestamp_utc')}")
        except Exception as e:
            print("Failed to insert record:", e)
            print("Record (truncated):", json.dumps(doc)[:400])
            continue

    conn.close()
    print(f"Inserted {inserted} records into {db_path}")

if __name__ == "__main__":
    load_and_insert()
