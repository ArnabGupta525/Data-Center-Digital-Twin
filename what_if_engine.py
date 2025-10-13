import sys
import random
import math
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# --- Import from the new, slider-based UI file ---
from ui.main_window import MainWindow
from data_pipeline import ScenarioCombinator, DataIngestor
from twin.digital_twin_engine import compute_results
from simulation.dynamics import StateRandomizer

class WhatIfEngineController:
    def __init__(self):
        print("Initializing components...")
        self.combinator = ScenarioCombinator()
        self.ingestor = DataIngestor()
        self.randomizer = StateRandomizer()
        self.view = MainWindow()
        self.view.simulation_requested.connect(self.run_simulation)
        self.simulation_timer = QTimer()
        self.simulation_timer.setInterval(1500)
        self.simulation_timer.timeout.connect(self.run_simulation)
        self.run_simulation()
        self.simulation_timer.start()
        print("Continuous simulation started.")

    def run_simulation(self):
        # --- (Steps 1 & 2 are unchanged) ---
        plan = self.combinator.generate_random_combination_plan()
        baseline_state = self.ingestor.get_state_from_plan(plan)
        baseline_payloads = [rack['payload'] for rack in baseline_state]
        varied_payloads = self.randomizer.apply_natural_variation(baseline_payloads)

        # 3. Apply "what-if" overrides from the UI (using updated variable names)
        is_workload_override = self.view.workload_slider['checkbox'].isChecked()
        is_inlet_override = self.view.inlet_slider['checkbox'].isChecked()
        is_ambient_override = self.view.ambient_slider['checkbox'].isChecked()
        
        override_workload = self.view.workload_slider['slider'].value()
        override_inlet = self.view.inlet_slider['slider'].value()
        override_ambient = self.view.ambient_slider['slider'].value()

        final_payloads = []
        for payload in varied_payloads:
            if is_workload_override: payload['server_workload_percent'] = max(0, min(100, override_workload + random.uniform(-2, 2)))
            if is_inlet_override: payload['inlet_temp_c'] = override_inlet
            if is_ambient_override: payload['ambient_temp_c'] = override_ambient
            final_payloads.append(payload)

        # --- (Steps 4 & 5 are unchanged) ---
        individual_results = [compute_results(p) for p in final_payloads]
        if not individual_results: return
        
        total_server_power_w = sum(r['calculated_server_power_watts'] for r in individual_results)
        total_cooling_power_w = sum(r['cooling_unit_power_watts'] for r in individual_results)
        total_facility_power_w = total_server_power_w + total_cooling_power_w
        avg_pue = total_facility_power_w / total_server_power_w if total_server_power_w > 0 else 0
        max_outlet_temp = max(r['outlet_temp_c'] for r in individual_results)
        hottest_result = max(individual_results, key=lambda r: r['temp_deviation_c'])
        strategy = hottest_result.get('cooling_strategy', "STABLE")
        total_compute_output = sum(r['compute_output'] for r in individual_results)

        aggregated_results = {
            "total_server_power_kw": total_server_power_w / 1000,
            "total_cooling_power_kw": total_cooling_power_w / 1000,
            "average_pue": avg_pue,
            "max_outlet_temp_c": max_outlet_temp,
            "total_daily_cost_usd": (total_facility_power_w / 1000 * 0.12 * 24),
            "cooling_strategy": strategy,
            "individual_outlet_temps": [r['outlet_temp_c'] for r in individual_results],
            "total_compute_output": total_compute_output
        }
        self.view.update_dashboard(aggregated_results)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    controller = WhatIfEngineController()
    controller.view.show()
    sys.exit(app.exec_())

