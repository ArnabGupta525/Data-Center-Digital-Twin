#!/usr/bin/env python3
"""
ingest/select_and_ingest.py

Select one random entity per rack (across a random set of racks), run twin prediction,
update the DB with results, and log the selection so the same entity isn't selected again.

Usage:
    python ingest/select_and_ingest.py                # default 5 racks, random seed
    python ingest/select_and_ingest.py 3              # pick 3 racks
    python ingest/select_and_ingest.py 5 42           # pick 5 racks with seed=42 (reproducible)
"""

import os
import sys
import json
import random
import sqlite3
import datetime
from typing import List, Dict, Any, Optional

# Ensure project root on path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from db.db_utils import get_conn, update_results_by_id  # helper to update DB
# We reuse compute_results from twin.twin_runner (ensure function exists there)
try:
    from twin.twin_runner import compute_results
except Exception:
    # If twin_runner not importable, try local fallback implementation (very small)
    def compute_results(payload: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal fallback mimic of twin_runner.compute_results
        SERVER_POWER_PER_PERCENT = 14.4
        COOLING_POWER_PER_PERCENT = 10.4
        sw = float(payload.get("server_workload_percent", 0.0))
        inlet = float(payload.get("inlet_temp_c", 25.0))
        chiller_pct = float(payload.get("chiller_usage_percent", 50.0))
        ahu_pct = float(payload.get("ahu_usage_percent", 50.0))
        server_power_w = sw * SERVER_POWER_PER_PERCENT
        cooling_unit_power_w = chiller_pct * COOLING_POWER_PER_PERCENT
        outlet_delta = sw * 0.03 + (100.0 - chiller_pct) * 0.03 + ahu_pct * 0.005
        outlet_temp = inlet + outlet_delta
        ambient_temp = inlet - 3.0
        it_power = server_power_w
        pue = (it_power + cooling_unit_power_w) / it_power if it_power > 0 else None
        price_per_kwh = 0.10
        total_kw = (it_power + cooling_unit_power_w) / 1000.0
        cost_usd_per_hour = total_kw * price_per_kwh
        return {
            "outlet_temp_c": round(outlet_temp, 2),
            "ambient_temp_c": round(ambient_temp, 2),
            "total_energy_cost_usd": round(cost_usd_per_hour, 4),
            "temp_deviation_c": round(outlet_temp - inlet, 2),
            "cooling_strategy": "Reduce AHU" if chiller_pct > 60 else "Increase Chiller",
            "calculated_server_power_watts": round(server_power_w, 2),
            "cooling_unit_power_watts": round(cooling_unit_power_w, 2),
            "calculated_pue": round(pue, 4) if pue else None
        }

# DB path (same as other scripts)
DB_PATH = "db/telemetry.db"

# table to persist which telemetry rows were chosen before (prevents repeats)
SELECTION_LOG_SQL = """
CREATE TABLE IF NOT EXISTS selection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    selected_row_id INTEGER NOT NULL,
    selected_entity_id TEXT,
    original_entity_id TEXT,
    rack_id TEXT,
    selection_ts TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    seed INTEGER
);
"""

def ensure_selection_log_table(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.executescript(SELECTION_LOG_SQL)
    conn.commit()

def get_available_racks(conn: sqlite3.Connection) -> List[str]:
    """Return distinct rack ids present in telemetry (entity_id values)."""
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT entity_id FROM telemetry ORDER BY entity_id")
    rows = cur.fetchall()
    return [r[0] for r in rows]

def get_unselected_rows_for_rack(conn: sqlite3.Connection, rack_id: str) -> List[sqlite3.Row]:
    """
    Return telemetry rows for the given rack_id that have not been previously selected (no entry in selection_log).
    Rows are returned as sqlite3.Row objects.
    """
    cur = conn.cursor()
    sql = """
    SELECT t.*
    FROM telemetry t
    LEFT JOIN selection_log s ON s.selected_row_id = t.id
    WHERE t.entity_id = ?
      AND s.selected_row_id IS NULL
    ORDER BY t.id
    """
    cur.execute(sql, (rack_id,))
    return cur.fetchall()

def extract_original_entity_id_from_raw(row: sqlite3.Row) -> Optional[str]:
    """Try to extract meta_data.originalEntityId from raw_json; fallback None."""
    raw = row.get("raw_json") if "raw_json" in row.keys() else None
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        meta = parsed.get("meta_data") or parsed.get("metadata") or {}
        return meta.get("originalEntityId") or meta.get("entityId") or None
    except Exception:
        return None

def record_selection(conn: sqlite3.Connection, row_id: int, rack_id: str, original_id: Optional[str], seed: Optional[int]):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO selection_log (selected_row_id, selected_entity_id, original_entity_id, rack_id, seed) VALUES (?, ?, ?, ?, ?)",
        (row_id, f"row-{row_id}", original_id, rack_id, seed)
    )
    conn.commit()

def choose_and_run(conn: sqlite3.Connection, rack_id: str, seed: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    For a rack_id, choose a random unselected telemetry row,
    run twin.compute_results on its payload, update DB, log selection.
    Returns dict with info about selection or None if none available.
    """
    rows = get_unselected_rows_for_rack(conn, rack_id)
    if not rows:
        print(f"[skip] no unselected rows left for {rack_id}")
        return None

    # reproducible randomness per-run if seed provided
    if seed is not None:
        random.seed(seed + hash(rack_id))

    chosen = random.choice(rows)
    row_id = chosen["id"]

    # Build payload from row columns (fall back to raw_json if needed)
    # Our init_db schema stores payload fields as separate columns
    payload = {
        "server_workload_percent": chosen.get("server_workload_percent"),
        "inlet_temp_c": chosen.get("inlet_temp_c"),
        "ambient_temp_c": chosen.get("ambient_temp_c"),
        # Some records may not contain chiller/ahu in payload; twin compute may expect them in results
        # we'll include if present in results_json
    }

    # If results columns hold chiller/ahu usage precomputed, include them as inputs for compute.
    # Use values from DB columns if available (they might be None).
    # (This keeps compute consistent with your earlier data layout)
    payload["chiller_usage_percent"] = chosen.get("chiller_usage_percent") or None
    payload["ahu_usage_percent"] = chosen.get("ahu_usage_percent") or None

    # If the DB row lacks payload values, try to parse raw_json as backup
    if any(v is None for v in [payload["server_workload_percent"], payload["inlet_temp_c"]]):
        raw = chosen.get("raw_json")
        if raw:
            try:
                parsed = json.loads(raw)
                payload_from_raw = parsed.get("payload", {})
                for k, v in payload_from_raw.items():
                    if payload.get(k) is None:
                        payload[k] = v
            except Exception:
                pass

    # Run twin compute
    results = compute_results(payload)

    # Update DB with results (using helper)
    update_results_by_id(conn, row_id, results)

    # extract original entity id for traceability
    orig_id = extract_original_entity_id_from_raw(chosen) or f"row-{row_id}"

    # log selection
    record_selection(conn, row_id, rack_id, orig_id, seed)

    info = {
        "rack_id": rack_id,
        "selected_row_id": row_id,
        "original_entity_id": orig_id,
        "payload_used": payload,
        "results": results
    }
    print(f"[selected] rack={rack_id} row_id={row_id} orig={orig_id}")
    return info

def main(argv):
    num_racks = 5
    seed = None
    if len(argv) >= 2:
        try:
            num_racks = int(argv[1])
        except Exception:
            pass
    if len(argv) >= 3:
        try:
            seed = int(argv[2])
        except Exception:
            seed = None

    conn = get_conn(DB_PATH)
    ensure_selection_log_table(conn)

    racks = get_available_racks(conn)
    if not racks:
        print("No racks found in telemetry DB.")
        return

    # choose random subset of racks (no replacement)
    if seed is not None:
        random.seed(seed)
    selected_racks = random.sample(racks, min(num_racks, len(racks)))
    print(f"Selected racks for this run: {selected_racks}")

    results_summary = []
    for rack in selected_racks:
        info = choose_and_run(conn, rack, seed)
        if info:
            results_summary.append(info)

    conn.close()

    # print summary
    print("\nSummary of selections:")
    for r in results_summary:
        print(f"  Rack {r['rack_id']}: row {r['selected_row_id']} orig={r['original_entity_id']} -> results keys: {list(r['results'].keys())}")

if __name__ == "__main__":
    main(sys.argv)
