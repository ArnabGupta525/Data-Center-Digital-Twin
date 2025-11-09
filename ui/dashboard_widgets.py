"""
Custom dashboard widgets for the datacenter digital twin UI.
Includes charts, gauges, and enhanced visualizations.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPainterPath, QLinearGradient
from collections import deque
import math


class MetricGauge(QWidget):
    """Circular gauge widget for displaying metrics like PUE."""
    
    def __init__(self, title="Metric", min_val=0, max_val=100, unit="", 
                 good_threshold=None, warning_threshold=None, reverse_colors=False):
        super().__init__()
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.current_value = min_val
        self.good_threshold = good_threshold
        self.warning_threshold = warning_threshold
        self.reverse_colors = reverse_colors
        self.setMinimumSize(140, 170)
        self.setMaximumSize(180, 190)
        
    def set_value(self, value):
        self.current_value = max(self.min_val, min(self.max_val, value))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        center_x = rect.width() / 2
        center_y = rect.height() / 2 - 30
        radius = min(rect.width(), rect.height()) / 2 - 35
        
        # Draw title above gauge
        painter.setPen(QColor("#7F8C8D"))
        painter.setFont(QFont("Segoe UI", 9))
        painter.drawText(QRectF(0, 5, rect.width(), 20), Qt.AlignCenter, self.title)
        
        # Draw background arc
        painter.setPen(QPen(QColor("#3D3D5C"), 8, Qt.SolidLine, Qt.RoundCap))
        start_angle = 135 * 16
        span_angle = 270 * 16
        painter.drawArc(int(center_x - radius), int(center_y - radius), 
                        int(radius * 2), int(radius * 2), start_angle, span_angle)
        
        # Calculate value position
        value_ratio = (self.current_value - self.min_val) / (self.max_val - self.min_val)
        value_angle = 135 + (270 * value_ratio)
        
        # Determine color based on thresholds
        if self.reverse_colors:
            if self.good_threshold and self.current_value <= self.good_threshold:
                color = QColor("#2ECC71")
            elif self.warning_threshold and self.current_value <= self.warning_threshold:
                color = QColor("#F39C12")
            else:
                color = QColor("#E74C3C")
        else:
            if self.good_threshold and self.current_value >= self.good_threshold:
                color = QColor("#2ECC71")
            elif self.warning_threshold and self.current_value >= self.warning_threshold:
                color = QColor("#F39C12")
            else:
                color = QColor("#E74C3C")
        
        # Draw value arc with gradient
        gradient = QLinearGradient(center_x - radius, center_y, center_x + radius, center_y)
        gradient.setColorAt(0, color.darker(120))
        gradient.setColorAt(1, color)
        painter.setPen(QPen(QBrush(gradient), 8, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(int(center_x - radius), int(center_y - radius),
                        int(radius * 2), int(radius * 2), start_angle, int(270 * value_ratio * 16))
        
        # Draw value text below the gauge
        painter.setPen(color)
        painter.setFont(QFont("Segoe UI", 18, QFont.Bold))
        value_text = f"{self.current_value:.2f}"
        value_y_position = center_y + radius + 15
        painter.drawText(QRectF(0, value_y_position, rect.width(), 30), Qt.AlignCenter, value_text)
        
        # Draw unit below the value
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#7F8C8D"))
        painter.drawText(QRectF(0, value_y_position + 25, rect.width(), 20), Qt.AlignCenter, self.unit)


class TrendChart(QWidget):
    """
    Line chart widget, with support for a second (forecast) series
    and gradient fill.
    """
    
    # --- UPDATED: Added goal_text, y_min, y_max ---
    def __init__(self, title="Trend", max_points=50, y_label="Value", color="#4D96FF", 
                 forecast_steps=30, goal_text=None, y_min=None, y_max=None):
        super().__init__()
        self.title = title
        self.y_label = y_label
        self.color = QColor(color)
        self.max_points = max_points
        self.forecast_steps = forecast_steps
        self.data_points = deque(maxlen=max_points)
        self.forecast_points = []
        
        # --- NEW: Store new properties ---
        self.goal_text = goal_text
        self.y_min = y_min
        self.y_max = y_max
        
        # --- UPDATED: Increased graph height ---
        self.setMinimumSize(400, 300) 
        
    def add_data_point(self, value):
        # --- NEW: Enforce static range if it exists ---
        if self.y_min is not None and value < self.y_min:
            value = self.y_min
        if self.y_max is not None and value > self.y_max:
            value = self.y_max
            
        self.data_points.append(value)
        self.update()
    
    def update_forecast_data(self, forecast_data):
        """Update the list of future (forecasted) data points."""
        self.forecast_points = forecast_data
        self.update()
        
    def clear_data(self):
        self.data_points.clear()
        self.forecast_points = []
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        margin = 50
        chart_rect = QRectF(margin, margin + 20, rect.width() - margin * 2, rect.height() - margin * 2 - 20)
        
        # Draw title
        painter.setPen(QColor("#BDC3C7"))
        painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
        painter.drawText(QRectF(0, 10, rect.width(), 30), Qt.AlignCenter, self.title)
        
        # --- NEW: Draw Goal Text (Sub-label) ---
        if self.goal_text:
            painter.setPen(QColor("#7F8C8D"))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(QRectF(0, 30, rect.width(), 20), Qt.AlignCenter, self.goal_text)
        
        # Draw chart background
        painter.fillRect(chart_rect, QColor("#1A1A2E"))
        painter.setPen(QPen(QColor("#3D3D5C"), 1))
        painter.drawRect(chart_rect)
        
        if len(self.data_points) < 2:
            painter.setPen(QColor("#95A5A6"))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(chart_rect, Qt.AlignCenter, "Collecting data...")
            return
        
        # --- UPDATED: Use static range if available ---
        all_points = list(self.data_points) + self.forecast_points
        
        if self.y_min is not None and self.y_max is not None:
            min_val = self.y_min
            max_val = self.y_max
        else:
            # Fallback to dynamic range
            min_val = min(all_points) if all_points else 0
            max_val = max(all_points) if all_points else 1
            
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Draw grid lines
        painter.setPen(QPen(QColor("#3D3D5C"), 1, Qt.DotLine))
        num_grid_lines = 5
        for i in range(num_grid_lines):
            y = chart_rect.top() + (chart_rect.height() / (num_grid_lines - 1)) * i
            painter.drawLine(int(chart_rect.left()), int(y), int(chart_rect.right()), int(y))
        
        
        # --- Build both paths (fill and line) ---
        points = list(self.data_points)
        
        total_x_points = (self.max_points - 1) + self.forecast_steps
        if total_x_points == 0: total_x_points = 1
        x_step = chart_rect.width() / total_x_points
        
        line_path = QPainterPath()
        fill_path = QPainterPath()
        
        current_x_offset = (self.max_points - len(points)) * x_step
        start_x = chart_rect.left() + current_x_offset
        
        fill_path.moveTo(start_x, chart_rect.bottom())

        first_value = points[0]
        first_y = chart_rect.bottom() - (((first_value - min_val) / value_range) * chart_rect.height())

        line_path.moveTo(start_x, first_y)
        fill_path.lineTo(start_x, first_y)

        last_x = start_x
        for i, value in enumerate(points[1:], 1):
            y_ratio = (value - min_val) / value_range
            x = chart_rect.left() + current_x_offset + (i * x_step)
            y = chart_rect.bottom() - (y_ratio * chart_rect.height())
            
            line_path.lineTo(x, y)
            fill_path.lineTo(x, y)
            last_x = x

        fill_path.lineTo(last_x, chart_rect.bottom())
        fill_path.lineTo(chart_rect.left() + current_x_offset, chart_rect.bottom())
        fill_path.closeSubpath()

        # --- 1. Draw the Gradient Fill ---
        gradient = QLinearGradient(chart_rect.center().x(), chart_rect.top(), chart_rect.center().x(), chart_rect.bottom())
        gradient_color = QColor(self.color)
        gradient_color.setAlpha(90)
        gradient.setColorAt(0, gradient_color)
        gradient_color.setAlpha(0)
        gradient.setColorAt(1, gradient_color)
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawPath(fill_path)

        # --- 2. Draw the Main Line (Thicker) ---
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.color, 3))
        painter.drawPath(line_path)
        
        
        # --- 3. Draw Forecast Data Line (Thicker) ---
        if self.forecast_points and len(self.data_points) > 0:
            forecast_path = QPainterPath()
            
            last_actual_value = points[-1]
            last_actual_x = last_x
            last_actual_y = chart_rect.bottom() - (((last_actual_value - min_val) / value_range) * chart_rect.height())
            forecast_path.moveTo(last_actual_x, last_actual_y)
            
            for i, value in enumerate(self.forecast_points):
                # --- Clamp forecast value to static range ---
                if self.y_min is not None and value < self.y_min: value = self.y_min
                if self.y_max is not None and value > self.y_max: value = self.y_max
                
                y_ratio = (value - min_val) / value_range
                x = last_actual_x + ((i + 1) * x_step)
                y = chart_rect.bottom() - (y_ratio * chart_rect.height())
                
                if x > chart_rect.right() + 5:
                    break
                    
                forecast_path.lineTo(x, y)

            forecast_pen = QPen(self.color.lighter(110), 3, Qt.DotLine)
            painter.setPen(forecast_pen)
            painter.drawPath(forecast_path)

        # --- 4. Draw Y-axis labels ---
        painter.setPen(QColor("#95A5A6"))
        painter.setFont(QFont("Segoe UI", 8))
        for i in range(num_grid_lines):
            y = chart_rect.top() + (chart_rect.height() / (num_grid_lines - 1)) * i
            value = max_val - (value_range / (num_grid_lines - 1)) * i
            painter.drawText(QRectF(5, y - 10, margin - 10, 20), Qt.AlignRight | Qt.AlignVCenter, f"{value:.1f}")


class AlertPanel(QFrame):
    """Panel for displaying system alerts and warnings."""
    
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #28284B;
                border-radius: 8px;
                border: 1px solid #3D3D5C;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("System Alerts")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: #4D96FF;")
        layout.addWidget(title)
        
        self.alerts_layout = QVBoxLayout()
        self.alerts_layout.setSpacing(5)
        layout.addLayout(self.alerts_layout)
        layout.addStretch()
        
        self.alerts = []
        
    def add_alert(self, message, severity="info"):
        """Add an alert message. Severity: info, warning, critical, good"""
        if len(self.alerts) > 0:
            last_alert_text = self.alerts[-1].text()
            if message in last_alert_text:
                return
        
        colors = {
            "info": "#4D96FF",
            "warning": "#F39C12",
            "critical": "#E74C3C",
            "good": "#2ECC71"
        }
        icons = {
            "info": "ℹ",
            "warning": "⚠",
            "critical": "✗",
            "good": "✓"
        }
        
        alert_widget = QLabel(f"{icons.get(severity, 'ℹ')} {message}")
        alert_widget.setStyleSheet(f"""
            color: {colors.get(severity, '#4D96FF')};
            font-size: 9px;
            padding: 5px 7px;
            background-color: rgba(255, 255, 255, 0.03);
            border-left: 3px solid {colors.get(severity, '#4D96FF')};
            border-radius: 3px;
        """)
        alert_widget.setWordWrap(True)
        
        self.alerts_layout.addWidget(alert_widget)
        self.alerts.append(alert_widget)
        
        if len(self.alerts) > 8:
            old_alert = self.alerts.pop(0)
            self.alerts_layout.removeWidget(old_alert)
            old_alert.deleteLater()
    
    def clear_alerts(self):
        for alert in self.alerts:
            self.alerts_layout.removeWidget(alert)
            alert.deleteLater()
        self.alerts.clear()


class EnhancedHeatmap(QWidget):
    """Enhanced heatmap with hover tooltips and rack details."""
    
    def __init__(self, rows=20, cols=35):
        super().__init__()
        self.rows, self.cols = rows, cols
        self.rack_temps = [25.0] * (rows * cols)
        self.rack_workloads = [50.0] * (rows * cols)
        self.setMinimumHeight(300)
        self.setMouseTracking(True)
        self.hover_rack = -1
        
    def update_data(self, temps, workloads=None):
        self.rack_temps = temps
        if workloads:
            self.rack_workloads = workloads
        self.update()
        
    def mouseMoveEvent(self, event):
        rect = self.rect()
        cell_width = rect.width() / self.cols
        cell_height = rect.height() / self.rows
        
        col = int(event.x() / cell_width)
        row = int(event.y() / cell_height)
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.hover_rack = row * self.cols + col
        else:
            self.hover_rack = -1
        
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        cell_width = rect.width() / self.cols
        cell_height = rect.height() / self.rows
        
        for i, temp in enumerate(self.rack_temps):
            row = i // self.cols
            col = i % self.cols
            
            if temp < 35.5:
                color = QColor("#2ECC71")
            elif temp < 37.0:
                color = QColor("#F1C40F")
            else:
                color = QColor("#E74C3C")
            
            if i == self.hover_rack:
                color = color.lighter(150)
                painter.setPen(QPen(QColor("#FFFFFF"), 2))
            else:
                painter.setPen(QPen(QColor("#1A1A2E"), 1))
            
            painter.setBrush(color)
            x = int(col * cell_width)
            y = int(row * cell_height)
            w = int(cell_width)
            h = int(cell_height)
            painter.drawRect(x, y, w, h)
        
        if self.hover_rack >= 0 and self.hover_rack < len(self.rack_temps):
            temp = self.rack_temps[self.hover_rack]
            workload = self.rack_workloads[self.hover_rack] if self.hover_rack < len(self.rack_workloads) else 0
            
            tooltip_text = f"Rack {self.hover_rack + 1}\nTemp: {temp:.1f}°C\nWorkload: {workload:.0f}%"
            
            painter.setFont(QFont("Segoe UI", 9))
            metrics = painter.fontMetrics()
            lines = tooltip_text.split('\n')
            max_width = max(metrics.horizontalAdvance(line) for line in lines)
            tooltip_height = len(lines) * metrics.height() + 10
            
            tooltip_x = min(event.rect().width() - max_width - 20, int((self.hover_rack % self.cols) * cell_width))
            tooltip_y = max(10, int((self.hover_rack // self.cols) * cell_height) - tooltip_height - 10)
            
            painter.setBrush(QColor("#28284B"))
            painter.setPen(QPen(QColor("#4D96FF"), 2))
            painter.drawRoundedRect(tooltip_x, tooltip_y, max_width + 10, tooltip_height, 5, 5)
            
            painter.setPen(QColor("#ECF0F1"))
            y_offset = tooltip_y + metrics.height()
            for line in lines:
                painter.drawText(tooltip_x + 5, y_offset, line)
                y_offset += metrics.height()