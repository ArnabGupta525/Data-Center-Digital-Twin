# init_db.py
import sqlite3
import os

DB_PATH = "db/telemetry.db"
os.makedirs("db", exist_ok=True)

schema = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Main telemetry table
CREATE TABLE IF NOT EXISTS telemetry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  -- metadata
  entity_type TEXT NOT NULL,
  entity_id TEXT NOT NULL,
  timestamp_utc TEXT NOT NULL,

  -- payload
  server_workload_percent REAL,
  inlet_temp_c REAL,
  ambient_temp_c REAL,

  -- results
  chiller_usage_percent REAL,
  ahu_usage_percent REAL,
  outlet_temp_c REAL,
  total_energy_cost_usd REAL,
  temp_deviation_c REAL,
  cooling_strategy TEXT,
  calculated_server_power_watts REAL,
  cooling_unit_power_watts REAL,
  calculated_pue REAL,

  -- store full JSON for flexibility
  raw_json TEXT,

  created_at DATETIME DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Indexes for faster querying
CREATE INDEX IF NOT EXISTS idx_telemetry_ts 
ON telemetry(timestamp_utc);

CREATE INDEX IF NOT EXISTS idx_telemetry_entity 
ON telemetry(entity_type, entity_id, timestamp_utc);
"""

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(schema)
    conn.commit()
    conn.close()
    print("Initialized DB at", DB_PATH)

if __name__ == "__main__":
    main()
