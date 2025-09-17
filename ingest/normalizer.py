"""
ingest/normalizer.py

Normalizes incoming JSON documents into a flat dict/tuple matching DB columns.

Usage:
    from ingest.normalizer import normalize_doc

    normalized = normalize_doc(raw_doc)
    # normalized is a dict with keys matching DB columns and 'raw_json' key

The function handles either:
- the shape with "meta_data", "payload", "results" (your current format), or
- a slight variant using "metadata" or top-level keys.

It tries to be permissive and fills missing fields with None.
"""
import json
from typing import Dict, Any

DB_COLUMNS = [
    "entity_type", "entity_id", "timestamp_utc",
    "server_workload_percent", "inlet_temp_c", "ambient_temp_c",
    "chiller_usage_percent", "ahu_usage_percent", "outlet_temp_c",
    "total_energy_cost_usd", "temp_deviation_c", "cooling_strategy",
    "calculated_server_power_watts", "cooling_unit_power_watts", "calculated_pue",
    "raw_json"
]

def _safe_get(d: Dict[str, Any], *keys, default=None):
    """Walk nested dict; return first existing key path result or default."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        if k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def normalize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert raw doc -> normalized dict with keys matching DB columns (except raw_json).
    Returns dict where 'raw_json' contains the original doc (as dict).
    """
    if not isinstance(doc, dict):
        raise ValueError("normalize_doc expects a dict")

    # accept either "meta_data" (your preferred) or "metadata"
    meta = doc.get("meta_data") or doc.get("metadata") or {}
    payload = doc.get("payload") or {}
    results = doc.get("results") or {}

    normalized = {
        "entity_type": meta.get("entityType") or meta.get("entity_type") or "unknown",
        "entity_id": meta.get("entityId") or meta.get("entity_id") or "unknown",
        "timestamp_utc": meta.get("timestamp") or meta.get("timestamp_utc") or None,

        # payload fields
        "server_workload_percent": payload.get("server_workload_percent"),
        "inlet_temp_c": payload.get("inlet_temp_c"),
        "ambient_temp_c": payload.get("ambient_temp_c"),

        # results fields
        "chiller_usage_percent": results.get("chiller_usage_percent"),
        "ahu_usage_percent": results.get("ahu_usage_percent"),
        "outlet_temp_c": results.get("outlet_temp_c"),
        "total_energy_cost_usd": results.get("total_energy_cost_usd"),
        "temp_deviation_c": results.get("temp_deviation_c"),
        "cooling_strategy": results.get("cooling_strategy"),
        "calculated_server_power_watts": results.get("calculated_server_power_watts"),
        "cooling_unit_power_watts": results.get("cooling_unit_power_watts"),
        "calculated_pue": results.get("calculated_pue"),

        "raw_json": doc  # keep original document for debugging / storage
    }

    # Ensure keys for DB_COLUMNS exist (even if None)
    for k in DB_COLUMNS:
        if k not in normalized:
            normalized[k] = None

    return normalized

def record_tuple_from_normalized(normalized: Dict[str, Any]) -> tuple:
    """
    Convert normalized dict -> tuple matching the INSERT order used in db_utils.
    """
    # Order equals COLUMNS in db/db_utils.py (except raw_json stored last)
    values = []
    for col in DB_COLUMNS[:-1]:  # all except raw_json
        values.append(normalized.get(col))
    # append raw_json as JSON string
    values.append(json.dumps(normalized.get("raw_json", {})))
    return tuple(values)
