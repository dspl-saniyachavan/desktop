"""
Telemetry widget for real-time data display
"""

import random
from collections import deque
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QGridLayout, QScrollArea)
from PySide6.QtCore import Qt, Slot, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient

class MiniChart(QWidget):
    """Mini bar chart widget"""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.values = deque([random.randint(30, 90) for _ in range(14)], maxlen=14)
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
    
    def update_value(self, value):
        """Add new value and update chart"""
        self.values.append(int(value))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        bar_width = width / len(self.values)
        
        for i, value in enumerate(self.values):
            bar_height = (value / 100) * height
            x = i * bar_width
            y = height - bar_height
            
            painter.fillRect(int(x + 1), int(y), int(bar_width - 2), int(bar_height), self.color)


class LineChart(QWidget):
    """Line chart widget for historical trends"""
    def __init__(self, param_id, param_name, param_unit, color, parent=None):
        super().__init__(parent)
        self.param_id = param_id
        self.param_name = param_name
        self.param_unit = param_unit
        self.color = QColor(color)
        self.values = deque(maxlen=20)
        self.timestamps = deque(maxlen=20)
        self.setMinimumHeight(350)
        self.setMouseTracking(True)
        self.hover_index = -1
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 16px;
            }
        """)
    
    def add_value(self, value, timestamp=None):
        """Add new value to chart"""
        self.values.append(float(value))
        self.timestamps.append(timestamp or datetime.now())
        self.update()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move to show tooltip"""
        if len(self.values) < 2:
            return
        
        padding_left = 70
        padding_right = 40
        padding_top = 80
        padding_bottom = 50
        chart_width = self.width() - padding_left - padding_right
        chart_height = self.height() - padding_top - padding_bottom
        
        mouse_pos = event.position()
        min_val = min(self.values)
        max_val = max(self.values)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Check if mouse is near any point
        self.hover_index = -1
        hover_distance = 10  # pixels
        
        for i, value in enumerate(self.values):
            x = padding_left + (chart_width * i / (len(self.values) - 1))
            y = padding_top + chart_height - ((value - min_val) / value_range * chart_height)
            
            dx = mouse_pos.x() - x
            dy = mouse_pos.y() - y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= hover_distance:
                self.hover_index = i
                break
        
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Draw rounded rectangle background with clipping
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, 16, 16)
        painter.setClipPath(path)
        painter.fillRect(self.rect(), QColor("#ffffff"))
        
        if len(self.values) < 2:
            return
        padding_left = 70
        padding_right = 40
        padding_top = 80
        padding_bottom = 50
        chart_width = width - padding_left - padding_right
        chart_height = height - padding_top - padding_bottom
        
        # Get min/max values
        min_val = min(self.values)
        max_val = max(self.values)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Draw title
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QColor("#1e293b"))
        painter.drawText(padding_left, 35, self.param_name)
        
        # Draw subtitle
        font.setPointSize(11)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor("#64748b"))
        painter.drawText(padding_left, 55, "Last 60 seconds")
        
        # Draw current value
        if self.values:
            current = self.values[-1]
            font.setPointSize(28)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(self.color)
            text = f"{current:.1f} {self.param_unit}"
            text_width = painter.fontMetrics().horizontalAdvance(text)
            painter.drawText(width - padding_right - text_width, 40, text)
            
            font.setPointSize(10)
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QColor("#64748b"))
            painter.drawText(width - padding_right - text_width, 60, "Current Value")
        
        # Draw grid lines and Y-axis labels
        painter.setPen(QPen(QColor("#e5e7eb"), 1))
        font.setPointSize(9)
        painter.setFont(font)
        
        for i in range(5):
            y = padding_top + (chart_height * i / 4)
            painter.drawLine(int(padding_left), int(y), int(width - padding_right), int(y))
            # Y-axis labels
            val = max_val - (value_range * i / 4)
            painter.setPen(QColor("#9ca3af"))
            painter.drawText(10, int(y + 5), f"{val:.1f}")
            painter.setPen(QPen(QColor("#e5e7eb"), 1))
        
        # Draw X-axis time labels
        painter.setPen(QColor("#9ca3af"))
        time_points = [0, 10, 20, 30, 40, 50, 60]
        for i, t in enumerate(time_points):
            x = padding_left + (chart_width * i / 6)
            painter.drawText(int(x - 15), height - 20, f"{t}s")
        
        # Draw line
        path = QPainterPath()
        points = []
        
        for i, value in enumerate(self.values):
            x = padding_left + (chart_width * i / (len(self.values) - 1))
            y = padding_top + chart_height - ((value - min_val) / value_range * chart_height)
            point = QPointF(x, y)
            points.append(point)
            
            if i == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
        
        # Draw gradient fill
        gradient = QLinearGradient(0, padding_top, 0, height - padding_bottom)
        fill_color = QColor(self.color)
        fill_color.setAlpha(40)
        gradient.setColorAt(0, fill_color)
        fill_color.setAlpha(5)
        gradient.setColorAt(1, fill_color)
        
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), height - padding_bottom)
        fill_path.lineTo(padding_left, height - padding_bottom)
        fill_path.closeSubpath()
        
        painter.fillPath(fill_path, gradient)
        
        # Draw line
        painter.setPen(QPen(self.color, 3))
        painter.drawPath(path)
        
        # Draw points
        painter.setBrush(self.color)
        for i, point in enumerate(points):
            if i == self.hover_index:
                painter.drawEllipse(point, 7, 7)
            else:
                painter.drawEllipse(point, 5, 5)
        
        # Draw tooltip
        if self.hover_index >= 0 and self.hover_index < len(self.values):
            point = points[self.hover_index]
            value = self.values[self.hover_index]
            timestamp = self.timestamps[self.hover_index] if self.hover_index < len(self.timestamps) else datetime.now()
            
            # Format tooltip text
            time_str = timestamp.strftime("%H:%M:%S")
            value_str = f"{value:.2f} {self.param_unit}"
            
            # Tooltip dimensions
            font.setPointSize(10)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_width = max(metrics.horizontalAdvance(time_str), metrics.horizontalAdvance(value_str)) + 20
            text_height = 50
            
            # Position tooltip
            tooltip_x = point.x() - text_width / 2
            tooltip_y = point.y() - text_height - 15
            
            # Keep tooltip in bounds
            if tooltip_x < padding_left:
                tooltip_x = padding_left
            if tooltip_x + text_width > width - padding_right:
                tooltip_x = width - padding_right - text_width
            if tooltip_y < padding_top:
                tooltip_y = point.y() + 15
            
            # Draw tooltip background
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor("#1e293b"))
            painter.drawRoundedRect(int(tooltip_x), int(tooltip_y), int(text_width), int(text_height), 8, 8)
            
            # Draw tooltip text
            painter.setPen(QColor("#ffffff"))
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(int(tooltip_x + 10), int(tooltip_y + 20), value_str)
            
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(int(tooltip_x + 10), int(tooltip_y + 38), time_str)
            
            # Draw vertical line
            painter.setPen(QPen(QColor("#64748b"), 1, Qt.DashLine))
            painter.drawLine(int(point.x()), padding_top, int(point.x()), height - padding_bottom)

class TelemetryWidget(QWidget):
    """Widget for displaying real-time telemetry data"""
    
    def __init__(self, telemetry_service=None, auth_service=None):
        super().__init__()
        self.telemetry_service = telemetry_service
        self.auth_service = auth_service
        self.parameter_widgets = {}
        self.line_charts = {}
        self.setup_ui()
        
        if self.telemetry_service:
            self.telemetry_service.parameters_updated.connect(self.update_all_parameters)
            self.telemetry_service.parameter_changed.connect(self.update_single_parameter)
            # Force initial parameter refresh
            print("🔄 Forcing initial parameter refresh...")
            self.telemetry_service.refresh_parameters()
            # Auto-start streaming only for client role (admin/user receive from clients)
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user and current_user.get('role') == 'client':
                    print(" Client mode: Starting telemetry streaming")
                    self.telemetry_service.start_streaming(3)
                elif current_user and current_user.get('role') in ['admin', 'user']:
                    print(f" {current_user.get('role').title()} mode: Receiving telemetry from clients")
                    # Admin/User needs to connect to MQTT to receive data
                    if not self.telemetry_service.mqtt_service.is_connected:
                        print(" Connecting to MQTT broker...")
                        self.telemetry_service.mqtt_service.connect()
    
    def refresh_parameters(self):
        """Refresh parameters display"""
        print("🔄 Refreshing telemetry widget parameters...")
        
        if self.telemetry_service:
            self.telemetry_service.refresh_parameters()
        
        # Clear and recreate parameter cards
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.parameter_widgets.clear()
        
        # Clear and recreate line charts
        for i in reversed(range(self.charts_layout.count())):
            widget = self.charts_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.line_charts.clear()
        
        # Recreate UI elements
        self.create_parameter_cards()
        self.create_line_charts()
        
        print(f"✅ Telemetry widget refreshed with {len(self.parameter_widgets)} parameters")
    
    def setup_ui(self):
        """Setup telemetry UI"""
        self.setStyleSheet("background-color: #0f172a;")
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(80, 50, 80, 50)
        
        # Welcome section
        user_name = "User"
        if self.auth_service:
            current_user = self.auth_service.get_current_user()
            if current_user:
                user_name = current_user.get('name', 'User')
        
        welcome_label = QLabel(f"Welcome back, {user_name}!")
        welcome_label.setStyleSheet("""
            font-size: 48px; 
            font-weight: 700; 
            color: white; 
            letter-spacing: -0.5px;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
            background: transparent;
        """)
        
        subtitle_label = QLabel("Monitor your telemetry streams in real-time")
        subtitle_label.setStyleSheet("""
            font-size: 20px; 
            color: #94a3b8; 
            font-weight: 400;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
            background: transparent;
        """)
        
        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(16)
        
        # Section title
        section_label = QLabel("LIVE DATA STREAM")
        section_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: 700; 
            color: #64748b; 
            letter-spacing: 2.5px;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
            background: transparent;
        """)
        layout.addWidget(section_label)
        layout.addSpacing(8)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { background: #1e293b; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #475569; border-radius: 4px; }
        """)
        
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(24)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Parameter cards grid
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        self.create_parameter_cards()
        scroll_layout.addLayout(self.grid_layout)
        
        
        # Historical trends section
        scroll_layout.addSpacing(32)
        trends_label = QLabel("HISTORICAL TRENDS")
        trends_label.setStyleSheet("""
            font-size: 13px; 
            font-weight: 700; 
            color: #64748b; 
            letter-spacing: 2.5px;
            background: transparent;
        """)
        scroll_layout.addWidget(trends_label)
        scroll_layout.addSpacing(16)
        
        # Line charts layout
        self.charts_layout = QVBoxLayout()
        self.charts_layout.setSpacing(24)
        self.create_line_charts()
        scroll_layout.addLayout(self.charts_layout)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)
    
    def create_parameter_cards(self):
        """Create parameter display cards"""
        if self.telemetry_service:
            parameters = list(self.telemetry_service.get_parameters().values())
            print(f"📊 Creating parameter cards for {len(parameters)} parameters")
        else:
            parameters = []
            print("⚠️ No telemetry service available")
        
        if not parameters:
            print("⚠️ No parameters found - dashboard will be empty")
            # Create a placeholder message
            placeholder = QLabel("No parameters configured. Add parameters to see telemetry data.")
            placeholder.setStyleSheet("""
                QLabel {
                    color: #64748b;
                    font-size: 16px;
                    padding: 40px;
                    text-align: center;
                    background: transparent;
                }
            """)
            placeholder.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(placeholder, 0, 0, 1, 3)
            return
        
        for i, param in enumerate(parameters):
            card = self.create_parameter_card(param)
            self.grid_layout.addWidget(card, i // 3, i % 3)
    
    def _get_default_parameters(self):
        """Get default parameters - empty list since parameters come from backend"""
        return []
    
    def create_parameter_card(self, param):
        """Create individual parameter card with trend indicator"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: none;
            }
        """)
        card.setFixedSize(450, 200)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(24, 24, 24, 20)
        
        # Header with value and trend
        header_layout = QHBoxLayout()
        
        # Value
        value_label = QLabel(f"{param['value']:.1f}")
        value_label.setStyleSheet("""
            font-size: 56px; 
            font-weight: 700; 
            color: #0f172a; 
            letter-spacing: -1.5px;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
            background: transparent;
        """)
        
        # Trend indicator
        trend_label = QLabel("•")
        trend_label.setStyleSheet("""
            font-size: 32px;
            color: #64748b;
            background: transparent;
        """)
        
        header_layout.addWidget(value_label)
        header_layout.addWidget(trend_label, alignment=Qt.AlignTop)
        header_layout.addStretch()
        
        # Name
        name_label = QLabel(f"{param['name']} ({param['unit']})")
        name_label.setStyleSheet("""
            font-size: 15px; 
            color: #64748b; 
            font-weight: 500;
            font-family: 'Inter', 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
            background: transparent;
        """)
        
        # Mini chart
        chart = MiniChart(param['color'])
        chart.setFixedHeight(60)
        
        layout.addLayout(header_layout)
        layout.addWidget(name_label)
        layout.addWidget(chart)
        
        self.parameter_widgets[param['id']] = {
            'value_label': value_label,
            'trend_label': trend_label,
            'chart': chart,
            'min': param.get('min', 0),
            'max': param.get('max', 100),
            'prev_value': param['value']
        }
        
        return card
    
    def create_line_charts(self):
        """Create line charts for historical trends"""
        if self.telemetry_service:
            parameters = list(self.telemetry_service.get_parameters().values())
            print(f" Creating line charts for {len(parameters)} parameters")
        else:
            parameters = []
            print(" No telemetry service for charts")
        
        if not parameters:
            print(" No parameters for charts")
            return
        
        for param in parameters:
            chart = LineChart(
                param['id'],
                param['name'],
                param['unit'],
                param['color']
            )
            self.charts_layout.addWidget(chart)
            self.line_charts[param['id']] = chart
    
    @Slot(dict)
    def update_all_parameters(self, parameters):
        """Update all parameters with trend indicators"""
        timestamp = datetime.now()
        for param_id, param in parameters.items():
            if param_id in self.parameter_widgets:
                value = param['value']
                widget = self.parameter_widgets[param_id]
                prev_value = widget.get('prev_value', value)
                
                # Update value
                widget['value_label'].setText(f"{value:.1f}")
                
                # Update trend indicator
                if value > prev_value + 0.1:
                    widget['trend_label'].setText("▲")
                    widget['trend_label'].setStyleSheet("font-size: 32px; color: #059669; background: transparent;")
                elif value < prev_value - 0.1:
                    widget['trend_label'].setText("▼")
                    widget['trend_label'].setStyleSheet("font-size: 32px; color: #dc2626; background: transparent;")
                else:
                    widget['trend_label'].setText("•")
                    widget['trend_label'].setStyleSheet("font-size: 32px; color: #64748b; background: transparent;")
                
                widget['prev_value'] = value
                
                # Update mini chart
                min_val = widget['min']
                max_val = widget['max']
                normalized = ((value - min_val) / (max_val - min_val)) * 100
                widget['chart'].update_value(normalized)
                
            # Update line chart
            if param_id in self.line_charts:
                self.line_charts[param_id].add_value(param['value'], timestamp)
    
    @Slot(str, float)
    def update_single_parameter(self, param_id, value):
        """Update single parameter with trend"""
        timestamp = datetime.now()
        if param_id in self.parameter_widgets:
            widget = self.parameter_widgets[param_id]
            prev_value = widget.get('prev_value', value)
            
            # Update value
            widget['value_label'].setText(f"{value:.1f}")
            
            # Update trend indicator
            if value > prev_value + 0.1:
                widget['trend_label'].setText("▲")
                widget['trend_label'].setStyleSheet("font-size: 32px; color: #059669; background: transparent;")
            elif value < prev_value - 0.1:
                widget['trend_label'].setText("▼")
                widget['trend_label'].setStyleSheet("font-size: 32px; color: #dc2626; background: transparent;")
            else:
                widget['trend_label'].setText("•")
                widget['trend_label'].setStyleSheet("font-size: 32px; color: #64748b; background: transparent;")
            
            widget['prev_value'] = value
            
            # Update mini chart
            min_val = widget['min']
            max_val = widget['max']
            normalized = ((value - min_val) / (max_val - min_val)) * 100
            widget['chart'].update_value(normalized)
        
        # Update line chart
        if param_id in self.line_charts:
            self.line_charts[param_id].add_value(value, timestamp)
