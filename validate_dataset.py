#!/usr/bin/env python3
"""
Dataset Validation Script for Data Center Digital Twin

This script validates that a dataset file meets the required format
and contains valid data for use with the Data Center Digital Twin.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple


class DatasetValidator:
    """Validates dataset format and content."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_records': 0,
            'unique_entities': set(),
            'scenarios_per_entity': {},
        }
    
    def validate_file(self, filepath: str) -> bool:
        """Validate a dataset file."""
        print(f"Validating dataset: {filepath}")
        print("=" * 60)
        
        # Check file exists
        if not Path(filepath).exists():
            self.errors.append(f"File not found: {filepath}")
            return False
        
        # Load JSON
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON format: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False
        
        # Validate structure
        if not isinstance(data, list):
            self.errors.append("Dataset must be a JSON array")
            return False
        
        if len(data) == 0:
            self.errors.append("Dataset is empty")
            return False
        
        self.stats['total_records'] = len(data)
        
        # Validate each record
        for idx, record in enumerate(data):
            self._validate_record(record, idx)
        
        # Calculate statistics
        self.stats['unique_entities'] = len(self.stats['unique_entities'])
        
        # Print results
        self._print_results()
        
        return len(self.errors) == 0
    
    def _validate_record(self, record: Dict[str, Any], idx: int) -> None:
        """Validate a single record."""
        
        # Check top-level structure
        if not isinstance(record, dict):
            self.errors.append(f"Record {idx}: Must be an object/dict")
            return
        
        # Check meta_data
        if 'meta_data' not in record:
            self.errors.append(f"Record {idx}: Missing 'meta_data' field")
            return
        
        if not isinstance(record['meta_data'], dict):
            self.errors.append(f"Record {idx}: 'meta_data' must be an object")
            return
        
        # Check entityId
        if 'entityId' not in record['meta_data']:
            self.errors.append(f"Record {idx}: Missing 'meta_data.entityId'")
            return
        
        entity_id = record['meta_data']['entityId']
        if not isinstance(entity_id, str):
            self.errors.append(f"Record {idx}: 'entityId' must be a string")
            return
        
        if not entity_id.strip():
            self.errors.append(f"Record {idx}: 'entityId' cannot be empty")
            return
        
        # Track entity
        self.stats['unique_entities'].add(entity_id)
        self.stats['scenarios_per_entity'][entity_id] = \
            self.stats['scenarios_per_entity'].get(entity_id, 0) + 1
        
        # Check payload
        if 'payload' not in record:
            self.errors.append(f"Record {idx} ({entity_id}): Missing 'payload' field")
            return
        
        if not isinstance(record['payload'], dict):
            self.errors.append(f"Record {idx} ({entity_id}): 'payload' must be an object")
            return
        
        payload = record['payload']
        
        # Validate required fields
        required_fields = {
            'ambient_temp_c': (10, 45, 'Ambient temperature'),
            'inlet_temp_c': (15, 30, 'Inlet temperature'),
            'server_workload_percent': (0, 100, 'Server workload'),
        }
        
        for field, (min_val, max_val, description) in required_fields.items():
            if field not in payload:
                self.errors.append(
                    f"Record {idx} ({entity_id}): Missing required field '{field}'"
                )
                continue
            
            value = payload[field]
            
            # Check type
            if not isinstance(value, (int, float)):
                self.errors.append(
                    f"Record {idx} ({entity_id}): '{field}' must be a number, got {type(value).__name__}"
                )
                continue
            
            # Check range
            if value < min_val or value > max_val:
                self.errors.append(
                    f"Record {idx} ({entity_id}): '{field}' value {value} out of range [{min_val}, {max_val}]"
                )
            
            # Warnings for unusual values
            if field == 'ambient_temp_c':
                if value < 15 or value > 35:
                    self.warnings.append(
                        f"Record {idx} ({entity_id}): Unusual ambient temperature: {value}°C"
                    )
            elif field == 'inlet_temp_c':
                if value < 18 or value > 28:
                    self.warnings.append(
                        f"Record {idx} ({entity_id}): Unusual inlet temperature: {value}°C"
                    )
    
    def _print_results(self) -> None:
        """Print validation results."""
        print("\n" + "=" * 60)
        print("VALIDATION RESULTS")
        print("=" * 60)
        
        # Statistics
        print("\nDataset Statistics:")
        print(f"  Total records: {self.stats['total_records']}")
        print(f"  Unique entities: {self.stats['unique_entities']}")
        
        if self.stats['scenarios_per_entity']:
            scenarios = list(self.stats['scenarios_per_entity'].values())
            avg_scenarios = sum(scenarios) / len(scenarios)
            min_scenarios = min(scenarios)
            max_scenarios = max(scenarios)
            print(f"  Scenarios per entity: avg={avg_scenarios:.1f}, min={min_scenarios}, max={max_scenarios}")
            
            if min_scenarios < 3:
                self.warnings.append(
                    f"Some entities have fewer than 3 scenarios (minimum: {min_scenarios}). "
                    "Recommend at least 3-5 scenarios per entity for realistic simulation."
                )
        
        # Errors
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors[:20]:  # Limit to first 20
                print(f"  - {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more errors")
        else:
            print("\n✓ No errors found")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Limit to first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        else:
            print("\n✓ No warnings")
        
        # Final verdict
        print("\n" + "=" * 60)
        if self.errors:
            print("❌ VALIDATION FAILED")
            print("Please fix the errors above before using this dataset.")
        else:
            print("✅ VALIDATION PASSED")
            if self.warnings:
                print("Dataset is valid but has some warnings (see above).")
            else:
                print("Dataset is ready to use!")
        print("=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_dataset.py <path_to_dataset.json>")
        print("\nExample:")
        print("  python validate_dataset.py data/datacenter_full_state_list.json")
        sys.exit(1)
    
    filepath = sys.argv[1]
    validator = DatasetValidator()
    
    success = validator.validate_file(filepath)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
