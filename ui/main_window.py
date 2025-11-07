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
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget,
                             QHBoxLayout, QLabel, QSlider, QFrame, QGridLayout, QCheckBox, QApplication, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QBrush, QPen
from ui.dashboard_widgets import MetricGauge, TrendChart, AlertPanel, EnhancedHeatmap





class StatusIndicator(QLabel):
    """Custom label with status icon and color coding."""

    def __init__(self, text="", status="neutral"):
        super().__init__(text)
        self.status = status
        self.update_status(status, text)

    def update_status(self, status, text=None):
        self.status = status
        if text is not None:
            self.setText(text)

        font = QFont("Segoe UI", 10, QFont.Bold)
        self.setFont(font)

        if status == "good":
            self.setStyleSheet("color: #2ECC71; font-weight: bold; font-size: 10px;")
        elif status == "warning":
            self.setStyleSheet("color: #F39C12; font-weight: bold; font-size: 10px;")
        elif status == "critical":
            self.setStyleSheet("color: #E74C3C; font-weight: bold; font-size: 10px;")
        else:
            self.setStyleSheet("color: #7F8C8D; font-weight: normal; font-size: 10px;")


class MainWindow(QMainWindow):
    """Enhanced main UI window with tabs, charts, and advanced visualizations."""
    simulation_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Center Digital Twin - Operations Console")
        self.setGeometry(50, 50, 1800, 1000)
        self.setStyleSheet("""
            QMainWindow { background-color: #0F0F1E; }
            QFrame { background-color: #1A1A2E; border-radius: 8px; border: 1px solid #2D2D4A; }
            QLabel { color: #ECF0F1; font-family: 'Segoe UI', Arial; }
            QSlider::groove:horizontal { background: #2D2D4A; height: 8px; border-radius: 4px; }
            QSlider::handle:horizontal { background: #4D96FF; width: 18px; margin: -5px 0; border-radius: 9px; }
            QCheckBox { color: #ECF0F1; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QCheckBox::indicator:checked { background-color: #4D96FF; border: 2px solid #4D96FF; border-radius: 3px; }
            QTabWidget::pane { border: 1px solid #2D2D4A; background: #0F0F1E; border-radius: 8px; }
            QTabBar::tab { background: #1A1A2E; color: #95A5A6; padding: 10px 20px; border: 1px solid #2D2D4A; 
                          border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background: #28284B; color: #4D96FF; font-weight: bold; }
            QTabBar::tab:hover { background: #252545; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Create tab widget
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Create different views
        self._create_overview_tab()
        self._create_analytics_tab()
        self._create_thermal_tab()

    def _create_overview_tab(self):
        """Main overview dashboard with key metrics and controls."""
        overview = QWidget()
        layout = QVBoxLayout(overview)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Top row: Controls and Key Metrics
        top_row = QHBoxLayout()
        
        # Control Panel
        control_panel = self._create_control_panel()
        top_row.addWidget(control_panel, 1)
        
        # Key Metrics Gauges
        gauges_panel = QFrame()
        gauges_layout = QHBoxLayout(gauges_panel)
        gauges_layout.setSpacing(15)
        
        self.pue_gauge = MetricGauge("PUE", 1.0, 3.0, "", 1.6, 1.9, reverse_colors=True)
        self.temp_gauge = MetricGauge("Max Temp", 20, 50, "°C", 35.5, 37.0, reverse_colors=True)
        self.power_gauge = MetricGauge("Total Power", 0, 2000, "kW", 1200, 1600, reverse_colors=True)
        
        gauges_layout.addWidget(self.pue_gauge)
        gauges_layout.addWidget(self.temp_gauge)
        gauges_layout.addWidget(self.power_gauge)
        
        top_row.addWidget(gauges_panel, 2)
        layout.addLayout(top_row)
        
        # Middle row: Summary metrics and alerts
        middle_row = QHBoxLayout()
        
        # Summary panel
        summary_panel = self._create_summary_panel()
        middle_row.addWidget(summary_panel, 2)
        
        # Alerts panel
        self.alert_panel = AlertPanel()
        middle_row.addWidget(self.alert_panel, 1)
        
        layout.addLayout(middle_row)
        
        # Bottom: Mini heatmap
        heatmap_frame = QFrame()
        heatmap_layout = QVBoxLayout(heatmap_frame)
        heatmap_title = QLabel("Rack Thermal Overview")
        heatmap_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #4D96FF; margin-bottom: 4px;")
        heatmap_layout.addWidget(heatmap_title)
        
        self.overview_heatmap = EnhancedHeatmap(rows=20, cols=35)
        heatmap_layout.addWidget(self.overview_heatmap)
        
        layout.addWidget(heatmap_frame)
        
        self.tabs.addTab(overview, "📊 Overview")
    
    def _create_control_panel(self):
        """Create the control panel with sliders."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("What-If Scenario Controls")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 6px; color: #4D96FF;")
        layout.addWidget(title)

        desc = QLabel("☑ Enable overrides to simulate conditions")
        desc.setStyleSheet("font-size: 8px; color: #7F8C8D; margin-bottom: 10px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.workload_slider = self._create_slider_control("Avg Server Workload (%)", 0, 100, 50)
        layout.addLayout(self.workload_slider['layout'])

        self.inlet_slider = self._create_slider_control("Global Inlet Temp (°C)", 15, 30, 22)
        layout.addLayout(self.inlet_slider['layout'])

        self.ambient_slider = self._create_slider_control("Global Ambient Temp (°C)", 10, 45, 25)
        layout.addLayout(self.ambient_slider['layout'])

        layout.addStretch()
        return panel

    def _handle_slider_interaction(self, checkbox):
        if checkbox.isChecked():
            self.simulation_requested.emit()

    def _create_slider_control(self, name, min_val, max_val, initial_val):
        """Helper to create a checkbox, label, and slider group."""
        checkbox = QCheckBox()
        checkbox.setStyleSheet("QCheckBox::indicator { width: 18px; height: 18px; }")

        label = QLabel(f"{name}: {initial_val}")
        label.setStyleSheet("color: #ECF0F1; font-size: 10px;")

        value_display = QLabel(f"{initial_val}")
        value_display.setStyleSheet("color: #4D96FF; font-size: 11px; font-weight: bold; min-width: 35px;")

        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(initial_val)

        def update_display(value):
            label.setText(f"{name}: {value}")
            value_display.setText(f"{value}")

        slider.valueChanged.connect(update_display)
        checkbox.stateChanged.connect(self.simulation_requested.emit)
        slider.valueChanged.connect(lambda: self._handle_slider_interaction(checkbox))

        layout = QHBoxLayout()
        layout.addWidget(checkbox)
        layout.addWidget(label, 0)
        layout.addWidget(value_display, 0)
        layout.addWidget(slider, 2)
        layout.setContentsMargins(0, 5, 0, 5)

        return {"layout": layout, "slider": slider, "label": label, "checkbox": checkbox}

    def _create_summary_panel(self):
        """Create summary metrics panel."""
        panel = QFrame()
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Current Metrics")
        title.setStyleSheet("font-size: 12px; font-weight: bold; margin-bottom: 8px; color: #4D96FF;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        self.result_labels = {}
        self.status_indicators = {}

        metrics = [
            ("Total Server Power (kW)", "power"),
            ("Total Cooling Power (kW)", "power"),
            ("Average PUE", "pue"),
            ("MAX Outlet Temp (°C)", "temp"),
            ("Total Compute Output", "compute"),
            ("Projected Daily Cost (USD)", "cost"),
            ("Cooling Strategy", "strategy")
        ]

        for i, (name, metric_type) in enumerate(metrics):
            name_label = QLabel(name)
            name_label.setStyleSheet("font-size: 9px; color: #95A5A6; font-weight: 600;")

            value_label = QLabel("N/A")
            value_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #ECF0F1;")

            status_label = StatusIndicator("", "neutral")

            grid.addWidget(name_label, i, 0, Qt.AlignLeft)
            grid.addWidget(value_label, i, 1, Qt.AlignLeft)
            grid.addWidget(status_label, i, 2, Qt.AlignLeft)

            self.result_labels[name] = value_label
            self.status_indicators[name] = (status_label, metric_type)

        layout.addLayout(grid)
        layout.addStretch()
        return panel

    def _create_analytics_tab(self):
        """Analytics tab with trend charts."""
        analytics = QWidget()
        layout = QVBoxLayout(analytics)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Performance Analytics & Trends")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #4D96FF; margin-bottom: 8px;")
        layout.addWidget(title)

        # Top row charts
        top_charts = QHBoxLayout()
        
        self.pue_chart = TrendChart("PUE Trend", max_points=60, y_label="PUE", color="#4D96FF")
        self.temp_chart = TrendChart("Temperature Trend", max_points=60, y_label="°C", color="#E74C3C")
        
        top_charts.addWidget(self.pue_chart)
        top_charts.addWidget(self.temp_chart)
        layout.addLayout(top_charts)

        # Bottom row charts
        bottom_charts = QHBoxLayout()
        
        self.power_chart = TrendChart("Total Power Trend", max_points=60, y_label="kW", color="#2ECC71")
        self.cost_chart = TrendChart("Cost Trend", max_points=60, y_label="USD/day", color="#F1C40F")
        
        bottom_charts.addWidget(self.power_chart)
        bottom_charts.addWidget(self.cost_chart)
        layout.addLayout(bottom_charts)

        # Efficiency insights
        insights_frame = QFrame()
        insights_layout = QVBoxLayout(insights_frame)
        insights_title = QLabel("Efficiency Insights")
        insights_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #4D96FF;")
        insights_layout.addWidget(insights_title)
        
        self.insights_label = QLabel("Analyzing datacenter performance...")
        self.insights_label.setStyleSheet("font-size: 10px; color: #BDC3C7; padding: 8px;")
        self.insights_label.setWordWrap(True)
        insights_layout.addWidget(self.insights_label)
        
        layout.addWidget(insights_frame)
        
        self.tabs.addTab(analytics, "📈 Analytics")
    
    def _create_thermal_tab(self):
        """Thermal management tab with detailed heatmap."""
        thermal = QWidget()
        layout = QVBoxLayout(thermal)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        title = QLabel("Thermal Management - Live Rack Heatmap (700 Racks)")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #4D96FF; margin-bottom: 8px;")
        layout.addWidget(title)

        # Legend
        legend_layout = QHBoxLayout()
        legend_label = QLabel("Temperature Status:")
        legend_label.setStyleSheet("color: #BDC3C7; font-size: 10px; font-weight: bold;")
        legend_layout.addWidget(legend_label)
        
        for color, label in [("#2ECC71", "Good < 35.5°C"), ("#F1C40F", "Warning 35.5-37°C"),
                             ("#E74C3C", "Critical > 37°C")]:
            color_box = QLabel()
            color_box.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            color_box.setFixedSize(15, 15)
            legend_text = QLabel(label)
            legend_text.setStyleSheet("color: #BDC3C7; font-size: 9px;")
            legend_layout.addWidget(color_box)
            legend_layout.addWidget(legend_text)
            legend_layout.addSpacing(15)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        # Heatmap
        self.heatmap = EnhancedHeatmap(rows=20, cols=35)
        layout.addWidget(self.heatmap)

        # Thermal stats
        stats_frame = QFrame()
        stats_layout = QHBoxLayout(stats_frame)
        
        self.thermal_stats_labels = {}
        for stat_name in ["Hottest Rack", "Coldest Rack", "Avg Temp", "Racks in Warning", "Racks Critical"]:
            stat_container = QVBoxLayout()
            name_label = QLabel(stat_name)
            name_label.setStyleSheet("font-size: 9px; color: #95A5A6;")
            value_label = QLabel("N/A")
            value_label.setStyleSheet("font-size: 11px; color: #FFFFFF; font-weight: bold;")
            stat_container.addWidget(name_label)
            stat_container.addWidget(value_label)
            stats_layout.addLayout(stat_container)
            self.thermal_stats_labels[stat_name] = value_label
        
        layout.addWidget(stats_frame)
        
        self.tabs.addTab(thermal, "🌡️ Thermal")

    def update_dashboard(self, results):
        """Update all dashboard elements with new simulation results."""
        # Extract values
        server_power = results.get('total_server_power_kw', 0)
        cooling_power = results.get('total_cooling_power_kw', 0)
        total_power = server_power + cooling_power
        pue = results.get('average_pue', 0)
        max_temp = results.get('max_outlet_temp_c', 0)
        daily_cost = results.get('total_daily_cost_usd', 0)
        compute_output = results.get('total_compute_output', 0)
        strategy = results.get('cooling_strategy', 'N/A')
        temps = results.get('individual_outlet_temps', [])
        workloads = results.get('individual_workloads', [])

        # Update text labels
        self.result_labels["Total Server Power (kW)"].setText(f"{server_power:.1f} kW")
        self.result_labels["Total Cooling Power (kW)"].setText(f"{cooling_power:.1f} kW")
        self.result_labels["Average PUE"].setText(f"{pue:.2f}")
        self.result_labels["MAX Outlet Temp (°C)"].setText(f"{max_temp:.1f}°C")
        self.result_labels["Total Compute Output"].setText(f"{compute_output:,.0f}")
        self.result_labels["Projected Daily Cost (USD)"].setText(f"${daily_cost:,.0f}")
        
        # Clean up strategy text
        clean_strategy = strategy.replace("[bold red]", "").replace("[/bold red]", "")
        clean_strategy = clean_strategy.replace("[bold yellow]", "").replace("[/bold yellow]", "")
        clean_strategy = clean_strategy.replace("[bold green]", "").replace("[/bold green]", "")
        self.result_labels["Cooling Strategy"].setText(clean_strategy)

        # Update gauges
        self.pue_gauge.set_value(pue)
        self.temp_gauge.set_value(max_temp)
        self.power_gauge.set_value(total_power)

        # Update status indicators with better logic
        pue_status = "good" if pue < 1.6 else "warning" if pue < 1.9 else "critical"
        pue_text = "✓ Excellent" if pue_status == "good" else "⚠ Fair" if pue_status == "warning" else "✗ Poor"
        self.status_indicators["Average PUE"][0].update_status(pue_status, pue_text)

        temp_status = "good" if max_temp < 35.5 else "warning" if max_temp < 37 else "critical"
        temp_text = "✓ Normal" if temp_status == "good" else "⚠ High" if temp_status == "warning" else "✗ Critical"
        self.status_indicators["MAX Outlet Temp (°C)"][0].update_status(temp_status, temp_text)

        # Power status based on total facility power
        power_status = "good" if total_power < 1200 else "warning" if total_power < 1600 else "critical"
        power_text = "✓ Normal" if power_status == "good" else "⚠ High" if power_status == "warning" else "✗ Very High"
        self.status_indicators["Total Server Power (kW)"][0].update_status(power_status, power_text)
        self.status_indicators["Total Cooling Power (kW)"][0].update_status(power_status, power_text)
        
        # Compute and cost always show as info
        self.status_indicators["Total Compute Output"][0].update_status("neutral", "")
        self.status_indicators["Projected Daily Cost (USD)"][0].update_status("neutral", "")
        self.status_indicators["Cooling Strategy"][0].update_status("neutral", "")

        # Update heatmaps
        self.heatmap.update_data(temps, workloads)
        self.overview_heatmap.update_data(temps, workloads)

        # Update trend charts
        self.pue_chart.add_data_point(pue)
        self.temp_chart.add_data_point(max_temp)
        self.power_chart.add_data_point(total_power)
        self.cost_chart.add_data_point(daily_cost)

        # Update thermal stats
        if temps:
            avg_temp = sum(temps) / len(temps)
            hottest_idx = temps.index(max(temps))
            coldest_idx = temps.index(min(temps))
            warning_count = sum(1 for t in temps if 35.5 <= t < 37.0)
            critical_count = sum(1 for t in temps if t >= 37.0)

            self.thermal_stats_labels["Hottest Rack"].setText(f"#{hottest_idx + 1} ({max(temps):.1f}°C)")
            self.thermal_stats_labels["Coldest Rack"].setText(f"#{coldest_idx + 1} ({min(temps):.1f}°C)")
            self.thermal_stats_labels["Avg Temp"].setText(f"{avg_temp:.1f}°C")
            
            # Color code warning/critical counts
            warning_label = self.thermal_stats_labels["Racks in Warning"]
            warning_label.setText(f"{warning_count}")
            if warning_count > 50:
                warning_label.setStyleSheet("font-size: 11px; color: #F39C12; font-weight: bold;")
            else:
                warning_label.setStyleSheet("font-size: 11px; color: #ECF0F1; font-weight: bold;")
            
            critical_label = self.thermal_stats_labels["Racks Critical"]
            critical_label.setText(f"{critical_count}")
            if critical_count > 20:
                critical_label.setStyleSheet("font-size: 11px; color: #E74C3C; font-weight: bold;")
            elif critical_count > 0:
                critical_label.setStyleSheet("font-size: 11px; color: #F39C12; font-weight: bold;")
            else:
                critical_label.setStyleSheet("font-size: 11px; color: #2ECC71; font-weight: bold;")

        # Generate alerts (only add new ones, avoid spam)
        if pue > 2.0:
            self.alert_panel.add_alert(f"PUE critical at {pue:.2f} - Cooling inefficient", "critical")
        elif pue > 1.9:
            self.alert_panel.add_alert(f"PUE elevated at {pue:.2f} - Review cooling", "warning")
        
        if max_temp > 40.0:
            self.alert_panel.add_alert(f"Extreme temperature: {max_temp:.1f}°C - Immediate action required", "critical")
        elif max_temp > 37.0:
            self.alert_panel.add_alert(f"Critical temperature: {max_temp:.1f}°C", "critical")
        elif max_temp > 35.5:
            self.alert_panel.add_alert(f"Temperature elevated: {max_temp:.1f}°C", "warning")
        
        if critical_count > 50:
            self.alert_panel.add_alert(f"{critical_count} racks critical - System overload", "critical")
        elif critical_count > 20:
            self.alert_panel.add_alert(f"{critical_count} racks in critical state", "warning")
        
        if total_power > 1800:
            self.alert_panel.add_alert(f"Power consumption very high: {total_power:.0f} kW", "critical")
        elif total_power > 1600:
            self.alert_panel.add_alert(f"Power consumption elevated: {total_power:.0f} kW", "warning")

        # Update efficiency insights
        efficiency_score = 100 - ((pue - 1.0) * 50)
        thermal_score = 100 - max(0, (max_temp - 30) * 5)
        overall_score = (efficiency_score + thermal_score) / 2

        insights = f"Overall Efficiency Score: {overall_score:.0f}/100\n\n"
        insights += f"• PUE Efficiency: {efficiency_score:.0f}/100 "
        insights += f"({'Excellent' if pue < 1.6 else 'Good' if pue < 1.8 else 'Needs Improvement'})\n"
        insights += f"• Thermal Management: {thermal_score:.0f}/100 "
        insights += f"({'Optimal' if max_temp < 35 else 'Acceptable' if max_temp < 37 else 'Critical'})\n"
        insights += f"• Estimated Annual Cost: ${daily_cost * 365:,.0f}\n\n"
        
        if pue > 1.8:
            insights += "💡 Recommendation: Reduce cooling overhead by optimizing airflow or using free cooling.\n"
        if max_temp > 36:
            insights += "💡 Recommendation: Increase cooling capacity or reduce workload on hot racks.\n"
        if overall_score > 80:
            insights += "✓ Datacenter is operating efficiently!"
        
        self.insights_label.setText(insights)