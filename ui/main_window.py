# from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
#                              QHBoxLayout, QLabel, QSlider, QFrame, QGridLayout, QCheckBox)
# from PyQt5.QtCore import Qt, pyqtSignal

# class MainWindow(QMainWindow):
#     """
#     The main UI window. Now includes checkboxes and smarter signal handling.
#     """
#     simulation_requested = pyqtSignal()

#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Data Center 'What-If' Engine")
#         self.setGeometry(100, 100, 1000, 600)

#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#         self.layout = QHBoxLayout(self.central_widget)

#         self._create_control_panel()
#         self._create_dashboard_panel()

#     def _create_control_panel(self):
#         control_panel = QFrame()
#         control_panel.setFrameShape(QFrame.StyledPanel)
#         control_layout = QVBoxLayout(control_panel)
#         title = QLabel("Global 'What-If' Overrides")
#         title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
#         control_layout.addWidget(title)

#         self.workload_slider = self._create_slider("Avg Server Workload (%)", 0, 100, 50)
#         control_layout.addLayout(self.workload_slider['layout'])
#         self.inlet_slider = self._create_slider("Global Inlet Temp (°C)", 15, 30, 22)
#         control_layout.addLayout(self.inlet_slider['layout'])
#         self.ambient_slider = self._create_slider("Global Ambient Temp (°C)", 10, 45, 25)
#         control_layout.addLayout(self.ambient_slider['layout'])

#         control_layout.addStretch()
#         self.layout.addWidget(control_panel, 1)

#     def _handle_slider_interaction(self, checkbox):
#         """
#         NEW: This is a 'slot' that checks the checkbox state before emitting a signal.
#         It ensures that moving a slider only triggers an update if its override is active.
#         """
#         if checkbox.isChecked():
#             self.simulation_requested.emit()

#     def _create_slider(self, name, min_val, max_val, initial_val):
#         """Helper to create a checkbox, label, and slider group with corrected logic."""
#         checkbox = QCheckBox()
#         checkbox.setChecked(False)
#         label = QLabel(f"{name}: {initial_val}")
#         slider = QSlider(Qt.Horizontal)
#         slider.setRange(min_val, max_val)
#         slider.setValue(initial_val)
        
#         # Connect slider movement to updating its own label's text
#         slider.valueChanged.connect(lambda value: label.setText(f"{name}: {value}"))
        
#         # --- THE FIX ---
#         # Toggling the checkbox will always trigger a simulation update.
#         checkbox.stateChanged.connect(self.simulation_requested.emit)
        
#         # Moving the slider will now call our new handler method, which is smarter.
#         slider.valueChanged.connect(lambda: self._handle_slider_interaction(checkbox))
        
#         layout = QHBoxLayout()
#         layout.addWidget(checkbox)
#         layout.addWidget(label, 1)
#         layout.addWidget(slider, 2)
#         return {"layout": layout, "slider": slider, "label": label, "checkbox": checkbox}

#     def _create_dashboard_panel(self):
#         # This function remains unchanged.
#         dashboard_panel = QFrame()
#         dashboard_panel.setFrameShape(QFrame.StyledPanel)
#         dashboard_layout = QVBoxLayout(dashboard_panel)
#         title = QLabel("Aggregated Datacenter Metrics")
#         title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
#         dashboard_layout.addWidget(title)
#         grid_layout = QGridLayout()
#         self.result_labels = {}
#         metrics = [
#             "Total Server Power (kW)", "Total Cooling Power (kW)", "Average PUE",
#             "MAX Outlet Temp (°C)", "Projected Daily Cost (USD)", "Cooling Strategy"
#         ]
#         for i, metric_name in enumerate(metrics):
#             name_label = QLabel(metric_name)
#             name_label.setStyleSheet("font-weight: bold;")
#             value_label = QLabel("N/A")
#             value_label.setStyleSheet("font-size: 18px; color: #337ab7;")
#             grid_layout.addWidget(name_label, i, 0)
#             grid_layout.addWidget(value_label, i, 1)
#             self.result_labels[metric_name] = value_label
#         dashboard_layout.addLayout(grid_layout)
#         dashboard_layout.addStretch()
#         self.layout.addWidget(dashboard_panel, 2)
    
#     def update_dashboard(self, results):
#         # This function remains unchanged.
#         self.result_labels["Total Server Power (kW)"].setText(f"{results.get('total_server_power_kw', 0):.2f} kW")
#         self.result_labels["Total Cooling Power (kW)"].setText(f"{results.get('total_cooling_power_kw', 0):.2f} kW")
#         self.result_labels["Average PUE"].setText(f"{results.get('average_pue', 0):.3f}")
#         self.result_labels["MAX Outlet Temp (°C)"].setText(f"{results.get('max_outlet_temp_c', 0):.2f} °C")
#         self.result_labels["Projected Daily Cost (USD)"].setText(f"$ {results.get('total_daily_cost_usd', 0):,.2f}")
#         self.result_labels["Cooling Strategy"].setText(results.get('cooling_strategy', 'N/A'))
        
#         pue = results.get('average_pue', 0)
#         pue_color = "green" if pue < 1.6 else "orange" if pue < 1.9 else "red"
#         self.result_labels["Average PUE"].setStyleSheet(f"font-size: 18px; color: {pue_color}; font-weight: bold;")
        
#         max_temp = results.get('max_outlet_temp_c', 0)
#         temp_color = "green" if max_temp < 35.5 else "orange" if max_temp < 37 else "red"
#         self.result_labels["MAX Outlet Temp (°C)"].setStyleSheet(f"font-size: 18px; color: {temp_color}; font-weight: bold;")

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QFrame, QGridLayout, QCheckBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

class HeatmapWidget(QWidget):
    """A widget to display the thermal state of 700 racks as a color grid."""
    def __init__(self, rows=20, cols=35):
        super().__init__()
        self.rows, self.cols = rows, cols
        self.rack_temps = [25.0] * (rows * cols)
        self.setMinimumHeight(200)

    def update_temps(self, temps):
        self.rack_temps = temps
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = event.rect()
        cell_width, cell_height = rect.width() / self.cols, rect.height() / self.rows
        for i, temp in enumerate(self.rack_temps):
            row, col = i // self.cols, i % self.cols
            color = QColor("#2ECC71") # Green (stable)
            if temp > 35.5: color = QColor("#F1C40F") # Yellow (warning)
            if temp > 37.0: color = QColor("#E74C3C") # Red (critical)
            painter.setBrush(color)
            painter.setPen(QColor("#1A1A2E"))
            painter.drawRect(int(col * cell_width), int(row * cell_height), int(cell_width), int(cell_height))

class MainWindow(QMainWindow):
    """The main UI window, now using sliders with the professional theme."""
    simulation_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Center Digital Twin - Operations Console")
        self.setGeometry(50, 50, 1600, 900)
        self.setStyleSheet("""
            QMainWindow { background-color: #1A1A2E; }
            QFrame { background-color: #28284B; border-radius: 8px; }
            QLabel { color: #ECF0F1; font-family: 'Segoe UI', Arial; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.top_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_layout, 2)
        
        self._create_control_panel()
        self._create_dashboard_panel()
        self._create_heatmap_panel()

    def _create_control_panel(self):
        panel = QFrame()
        layout = QVBoxLayout(panel)
        title = QLabel("Global 'What-If' Overrides")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #4D96FF;")
        layout.addWidget(title)

        self.workload_slider = self._create_slider_control("Avg Server Workload (%)", 0, 100, 50)
        layout.addLayout(self.workload_slider['layout'])
        self.inlet_slider = self._create_slider_control("Global Inlet Temp (°C)", 15, 30, 22)
        layout.addLayout(self.inlet_slider['layout'])
        self.ambient_slider = self._create_slider_control("Global Ambient Temp (°C)", 10, 45, 25)
        layout.addLayout(self.ambient_slider['layout'])
        
        layout.addStretch()
        self.top_layout.addWidget(panel, 1)

    def _handle_slider_interaction(self, checkbox):
        if checkbox.isChecked():
            self.simulation_requested.emit()

    def _create_slider_control(self, name, min_val, max_val, initial_val):
        """Helper to create a checkbox, label, and slider group."""
        checkbox = QCheckBox()
        checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        label = QLabel(f"{name}: {initial_val}")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(initial_val)
        
        slider.valueChanged.connect(lambda value: label.setText(f"{name}: {value}"))
        checkbox.stateChanged.connect(self.simulation_requested.emit)
        slider.valueChanged.connect(lambda: self._handle_slider_interaction(checkbox))
        
        layout = QHBoxLayout()
        layout.addWidget(checkbox)
        layout.addWidget(label, 1)
        layout.addWidget(slider, 2)
        return {"layout": layout, "slider": slider, "label": label, "checkbox": checkbox}

    def _create_dashboard_panel(self):
        panel = QFrame(); layout = QVBoxLayout(panel)
        title = QLabel("Aggregated Datacenter Metrics"); title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #4D96FF;")
        layout.addWidget(title, 0, Qt.AlignCenter)
        grid = QGridLayout(); self.result_labels = {}
        metrics = ["Total Server Power (kW)", "Total Cooling Power (kW)", "Average PUE", "MAX Outlet Temp (°C)", "Total Compute Output", "Projected Daily Cost (USD)", "Cooling Strategy"]
        for i, name in enumerate(metrics):
            name_label = QLabel(name); name_label.setStyleSheet("font-size: 16px; color: #BDC3C7;")
            value_label = QLabel("N/A"); value_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFFFFF;")
            grid.addWidget(name_label, i, 0); grid.addWidget(value_label, i, 1); self.result_labels[name] = value_label
        layout.addLayout(grid); layout.addStretch(); self.top_layout.addWidget(panel, 2)

    def _create_heatmap_panel(self):
        panel = QFrame(); layout = QVBoxLayout(panel)
        title = QLabel("Live Rack Thermal Heatmap (700 Racks)"); title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #4D96FF;")
        self.heatmap = HeatmapWidget(); layout.addWidget(title, 0, Qt.AlignCenter); layout.addWidget(self.heatmap); self.main_layout.addWidget(panel, 1)

    def update_dashboard(self, results):
        self.result_labels["Total Server Power (kW)"].setText(f"{results.get('total_server_power_kw', 0):.2f} kW")
        self.result_labels["Total Cooling Power (kW)"].setText(f"{results.get('total_cooling_power_kw', 0):.2f} kW")
        self.result_labels["Average PUE"].setText(f"{results.get('average_pue', 0):.3f}")
        self.result_labels["MAX Outlet Temp (°C)"].setText(f"{results.get('max_outlet_temp_c', 0):.2f} °C")
        self.result_labels["Total Compute Output"].setText(f"{results.get('total_compute_output', 0):,.0f} Units/hr")
        self.result_labels["Projected Daily Cost (USD)"].setText(f"$ {results.get('total_daily_cost_usd', 0):,.2f}")
        self.result_labels["Cooling Strategy"].setText(results.get('cooling_strategy', 'N/A'))
        self.heatmap.update_temps(results.get('individual_outlet_temps', []))
        
        pue = results.get('average_pue', 0); pue_color = "#2ECC71" if pue < 1.6 else "#F1C40F" if pue < 1.9 else "#E74C3C"
        self.result_labels["Average PUE"].setStyleSheet(f"font-size: 22px; font-weight: bold; color: {pue_color};")
        
        max_temp = results.get('max_outlet_temp_c', 0); temp_color = "#2ECC71" if max_temp < 35.5 else "#F1C40F" if max_temp < 37 else "#E74C3C"
        self.result_labels["MAX Outlet Temp (°C)"].setStyleSheet(f"font-size: 22px; font-weight: bold; color: {temp_color};")

