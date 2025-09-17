"""
db/db_utils.py

Simple SQLite helper utilities for the digital twin prototype.
Uses DB path "db/telemetry.db" by default but accepts override.

Functions:
- get_conn(db_path) -> sqlite3.Connection
- insert_telemetry_row(conn, row_tuple) -> rowid
- get_latest_record(conn, entity_type=None) -> dict or None
- update_results_by_id(conn, row_id, results_dict) -> None
- query_latest_per_entity(conn, entity_type) -> list[dict]
- execute_query(conn, sql, params) -> list[sqlite3.Row]

The row_tuple shape matches the columns defined by init_db.py and ingest/load_json.py.
"""
import sqlite3
import json
from typing import Any, Dict, Optional, List, Tuple

DEFAULT_DB = "db/telemetry.db"

# Column order used in INSERT (must match init_db.py and load_json.py)
COLUMNS = [
    "entity_type", "entity_id", "timestamp_utc",
    "server_workload_percent", "inlet_temp_c", "ambient_temp_c",
    "chiller_usage_percent", "ahu_usage_percent", "outlet_temp_c",
    "total_energy_cost_usd", "temp_deviation_c", "cooling_strategy",
    "calculated_server_power_watts", "cooling_unit_power_watts", "calculated_pue",
    "raw_json"
]

INSERT_SQL = f"INSERT INTO telemetry ({', '.join(COLUMNS)}) VALUES ({', '.join(['?']*len(COLUMNS))})"

def get_conn(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    """Return a sqlite3 connection with row_factory set to sqlite3.Row"""
    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def insert_telemetry_row(conn: sqlite3.Connection, row: Tuple) -> int:
    """
    Insert a telemetry row tuple. Returns the inserted row id.
    Row must be in the same order as COLUMNS.
    """
    cur = conn.cursor()
    cur.execute(INSERT_SQL, row)
    conn.commit()
    return cur.lastrowid

def get_latest_record(conn: sqlite3.Connection, entity_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Return the latest telemetry row (optionally limited by entity_type).
    Returns a dict (column -> value) or None.
    """
    cur = conn.cursor()
    if entity_type:
        cur.execute("SELECT * FROM telemetry WHERE entity_type = ? ORDER BY timestamp_utc DESC LIMIT 1", (entity_type,))
    else:
        cur.execute("SELECT * FROM telemetry ORDER BY timestamp_utc DESC LIMIT 1")
    row = cur.fetchone()
    return dict(row) if row else None

def update_results_by_id(conn: sqlite3.Connection, row_id: int, results: Dict[str, Any]) -> None:
    """
    Update the results columns for a given telemetry id.
    'results' can contain any of the result fields (keys matching init_db columns),
    and will also set the raw_json results fragment merged into raw_json (keeps original raw_json intact).
    """
    # Build SET clause from provided fields
    allowed_fields = {
        "chiller_usage_percent","ahu_usage_percent","outlet_temp_c",
        "total_energy_cost_usd","temp_deviation_c","cooling_strategy",
        "calculated_server_power_watts","cooling_unit_power_watts","calculated_pue"
    }
    set_clauses = []
    params = []
    for k, v in results.items():
        if k in allowed_fields:
            set_clauses.append(f"{k} = ?")
            params.append(v)
    # also update results_json column by storing the dict as JSON (optional)
    set_clauses.append("results_json = ?")
    params.append(json.dumps(results))
    params.append(row_id)
    sql = f"UPDATE telemetry SET {', '.join(set_clauses)} WHERE id = ?"
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    conn.commit()

def query_latest_per_entity(conn: sqlite3.Connection, entity_type: str) -> List[Dict[str, Any]]:
    """
    Return the latest telemetry row for each entity_id of the given entity_type.
    """
    cur = conn.cursor()
    sql = """
    SELECT t.*
    FROM telemetry t
    JOIN (
      SELECT entity_id, MAX(timestamp_utc) AS maxts
      FROM telemetry
      WHERE entity_type = ?
      GROUP BY entity_id
    ) m ON t.entity_id = m.entity_id AND t.timestamp_utc = m.maxts
    ORDER BY t.entity_id
    """
    cur.execute(sql, (entity_type,))
    rows = cur.fetchall()
    return [dict(r) for r in rows]

def execute_query(conn: sqlite3.Connection, sql: str, params: Tuple = ()) -> List[sqlite3.Row]:
    """Execute arbitrary read query and return rows."""
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur.fetchall()

# Convenience small example functions
def insert_doc(conn: sqlite3.Connection, doc: Dict[str, Any]) -> int:
    """
    Accepts a normalized dict like produced by normalizer.normalized_record(doc)
    and inserts into DB. This is a convenience wrapper.
    """
    # Build tuple according to COLUMNS
    tup = tuple(doc.get(col) for col in COLUMNS[:-1]) + (json.dumps(doc.get("raw_json", {})),)
    return insert_telemetry_row(conn, tup)
