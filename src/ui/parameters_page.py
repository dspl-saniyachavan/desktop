"""
Parameters page for telemetry configuration
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QFrame, QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QCheckBox, QDialog, QLineEdit, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPixmap
from typing import Dict
import os

from src.ui.CustomMessageBox import CustomMessageBox1
from src.ui.CustomMessageBox import CustomMessageBox


class ParametersPage(QWidget):
    """Full-page parameters configuration"""
    
    back_clicked = Signal()
    parameters_changed = Signal()
    
    def __init__(self, db_manager=None, auth_service=None, sync_service=None):
        super().__init__()
        self.db = db_manager
        self.auth_service = auth_service
        self.sync_service = sync_service
        self.parameters = self.get_default_parameters()
        self._refresh_pending = False
        self.setup_ui()
        
        # Connect to sync service to receive parameter updates
        if self.sync_service:
            self.sync_service.parameter_synced.connect(self._on_parameter_synced)
    
    def setup_ui(self):
        """Setup parameters page UI"""
        self.setStyleSheet("background-color: #1e293b;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        self.create_header(layout)
        
        # Content
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #1e293b;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Title section
        title_layout = QHBoxLayout()
        
        title_section = QVBoxLayout()
        title_label = QLabel("Telemetry Parameters")
        title_label.setStyleSheet("font-size: 36px; font-weight: 700; color: white;")
        
        subtitle_label = QLabel("Configure which parameters the desktop application should collect")
        subtitle_label.setStyleSheet("font-size: 16px; color: #94a3b8;")
        
        title_section.addWidget(title_label)
        title_section.addWidget(subtitle_label)
        
        title_layout.addLayout(title_section)
        title_layout.addStretch()
        
        # Action buttons (only for admin)
        if self.auth_service and self.db:
            user = self.auth_service.get_current_user()
            if user and self.db.check_permission(user['role'], 'parameters', 'write'):
                add_btn = QPushButton("+ Add Parameter")
                add_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #059669;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 24px;
                        font-weight: 600;
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #047857; }
                """)
                add_btn.clicked.connect(self.add_parameter)
                
                save_btn = QPushButton("Save & Send to Desktop")
                save_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2563eb;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 12px 24px;
                        font-weight: 600;
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #1d4ed8; }
                """)
                save_btn.clicked.connect(self.save_parameters)
                
                title_layout.addWidget(add_btn)
                title_layout.addWidget(save_btn)
        
        content_layout.addLayout(title_layout)
        
        # Info box
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e3a5f;
                border: 1px solid #3b82f6;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        info_label = QLabel(f"{len([p for p in self.parameters if p['enabled']])} of {len(self.parameters)} parameters enabled. Desktop will collect and send only enabled parameters every 3 seconds.")
        info_label.setStyleSheet("color: #93c5fd; font-size: 14px;")
        info_layout.addWidget(info_label)
        content_layout.addWidget(info_frame)
        
        # Parameters table
        self.create_table(content_layout)
        
        layout.addWidget(content_widget)
    
    def create_header(self, layout):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setFixedHeight(90)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2d3748;
                border: none;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo and title
        logo_title_layout = QHBoxLayout()
        logo_title_layout.setSpacing(15)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'logo.svg')
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setStyleSheet("background-color: transparent;")
        else:
            logo_label.setText("⚡")
            logo_label.setStyleSheet("""
                QLabel {
                    background-color: #2563eb;
                    color: white;
                    font-size: 28px;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFixedSize(50, 50)
        
        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        
        title_label = QLabel("PrecisionPulse")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: 700;
                background: transparent;
            }
        """)
        
        subtitle_label = QLabel("Parameter Configuration")
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 14px;
                background: transparent;
            }
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        logo_title_layout.addWidget(logo_label)
        logo_title_layout.addLayout(title_layout)
        
        header_layout.addLayout(logo_title_layout)
        header_layout.addStretch()
        
        # Back button
        back_btn = QPushButton("Back to Dashboard")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #1e293b;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #f1f5f9; }
        """)
        back_btn.clicked.connect(self.back_clicked.emit)
        
        header_layout.addWidget(back_btn)
        layout.addWidget(header_frame)
    
    def create_table(self, layout):
        """Create parameters table"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Status", "Parameter", "Unit", "Description", "Actions"])
        table.setStyleSheet("""
            QTableWidget {
                background-color: #2d3748;
                border: none;
                border-radius: 8px;
                color: white;
                font-size: 14px;
                selection-background-color: #1e3a5f;
            }
            QTableWidget::item {
                padding: 16px;
                border-bottom: 1px solid #374151;
            }
            QTableWidget::item:selected {
                background-color: #1e3a5f;
            }
            QHeaderView::section {
                background-color: #374151;
                color: #9ca3af;
                padding: 16px;
                border: none;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
            }
        """)
        
        table.horizontalHeader().setStretchLastSection(False)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        
        table.setColumnWidth(0, 150)
        table.setColumnWidth(2, 100)
        table.setColumnWidth(4, 150)
        
        table.verticalHeader().setVisible(False)
        table.setRowCount(len(self.parameters))
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        for i, param in enumerate(self.parameters):
            # Status - clickable button
            status_widget = QWidget()
            status_widget.setStyleSheet("background: transparent;")
            status_layout = QHBoxLayout(status_widget)
            status_layout.setContentsMargins(16, 0, 0, 0)
            
            status_btn = QPushButton(f"{'✓' if param['enabled'] else '✗'} {'Enabled' if param['enabled'] else 'Disabled'}")
            status_btn.setProperty('param_index', i)
            status_btn.setCursor(Qt.PointingHandCursor)
            status_btn.setStyleSheet(f"""
                QPushButton {{
                    color: white;
                    background-color: {'#059669' if param['enabled'] else '#dc2626'};
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 12px;
                    border: none;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {'#047857' if param['enabled'] else '#b91c1c'};
                }}
            """)
            status_btn.clicked.connect(lambda checked, idx=i: self.toggle_parameter(idx))
            
            status_layout.addWidget(status_btn)
            status_layout.addStretch()
            table.setCellWidget(i, 0, status_widget)
            
            # Parameter
            param_item = QTableWidgetItem(param['name'])
            param_item.setFlags(param_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(i, 1, param_item)
            
            # Unit
            unit_item = QTableWidgetItem(param['unit'])
            unit_item.setFlags(unit_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(i, 2, unit_item)
            
            # Description
            desc_item = QTableWidgetItem(param['description'])
            desc_item.setForeground(Qt.gray)
            desc_item.setFlags(desc_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(i, 3, desc_item)
            
            # Actions
            actions_widget = QWidget()
            actions_widget.setStyleSheet("background: transparent;")
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 16, 0)
            actions_layout.addStretch()
            
            # Only show remove button for users with write permission
            if self.auth_service and self.db:
                user = self.auth_service.get_current_user()
                if user and self.db.check_permission(user['role'], 'parameters', 'write'):
                    remove_btn = QPushButton("Remove")
                    remove_btn.setProperty('param_index', i)
                    remove_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #dc2626;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 8px 16px;
                            font-weight: 600;
                            font-size: 12px;
                        }
                        QPushButton:hover { background-color: #b91c1c; }
                    """)
                    remove_btn.clicked.connect(lambda checked, idx=i: self.remove_parameter(idx))
                    actions_layout.addWidget(remove_btn)
                else:
                    # Show empty space for non-admin users
                    empty_label = QLabel("View Only")
                    empty_label.setStyleSheet("color: #6b7280; font-size: 12px; font-style: italic;")
                    actions_layout.addWidget(empty_label)
            
            table.setCellWidget(i, 4, actions_widget)
            table.setRowHeight(i, 70)
        
        self.table = table
        layout.addWidget(table)
    
    def toggle_parameter(self, index):
        """Toggle parameter enabled/disabled state"""
        self.parameters[index]['enabled'] = not self.parameters[index]['enabled']
        # Update database
        if self.db:
            self._update_parameter_in_db(self.parameters[index])
        # Publish to MQTT for sync
        if self.sync_service:
            self.sync_service.publish_parameter_change(self.parameters[index], 'update')
        # Recreate the table to update UI
        self.refresh_ui()
        # Notify that parameters changed
        self.parameters_changed.emit()
    
    def refresh_ui(self):
        """Refresh the UI to reflect parameter changes"""
        # Prevent multiple simultaneous refreshes
        if self._refresh_pending:
            return
        self._refresh_pending = True
        # Defer UI update to next event loop cycle
        QTimer.singleShot(0, self._do_refresh_ui)
    
    def _do_refresh_ui(self):
        """Actually perform the UI refresh"""
        try:
            # Update info box
            enabled_count = len([p for p in self.parameters if p['enabled']])
            # Find and update the info label
            for child in self.findChildren(QLabel):
                if 'parameters enabled' in child.text():
                    child.setText(f"{enabled_count} of {len(self.parameters)} parameters enabled. Desktop will collect and send only enabled parameters every 3 seconds.")
                    break
            
            # Recreate table
            if hasattr(self, 'table') and self.table:
                old_table = self.table
                parent_layout = old_table.parent().layout()
                if parent_layout:
                    parent_layout.removeWidget(old_table)
                    old_table.deleteLater()
                    self.create_table(parent_layout)
        except Exception as e:
            print(f"Error in _do_refresh_ui: {e}")
        finally:
            self._refresh_pending = False
    
    def remove_parameter(self, index):
        """Remove parameter from list"""
        from PySide6.QtWidgets import QMessageBox
        param = self.parameters[index]
        msg = CustomMessageBox1("Confirm Action", "Do you want to delete this user")
        result = msg.exec()  # Waits for user input

        
        
        if result == QDialog.Accepted:
            # Delete from database
            if self.db:
                self._delete_parameter_from_db(param['id'])
            # Publish delete to MQTT for sync
            if self.sync_service:
                self.sync_service.publish_parameter_change(param, 'delete')
            self.parameters.pop(index)
            self.refresh_ui()
            # Notify that parameters changed
            self.parameters_changed.emit()
    
    def add_parameter(self):
        """Show add parameter dialog"""
        from PySide6.QtWidgets import  QApplication
        
        overlay = QWidget(self)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")
        overlay.show()
        
        dialog = AddParameterDialog(self)
        
        screen = QApplication.primaryScreen().geometry()
        dialog.move(
            screen.center().x() - dialog.width() // 2,
            screen.center().y() - dialog.height() // 2
        )
        
        result = dialog.exec()
        overlay.deleteLater()
        
        if result:
            param_data = dialog.get_parameter_data()
            self.parameters.append(param_data)
            # Update database
            if self.db:
                self._add_parameter_to_db(param_data)
            # Publish to MQTT for sync
            if self.sync_service:
                self.sync_service.publish_parameter_change(param_data, 'add')
            self.refresh_ui()
            # Notify that parameters changed
            self.parameters_changed.emit()
    
    def get_default_parameters(self):
        """Get parameters from database or defaults"""
        if self.db:
            return self._load_parameters_from_db()
        return [
            {'id': 'temp', 'name': 'Temperature', 'unit': '°C', 'enabled': True, 'description': 'Ambient temperature sensor'},
            {'id': 'pressure', 'name': 'Pressure', 'unit': 'kPa', 'enabled': True, 'description': 'System pressure measurement'},
            {'id': 'flow', 'name': 'Flow Rate', 'unit': 'L/s', 'enabled': False, 'description': 'Liquid flow rate'},
            {'id': 'humidity', 'name': 'Humidity', 'unit': '%', 'enabled': True, 'description': 'Relative humidity'},
            {'id': 'voltage', 'name': 'Voltage', 'unit': 'V', 'enabled': True, 'description': 'System voltage'},
            {'id': 'custom', 'name': 'custom', 'unit': 'l/s', 'enabled': True, 'description': 'd'},
        ]
    
    def _load_parameters_from_db(self):
        """Load parameters from database"""
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, unit, enabled, description FROM parameters')
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'unit': row[2],
                    'enabled': bool(row[3]),
                    'description': row[4] or ''
                }
                for row in cursor.fetchall()
            ]
    
    def save_parameters(self):
        """Save parameters configuration"""
        from PySide6.QtWidgets import QMessageBox
        # Update all parameters in database
        if self.db:
            for param in self.parameters:
                self._update_parameter_in_db(param)
                msg = CustomMessageBox("Success", "parameter saved successfully!")
                msg.exec()
        # Notify that parameters changed
        self.parameters_changed.emit()
    
    def _update_parameter_in_db(self, param: Dict):
        """Update parameter in database"""
        if self.db:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO parameters (id, name, unit, enabled, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (param['id'], param['name'], param['unit'], param['enabled'], param.get('description', '')))
                conn.commit()
    
    def _add_parameter_to_db(self, param: Dict):
        """Add new parameter to database"""
        self._update_parameter_in_db(param)
    
    def _delete_parameter_from_db(self, param_id: str):
        """Delete parameter from database"""
        if self.db:
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM parameters WHERE id = ?', (param_id,))
                conn.commit()
    
    def _on_parameter_synced(self, parameter):
        """Handle parameter sync from remote"""
        try:
            print(f" Parameters page received sync: {parameter.get('name')}")
            # Reload parameters from database
            self.parameters = self._load_parameters_from_db()
            # Refresh UI with debouncing
            self.refresh_ui()
        except Exception as e:
            print(f"Error in _on_parameter_synced: {e}")


class AddParameterDialog(QDialog):
    """Dialog for adding new parameters"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup dialog UI"""
        self.setWindowTitle("")
        self.setModal(True)
        self.setFixedSize(500, 580)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main container with rounded corners
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #374151;
                border-radius: 16px;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Add New Parameter")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: white;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Parameter Name
        name_label = QLabel("Parameter Name")
        name_label.setStyleSheet("color: #e5e7eb; font-size: 14px; font-weight: 600;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Temperature")
        self.name_input.setFixedHeight(45)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 0 16px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(self.name_input)
        
        # Unit
        unit_label = QLabel("Unit")
        unit_label.setStyleSheet("color: #e5e7eb; font-size: 14px; font-weight: 600; margin-top: 10px;")
        layout.addWidget(unit_label)
        
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("e.g., °C, kPa, L/s")
        self.unit_input.setFixedHeight(45)
        self.unit_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 0 16px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(self.unit_input)
        
        # Description
        desc_label = QLabel("Description")
        desc_label.setStyleSheet("color: #e5e7eb; font-size: 14px; font-weight: 600; margin-top: 10px;")
        layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Brief description of this parameter")
        self.desc_input.setFixedHeight(100)
        self.desc_input.setStyleSheet("""
            QTextEdit {
                background-color: #1e293b;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
            }
        """)
        layout.addWidget(self.desc_input)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        add_btn = QPushButton("Add Parameter")
        add_btn.setFixedHeight(45)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        add_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b5563;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 24px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        main_layout.addWidget(container)
    
    def get_parameter_data(self):
        """Get parameter data from form"""
        import time
        return {
            'id': f"param_{int(time.time())}",
            'name': self.name_input.text() or "New Parameter",
            'unit': self.unit_input.text() or "unit",
            'description': self.desc_input.toPlainText() or "No description",
            'enabled': True
        }
