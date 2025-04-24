from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QComboBox,
    QFileDialog, QFormLayout, QDialog, QToolButton,
    QSizePolicy, QStyledItemDelegate
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor
from database.db_connection import execute_query
import os

districts_by_province = {
    "Central Province": [
        "Abau District",
        "Goilala District",
        "Kairuku District",
        "Hiri-Koiari District",
        "Rigo District"
    ],
    "Eastern Highlands Province": [
        "Daulo District",
        "Goroka District",
        "Henganofi District",
        "Kainantu District",
        "Lufa District",
        "Obura-Wonenara District",
        "Okapa District",
        "Unggai-Benna District"
    ],
    "Enga Province": [
        "Kandep District",
        "Kompiam-Ambum District",
        "Lagaip District",
        "Wapenamanda District",
        "Wabag District",
        "Porgera-Paiela District"
    ],
    "Hela Province": [
        "Magarima District",
        "Koroba-Kopiago District",
        "Tari-Pori District",
        "Komo-Hulia District"
    ],
    "Jiwaka Province": [
        "Anglimp-South Waghi District",
        "Jimi District",
        "North Waghi District"
    ],
    "Madang Province": [
        "Bogia District",
        "Madang District",
        "Middle Ramu District",
        "Rai Coast District",
        "Sumkar District",
        "Usino Bundi District"
    ],
    "Manus Province": [
        "Manus District"
    ],
    "Milne Bay Province": [
        "Alotau District",
        "Esa'ala District",
        "Kiriwini-Goodenough District",
        "Samarai-Murua District"
    ],
    "Morobe Province": [
        "Finschhafen District",
        "Huon District",
        "Kabwum District",
        "Lae District",
        "Markham District",
        "Menyamya District",
        "Nawae District",
        "Tawae-Siassi District",
        "Bulolo District",
        "Wau-Waria District"
    ],
    "New Ireland Province": [
        "Kavieng District",
        "Namatanai District"
    ],
    "Oro (Northern) Province": [
        "Ijivitari District",
        "Sohe District",
        "Popondetta District"
    ],
    "Sandaun (West Sepik) Province": [
        "Aitape-Lumi District",
        "Nuku District",
        "Telefomin District",
        "Vanimo-Green River District"
    ],
    "Simbu (Chimbu) Province": [
        "Chuave District",
        "Gumine District",
        "Karimui-Nomane District",
        "Kerowagi District",
        "Kundiawa-Gembogl District",
        "Sina Sina-Yonggomugl District"
    ],
    "Southern Highlands Province": [
        "Ialibu-Pangia District",
        "Imbonggu District",
        "Kagua-Erave District",
        "Mendi-Munihu District",
        "Nipa-Kutubu District"
    ],
    "Western (Fly) Province": [
        "North Fly District",
        "Middle Fly District",
        "South Fly District",
        "Delta Fly District"
    ],
    "Western Highlands Province": [
        "Dei District",
        "Mount Hagen District",
        "Mul-Baiyer District",
        "Tambul-Nebilyer District"
    ],
    "East New Britain Province": [
        "Gazelle District",
        "Kokopo District",
        "Pomio District",
        "Rabaul District"
    ],
    "East Sepik Province": [
        "Ambunti-Dreikikier District",
        "Angoram District",
        "Maprik District",
        "Wewak District",
        "Wosera-Gawi District",
        "Yangoru-Saussia District"
    ],
    "West New Britain Province": [
        "Kandrian-Gloucester District",
        "Talasea District",
        "Nakanai District"
    ],
    "Autonomous Region of Bougainville": [
        "Central Bougainville District",
        "North Bougainville District",
        "South Bougainville District"
    ],
    "National Capital District": [
        "National Capital District"
    ]
}


class AdminDashboardWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("PNG Electoral System - Admin Dashboard")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a6ca8;
            }
            QTableWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QComboBox:hover {
                border: 1px solid #3498db;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Candidate Management")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        
        # Action buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        
        add_btn = QPushButton("Add Candidate")
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        back_btn = QPushButton("Logout")
        back_btn.setIcon(QIcon.fromTheme("system-log-out"))
        
        for btn in [add_btn, refresh_btn, back_btn]:
            btn.setCursor(Qt.PointingHandCursor)
        
        add_btn.clicked.connect(self.show_add_candidate_dialog)
        refresh_btn.clicked.connect(self.load_candidates)
        back_btn.clicked.connect(self.back_to_login)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)
        btn_container.setLayout(btn_layout)
        
        header_layout.addWidget(title)
        header_layout.addWidget(btn_container)
        header.setLayout(header_layout)
        
        # Candidates table with action buttons
        self.candidates_table = QTableWidget()
        self.candidates_table.setColumnCount(7)  # Added action columns
        self.candidates_table.setHorizontalHeaderLabels([
            "ID", "Name", "Party", "Province", "District", "Edit", "Delete"
        ])
        self.candidates_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.candidates_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.candidates_table.verticalHeader().setVisible(False)
        self.candidates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Load initial data
        self.load_candidates()
        
        # Add to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(self.candidates_table)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def load_candidates(self):
        candidates = execute_query("""
            SELECT candidate_id, name, party, province, district 
            FROM candidates
            ORDER BY province, district, name
        """)
        
        self.candidates_table.setRowCount(len(candidates))
        
        for row, candidate in enumerate(candidates):
            # Candidate info
            for col, value in enumerate(candidate[:5]):  # First 5 columns
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.candidates_table.setItem(row, col, item)
            
            # Edit button
            edit_btn = QPushButton()
            edit_btn.setIcon(QIcon.fromTheme("document-edit"))
            edit_btn.setToolTip("Edit candidate")
            edit_btn.setStyleSheet("background-color: #f39c12;")
            edit_btn.clicked.connect(lambda _, r=row: self.edit_candidate(r))
            
            # Delete button
            delete_btn = QPushButton()
            delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
            delete_btn.setToolTip("Delete candidate")
            delete_btn.setStyleSheet("background-color: #e74c3c;")
            delete_btn.clicked.connect(lambda _, r=row: self.delete_candidate(r))
            
            # Add buttons to table
            self.candidates_table.setCellWidget(row, 5, edit_btn)
            self.candidates_table.setCellWidget(row, 6, delete_btn)
    
    def show_add_candidate_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Candidate")
        dialog.setMinimumSize(500, 600)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Add New Candidate")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Form container
        form_container = QWidget()
        form = QFormLayout()
        form.setVerticalSpacing(20)
        form.setLabelAlignment(Qt.AlignLeft)
        
        # Form fields
        self.name_input = QLineEdit()
        self.party_input = QLineEdit()
        
        # Province dropdown with all 22 PNG provinces
        self.province_input = QComboBox()
        provinces = [
            "Central", "Chimbu", "Eastern Highlands", "East New Britain",
            "East Sepik", "Enga", "Gulf", "Madang", "Manus", "Milne Bay",
            "Morobe", "New Ireland", "Oro", "Autonomous Region of Bougainville",
            "Southern Highlands", "Western", "Western Highlands", "West New Britain",
            "West Sepik", "National Capital District", "Hela", "Jiwaka"
        ]
        self.province_input.addItems(provinces)
        self.province_input.setCurrentIndex(-1)  # No default selection
        
        # District dropdown (will be populated based on province)
        self.district_input = QComboBox()
        self.district_input.setEnabled(False)
        self.province_input.currentTextChanged.connect(self.update_districts)
        
        # Photo upload
        self.photo_path = ""
        photo_btn = QPushButton("Upload Photo")
        photo_btn.setIcon(QIcon.fromTheme("insert-image"))
        photo_btn.clicked.connect(self.upload_photo)
        self.photo_label = QLabel("No photo selected")
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        # Add fields to form
        form.addRow("Full Name:", self.name_input)
        form.addRow("Political Party:", self.party_input)
        form.addRow("Province:", self.province_input)
        form.addRow("District:", self.district_input)
        form.addRow("Photo:", photo_btn)
        form.addRow(self.photo_label)
        form_container.setLayout(form)
        
        # Dialog buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        submit_btn = QPushButton("Save Candidate")
        submit_btn.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(QIcon.fromTheme("dialog-cancel"))
        
        submit_btn.clicked.connect(lambda: self.add_candidate(dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(submit_btn)
        btn_container.setLayout(btn_layout)
        
        # Add to dialog
        layout.addWidget(title)
        layout.addWidget(form_container)
        layout.addWidget(btn_container)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def update_districts(self):
        self.district_input.clear()
        province = self.province_input.currentText()
        
        if not province:
            self.district_input.setEnabled(False)
            return
        
        self.district_input.setEnabled(True)
        
        # Sample districts - in a real app you'd load these from your database
        districts = {
            "East Sepik": ["Ambunti-Dreikikir", "Angoram", "Maprik", "Wewak"],
            "Morobe": ["Lae", "Bulolo", "Finschhafen", "Huon Gulf"],
            # Add all other provinces and districts here
        }
        
        if province in districts:
            self.district_input.addItems(districts[province])
        else:
            self.district_input.addItem("Select district")
    
    def upload_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Candidate Photo", "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.photo_path = file_path
            self.photo_label.setText(os.path.basename(file_path))
            self.photo_label.setStyleSheet("color: #2c3e50; font-style: normal;")
    
    def add_candidate(self, dialog):
        name = self.name_input.text().strip()
        party = self.party_input.text().strip()
        province = self.province_input.currentText()
        district = self.district_input.currentText()
        
        if not all([name, party, province, district]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return
        
        try:
            # Read photo if provided
            photo_data = None
            if self.photo_path:
                with open(self.photo_path, 'rb') as f:
                    photo_data = f.read()
            
            execute_query(
                """INSERT INTO candidates 
                (name, party, province, district, photo)
                VALUES (%s, %s, %s, %s, %s)""",
                (name, party, province, district, photo_data)
            )
            
            QMessageBox.information(self, "Success", 
                "Candidate added successfully!")
            self.load_candidates()
            dialog.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error",
                f"Failed to add candidate: {str(e)}")
    
    def edit_candidate(self, row):
        candidate_id = int(self.candidates_table.item(row, 0).text())
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Candidate")
        dialog.setMinimumSize(500, 600)
        dialog.setStyleSheet(self.styleSheet())
        
        # [Similar to add_candidate_dialog but with existing data]
        # Implement similar to add dialog but with pre-filled fields
        # and UPDATE query instead of INSERT
    
    def delete_candidate(self, row):
        candidate_id = int(self.candidates_table.item(row, 0).text())
        candidate_name = self.candidates_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {candidate_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                execute_query(
                    "DELETE FROM candidates WHERE candidate_id = %s",
                    (candidate_id,)
                )
                self.load_candidates()
                QMessageBox.information(self, "Success",
                    "Candidate deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error",
                    f"Failed to delete candidate: {str(e)}")
    
    def back_to_login(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()