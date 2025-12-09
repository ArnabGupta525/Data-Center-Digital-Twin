#!/usr/bin/env python3
"""
Generate sample dataset for Data Center Digital Twin

This script generates a realistic sample dataset that can be used
when users don't have their own data.
"""

import json
import random
import os


def generate_sample_dataset(
    num_servers=700,
    scenarios_per_server=5,
    output_file='data/datacenter_full_state_list.json'
):
    """Generate a sample dataset with realistic values."""
    
    print(f"Generating sample dataset...")
    print(f"  Servers: {num_servers}")
    print(f"  Scenarios per server: {scenarios_per_server}")
    
    data = []
    
    # Define realistic value ranges for different scenarios
    scenarios = [
        # Low load, cool conditions
        {
            'ambient_range': (18, 22),
            'inlet_range': (16, 20),
            'workload_range': (20, 40)
        },
        # Normal operations
        {
            'ambient_range': (22, 26),
            'inlet_range': (20, 24),
            'workload_range': (40, 70)
        },
        # Peak load
        {
            'ambient_range': (26, 30),
            'inlet_range': (24, 27),
            'workload_range': (70, 90)
        },
        # High temperature stress
        {
            'ambient_range': (30, 35),
            'inlet_range': (26, 29),
            'workload_range': (50, 80)
        },
        # Mixed conditions
        {
            'ambient_range': (20, 28),
            'inlet_range': (18, 26),
            'workload_range': (30, 85)
        }
    ]
    
    for server_id in range(1, num_servers + 1):
        for scenario_idx in range(scenarios_per_server):
            # Pick a scenario template
            scenario = scenarios[scenario_idx % len(scenarios)]
            
            # Generate values with some variation
            ambient = round(random.uniform(*scenario['ambient_range']), 1)
            inlet = round(random.uniform(*scenario['inlet_range']), 1)
            workload = round(random.uniform(*scenario['workload_range']), 1)
            
            # Ensure inlet is cooler than ambient (realistic)
            if inlet >= ambient:
                inlet = ambient - random.uniform(1, 3)
                inlet = round(max(15, inlet), 1)
            
            data.append({
                "meta_data": {
                    "entityId": f"server-{server_id:03d}"
                },
                "payload": {
                    "ambient_temp_c": ambient,
                    "inlet_temp_c": inlet,
                    "server_workload_percent": workload
                }
            })
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Generated {len(data)} records")
    print(f"✓ Saved to: {output_file}")
    
    return len(data)


if __name__ == "__main__":
    import sys
    
    # Allow custom parameters
    num_servers = int(sys.argv[1]) if len(sys.argv) > 1 else 700
    scenarios_per_server = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    output_file = sys.argv[3] if len(sys.argv) > 3 else 'data/datacenter_full_state_list.json'
    
    generate_sample_dataset(num_servers, scenarios_per_server, output_file)
