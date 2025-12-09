# Dataset Format Specification

This document describes the required format for custom datasets used with the Data Center Digital Twin.

## Overview

The Data Center Digital Twin accepts telemetry data in JSON format. The data represents various operational states of servers/racks in a data center.

## File Format

- **File Type**: JSON
- **File Name**: `datacenter_full_state_list.json`
- **Location**: Place in the `data/` directory
- **Encoding**: UTF-8

## JSON Structure

The file must contain a JSON array of objects, where each object represents a single operational state snapshot of a server/rack.

### Basic Structure

```json
[
  {
    "meta_data": {
      "entityId": "string"
    },
    "payload": {
      "ambient_temp_c": number,
      "inlet_temp_c": number,
      "server_workload_percent": number
    }
  }
]
```

## Field Specifications

### meta_data Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entityId` | string | Yes | Unique identifier for the server/rack (e.g., "server-001", "rack-A-12") |

### payload Object

| Field | Type | Required | Range | Description |
|-------|------|----------|-------|-------------|
| `ambient_temp_c` | number | Yes | 10-45 | Ambient temperature in Celsius around the server |
| `inlet_temp_c` | number | Yes | 15-30 | Inlet air temperature in Celsius entering the server |
| `server_workload_percent` | number | Yes | 0-100 | Server workload as a percentage of maximum capacity |

## Multiple Scenarios

For realistic simulation, provide **multiple operational scenarios** for each server. The simulation will randomly select from these scenarios to create varied conditions.

### Example: Single Server, Multiple Scenarios

```json
[
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {
      "ambient_temp_c": 20.0,
      "inlet_temp_c": 18.0,
      "server_workload_percent": 30.0
    }
  },
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {
      "ambient_temp_c": 25.0,
      "inlet_temp_c": 22.0,
      "server_workload_percent": 65.0
    }
  },
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {
      "ambient_temp_c": 30.0,
      "inlet_temp_c": 26.0,
      "server_workload_percent": 90.0
    }
  }
]
```

## Complete Example

Here's a complete example with multiple servers and scenarios:

```json
[
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {
      "ambient_temp_c": 22.5,
      "inlet_temp_c": 20.0,
      "server_workload_percent": 45.0
    }
  },
  {
    "meta_data": {"entityId": "server-001"},
    "payload": {
      "ambient_temp_c": 28.0,
      "inlet_temp_c": 24.5,
      "server_workload_percent": 75.0
    }
  },
  {
    "meta_data": {"entityId": "server-002"},
    "payload": {
      "ambient_temp_c": 21.0,
      "inlet_temp_c": 19.0,
      "server_workload_percent": 35.0
    }
  },
  {
    "meta_data": {"entityId": "server-002"},
    "payload": {
      "ambient_temp_c": 26.5,
      "inlet_temp_c": 23.0,
      "server_workload_percent": 80.0
    }
  }
]
```

## Recommendations

### Dataset Size

- **Minimum**: 100 servers with 3-5 scenarios each
- **Recommended**: 500-1000 servers with 5-10 scenarios each
- **Maximum**: Limited only by memory (tested up to 10,000 servers)

### Scenario Diversity

Create scenarios that represent:
- **Low load conditions**: 20-40% workload, cooler temperatures
- **Normal operations**: 50-70% workload, moderate temperatures
- **Peak load**: 80-100% workload, higher temperatures
- **Seasonal variations**: Different ambient temperatures
- **Cooling system states**: Various inlet temperatures

### Realistic Values

Based on typical data center operations:

| Metric | Low | Normal | High | Critical |
|--------|-----|--------|------|----------|
| Ambient Temp (°C) | 18-22 | 22-26 | 26-32 | 32-40 |
| Inlet Temp (°C) | 16-20 | 20-24 | 24-28 | 28-30 |
| Workload (%) | 10-30 | 40-70 | 70-90 | 90-100 |

## Validation

### Manual Validation

Check your dataset:

1. **Valid JSON**: Use a JSON validator (e.g., jsonlint.com)
2. **Required fields**: All objects have `meta_data.entityId` and all `payload` fields
3. **Value ranges**: All numbers are within acceptable ranges
4. **Data types**: Strings are strings, numbers are numbers

### Automated Validation

Use the provided validation script:

```bash
# Using Docker
docker-compose run datacenter-twin python validate_dataset.py /data/datacenter_full_state_list.json

# Using Python directly
python validate_dataset.py data/datacenter_full_state_list.json
```

## Common Issues

### Issue: "Dataset not found"

**Solution**: Ensure the file is named exactly `datacenter_full_state_list.json` and is in the `data/` directory.

### Issue: "Invalid JSON format"

**Solution**: Validate your JSON using a tool like jsonlint.com. Common issues:
- Missing commas between objects
- Trailing commas after last object
- Unquoted keys or string values
- Single quotes instead of double quotes

### Issue: "Missing required field"

**Solution**: Ensure every object has:
```json
{
  "meta_data": {"entityId": "..."},
  "payload": {
    "ambient_temp_c": ...,
    "inlet_temp_c": ...,
    "server_workload_percent": ...
  }
}
```

### Issue: "Value out of range"

**Solution**: Check that:
- `ambient_temp_c` is between 10-45
- `inlet_temp_c` is between 15-30
- `server_workload_percent` is between 0-100

## Converting Existing Data

### From CSV

If you have data in CSV format:

```python
import pandas as pd
import json

# Read CSV
df = pd.read_csv('your_data.csv')

# Convert to required format
data = []
for _, row in df.iterrows():
    data.append({
        "meta_data": {
            "entityId": row['server_id']
        },
        "payload": {
            "ambient_temp_c": float(row['ambient_temp']),
            "inlet_temp_c": float(row['inlet_temp']),
            "server_workload_percent": float(row['workload'])
        }
    })

# Save as JSON
with open('datacenter_full_state_list.json', 'w') as f:
    json.dump(data, f, indent=2)
```

### From Database

Example for PostgreSQL:

```python
import psycopg2
import json

conn = psycopg2.connect("dbname=datacenter user=postgres")
cur = conn.cursor()

cur.execute("""
    SELECT server_id, ambient_temp, inlet_temp, workload
    FROM telemetry
""")

data = []
for row in cur.fetchall():
    data.append({
        "meta_data": {"entityId": row[0]},
        "payload": {
            "ambient_temp_c": float(row[1]),
            "inlet_temp_c": float(row[2]),
            "server_workload_percent": float(row[3])
        }
    })

with open('datacenter_full_state_list.json', 'w') as f:
    json.dump(data, f, indent=2)
```

## Generating Synthetic Data

For testing purposes, you can generate synthetic data:

```python
import json
import random

num_servers = 700
scenarios_per_server = 5

data = []
for server_id in range(1, num_servers + 1):
    for scenario in range(scenarios_per_server):
        data.append({
            "meta_data": {
                "entityId": f"server-{server_id:03d}"
            },
            "payload": {
                "ambient_temp_c": round(random.uniform(18, 35), 1),
                "inlet_temp_c": round(random.uniform(16, 28), 1),
                "server_workload_percent": round(random.uniform(20, 95), 1)
            }
        })

with open('datacenter_full_state_list.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data)} records for {num_servers} servers")
```

## Support

For questions or issues with dataset formatting:
1. Check this specification
2. Use the validation script
3. Review the example dataset in `data/sample.json`
4. Open an issue on GitHub with your dataset structure (sanitized)

---

**Last Updated**: 2025-11-25
