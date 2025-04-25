from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from database.db_connection import execute_query
import csv
import datetime

class AuditTab(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Audit Log")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        # Export button
        export_btn = QPushButton("Export Audit Log")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a6ca8;
            }
        """)
        export_btn.clicked.connect(self.export_audit_log)
        
        # Audit log table
        self.audit_table = QTableWidget()
        self.audit_table.setColumnCount(5)
        
        # Custom header
        self.audit_table.setRowCount(1)
        header_labels = ["Timestamp", "User", "Action", "Details", "IP Address"]
        
        for col, label in enumerate(header_labels):
            header_item = QTableWidgetItem(label)
            header_item.setBackground(QColor("#2c3e50"))
            header_item.setForeground(QColor("white"))
            font = header_item.font()
            font.setBold(True)
            header_item.setFont(font)
            header_item.setTextAlignment(Qt.AlignCenter)
            self.audit_table.setItem(0, col, header_item)
        
        # Set column widths
        self.audit_table.setColumnWidth(0, 180)  # Timestamp
        self.audit_table.setColumnWidth(1, 150)  # User
        self.audit_table.setColumnWidth(2, 150)  # Action
        self.audit_table.setColumnWidth(3, 300)  # Details
        self.audit_table.setColumnWidth(4, 150)  # IP Address
        
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audit_table.verticalHeader().setVisible(False)
        self.audit_table.horizontalHeader().setVisible(False)
        
        # Add to layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(self.audit_table)
        
        self.setLayout(layout)
        
        # Load audit data
        self.load_audit_data()
        
    def load_audit_data(self):
        """Load audit log data from database"""
        audit_data = execute_query("""
            SELECT a.timestamp, u.full_name, a.action, a.details, a.ip_address
            FROM audit_log a
            LEFT JOIN users u ON a.user_id = u.user_id
            ORDER BY a.timestamp DESC
        """)
        
        if audit_data:
            # Set row count (add 1 for header)
            self.audit_table.setRowCount(len(audit_data) + 1)
            
            for row, (timestamp, username, action, details, ip) in enumerate(audit_data):
                # Adjust row index for header
                table_row = row + 1
                
                # Format timestamp
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                # Create items
                time_item = QTableWidgetItem(formatted_time)
                user_item = QTableWidgetItem(username or "Unknown")
                action_item = QTableWidgetItem(action)
                details_item = QTableWidgetItem(details or "")
                ip_item = QTableWidgetItem(ip or "")
                
                # Center align
                for item in [time_item, user_item, action_item, ip_item]:
                    item.setTextAlignment(Qt.AlignCenter)
                
                # Add to table
                self.audit_table.setItem(table_row, 0, time_item)
                self.audit_table.setItem(table_row, 1, user_item)
                self.audit_table.setItem(table_row, 2, action_item)
                self.audit_table.setItem(table_row, 3, details_item)
                self.audit_table.setItem(table_row, 4, ip_item)
        
    def export_audit_log(self):
        """Export audit log to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Audit Log", 
            f"audit_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )
        
        if not filename:
            return
            
        try:
            # Get audit data
            audit_data = execute_query("""
                SELECT a.timestamp, u.full_name, a.action, a.details, a.ip_address
                FROM audit_log a
                LEFT JOIN users u ON a.user_id = u.user_id
                ORDER BY a.timestamp DESC
            """)
            
            if not audit_data:
                QMessageBox.warning(self, "No Data", "There is no audit data to export.")
                return
                
            # Write to CSV
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "User", "Action", "Details", "IP Address"])
                
                for row in audit_data:
                    # Format timestamp
                    formatted_time = row[0].strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([formatted_time, row[1] or "Unknown", row[2], row[3] or "", row[4] or ""])
                    
            QMessageBox.information(self, "Export Successful", 
                                 f"Audit log has been exported to {filename}")
                                 
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export audit log: {str(e)}")
