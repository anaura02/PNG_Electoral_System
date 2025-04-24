from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QLineEdit, QComboBox,
    QFileDialog, QFormLayout, QDialog, QToolButton,
    QSizePolicy, QStyledItemDelegate, QDateTimeEdit,
    QTabWidget, QGroupBox, QRadioButton
)
from PyQt5.QtCore import Qt, QSize, QDateTime, QBuffer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QImage
from database.db_connection import execute_query, create_connection
import os
import base64

# Dictionary of provinces and their districts
districts_by_province = {
    "Central": ["Abau", "Goilala", "Kairuku-Hiri", "Rigo"],
    "East New Britain": ["Gazelle", "Kokopo", "Pomio", "Rabaul"],
    "East Sepik": ["Ambunti-Dreikikier", "Angoram", "Maprik", "Wewak", "Wosera-Gawi", "Yangoru-Saussia"],
    "Eastern Highlands": ["Daulo", "Goroka", "Henganofi", "Kainantu", "Lufa", "Obura-Wonenara", "Okapa", "Unggai-Bena"],
    "Enga": ["Kandep", "Kompiam-Ambum", "Lagaip-Porgera", "Wabag", "Wapenamanda"],
    "Gulf": ["Kerema", "Kikori"],
    "Hela": ["Komo-Margarima", "Koroba-Lake Kopiago", "Tari-Pori"],
    "Jiwaka": ["Anglimp-South Waghi", "Jimi", "North Waghi"],
    "Madang": ["Bogia", "Madang", "Middle Ramu", "Rai Coast", "Sumkar", "Usino-Bundi"],
    "Manus": ["Manus"],
    "Milne Bay": ["Alotau", "Esa'ala", "Kiriwina-Goodenough", "Samarai-Murua"],
    "Morobe": ["Bulolo", "Finschhafen", "Huon-Gulf", "Kabwum", "Lae", "Markham", "Menyamya", "Nawae", "Tewai-Siassi"],
    "National Capital District": ["Moresby North-East", "Moresby North-West", "Moresby South"],
    "New Ireland": ["Kavieng", "Namatanai"],
    "Northern": ["Ijivitari", "Sohe"],
    "Southern Highlands": ["Ialibu-Pangia", "Imbonggu", "Kagua-Erave", "Mendi-Munihu", "Nipa-Kutubu"],
    "West New Britain": ["Kandrian-Gloucester", "Talasea"],
    "West Sepik": ["Aitape-Lumi", "Nuku", "Telefomin", "Vanimo-Green River"],
    "Western": ["Middle Fly", "North Fly", "South Fly"],
    "Western Highlands": ["Dei", "Hagen", "Mul-Baiyer", "Tambul-Nebilyer"]
}

class AdminDashboardWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        # Get admin name from database
        admin_data = execute_query(
            "SELECT full_name FROM users WHERE user_id = %s",
            (user_id,)
        )
        
        if admin_data:
            self.admin_name = admin_data[0][0]
        else:
            self.admin_name = "Administrator"
        
        self.setup_ui()
        self.show()
    
    def setup_ui(self):
        self.setWindowTitle("Electoral System - Admin Dashboard")
        self.setMinimumSize(1000, 700)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50; color: white;")
        header.setMinimumHeight(80)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        # Logo/Title
        title = QLabel("Electoral System - Admin Dashboard")
        title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        
        # User info
        user_info = QLabel(f"Admin: {self.admin_name}")
        user_info.setFont(QFont('Segoe UI', 10))
        user_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                border-radius: 3px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)
        header_layout.addWidget(logout_btn)
        header.setLayout(header_layout)
        
        # Create a tab widget for different admin functions
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e0e0e0;
                background: white;
            }
            QTabBar::tab {
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                padding: 10px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # Candidate management tab
        candidate_tab = QWidget()
        candidate_layout = QVBoxLayout()
        candidate_layout.setContentsMargins(20, 20, 20, 20)
        candidate_layout.setSpacing(20)
        
        # Title
        candidates_title = QLabel("Candidate Management")
        candidates_title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        candidates_title.setStyleSheet("color: #2c3e50;")
        
        # Action buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        add_btn = QPushButton("Add Candidate")
        add_btn.setIcon(QIcon.fromTheme("list-add"))
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_candidate)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setIcon(QIcon.fromTheme("view-refresh"))
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.load_candidates)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_container.setLayout(btn_layout)
        
        # Candidates table
        self.candidates_table = QTableWidget()
        self.candidates_table.setColumnCount(7)
        self.candidates_table.setHorizontalHeaderLabels([
            "ID", "Name", "Party", "Province", "District", "Photo", "Actions"
        ])
        self.candidates_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.candidates_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.candidates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.candidates_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.candidates_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.candidates_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.candidates_table.verticalHeader().setVisible(False)
        self.candidates_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # Add to candidate tab layout
        candidate_layout.addWidget(candidates_title)
        candidate_layout.addWidget(btn_container)
        candidate_layout.addWidget(self.candidates_table)
        candidate_tab.setLayout(candidate_layout)
        
        # Voting control tab
        voting_control_tab = self.setup_voting_control()
        
        # Add tabs to tab widget
        tab_widget.addTab(candidate_tab, "Candidate Management")
        tab_widget.addTab(voting_control_tab, "Voting Control")
        
        # Add components to main layout
        main_layout.addWidget(header)
        main_layout.addWidget(tab_widget)
        
        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Load candidates
        self.load_candidates()
    
    def setup_voting_control(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Voting Control Panel")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        # Voting schedule group
        schedule_group = QGroupBox("Voting Schedule")
        schedule_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        schedule_layout = QFormLayout()
        schedule_layout.setLabelAlignment(Qt.AlignRight)
        schedule_layout.setFormAlignment(Qt.AlignLeft)
        schedule_layout.setSpacing(15)
        
        # Get current end time if set
        current_end_time = execute_query("SELECT value FROM system_settings WHERE key = 'voting_end_time'")
        end_time = QDateTime.currentDateTime().addDays(1)
        
        if current_end_time and current_end_time[0][0]:
            try:
                end_time = QDateTime.fromString(current_end_time[0][0], "yyyy-MM-dd hh:mm:ss")
            except:
                pass
        
        # Date/time picker
        self.end_time_edit = QDateTimeEdit(end_time)
        self.end_time_edit.setCalendarPopup(True)
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.end_time_edit.setMinimumDateTime(QDateTime.currentDateTime())
        self.end_time_edit.setStyleSheet("""
            QDateTimeEdit {
                padding: 8px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        
        # Set schedule button
        set_schedule_btn = QPushButton("Set Voting End Time")
        set_schedule_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        set_schedule_btn.clicked.connect(self.set_voting_end_time)
        
        schedule_layout.addRow("Voting Ends At:", self.end_time_edit)
        schedule_layout.addRow("", set_schedule_btn)
        schedule_group.setLayout(schedule_layout)
        
        # Voting control group
        control_group = QGroupBox("Voting Status Control")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        control_layout = QVBoxLayout()
        control_layout.setSpacing(15)
        
        # Get current voting status
        voting_status = execute_query("SELECT value FROM system_settings WHERE key = 'voting_status'")
        is_open = True
        
        if voting_status and voting_status[0][0] == 'closed':
            is_open = False
        
        # Status label
        self.voting_status_label = QLabel()
        self.update_voting_status_label(is_open)
        self.voting_status_label.setFont(QFont('Segoe UI', 12))
        self.voting_status_label.setAlignment(Qt.AlignCenter)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        close_voting_btn = QPushButton("Close Voting & Declare Winners")
        close_voting_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        close_voting_btn.clicked.connect(lambda: self.set_voting_status(False))
        
        open_voting_btn = QPushButton("Open Voting")
        open_voting_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        open_voting_btn.clicked.connect(lambda: self.set_voting_status(True))
        
        btn_layout.addWidget(open_voting_btn)
        btn_layout.addWidget(close_voting_btn)
        
        control_layout.addWidget(self.voting_status_label)
        control_layout.addLayout(btn_layout)
        control_group.setLayout(control_layout)
        
        # Results group
        results_group = QGroupBox("Election Results")
        results_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                margin-top: 1ex;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """)
        results_layout = QVBoxLayout()
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Candidate", "Party", "Total Points"])
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # Refresh results button
        refresh_results_btn = QPushButton("Refresh Results")
        refresh_results_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_results_btn.clicked.connect(self.load_results)
        
        results_layout.addWidget(self.results_table)
        results_layout.addWidget(refresh_results_btn)
        results_group.setLayout(results_layout)
        
        # Add the "Clear All Votes" button (as per instructions)
        self.clear_votes_btn = QPushButton("Clear All Votes")
        self.clear_votes_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.clear_votes_btn.clicked.connect(self.clear_all_votes)
        layout.addWidget(self.clear_votes_btn)  # Add this to your existing layout
        
        # Add everything to the main layout
        layout.addWidget(title)
        layout.addWidget(schedule_group)
        layout.addWidget(control_group)
        layout.addWidget(results_group)
        
        tab.setLayout(layout)
        
        # Load initial results
        self.load_results()
        
        return tab
    
    
    def clear_all_votes(self):
        """Clear all votes from the database"""
        reply = QMessageBox.question(
            self, 'Confirm Clear Votes',
            "Are you sure you want to clear ALL votes from the system?\n\n"
            "This action cannot be undone and will remove all voting data.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Clear votes from database
        from database.db_connection import execute_query
        
        result = execute_query("DELETE FROM votes")
        
        if result:
            QMessageBox.information(self, "Success", "All votes have been cleared successfully!")
            # Refresh any displays that show vote counts
            if hasattr(self, 'refresh_data'):
                self.refresh_data()
        else:
            QMessageBox.critical(self, "Error", "Failed to clear votes. Please try again.")
    
    def refresh_data(self):
        """Refresh all data displays"""
        # Update any tables or displays that show vote counts
        # For example, if you have a candidates table:
        if hasattr(self, 'candidates_table'):
            self.load_candidates()
        
        # If you have a votes summary:
        if hasattr(self, 'votes_summary'):
            self.update_votes_summary()
    
    
    def update_voting_status_label(self, is_open):
        if is_open:
            self.voting_status_label.setText("Voting is currently OPEN")
            self.voting_status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.voting_status_label.setText("Voting is currently CLOSED")
            self.voting_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def set_voting_end_time(self):
        end_time = self.end_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        try:
            execute_query(
                "UPDATE system_settings SET value = %s WHERE key = 'voting_end_time'",
                (end_time,)
            )
            QMessageBox.information(self, "Success", "Voting end time has been set successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set voting end time: {str(e)}")
    
    def set_voting_status(self, is_open):
        status = 'open' if is_open else 'closed'
        
        # Confirm before closing voting
        if not is_open:
            reply = QMessageBox.question(
                self, 'Confirm Close Voting',
                "Are you sure you want to close voting and declare winners? This action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        try:
            execute_query(
                "UPDATE system_settings SET value = %s WHERE key = 'voting_status'",
                (status,)
            )
            
            self.update_voting_status_label(is_open)
            
            if not is_open:
                self.load_results()
                QMessageBox.information(self, "Success", "Voting has been closed and winners declared!")
            else:
                QMessageBox.information(self, "Success", "Voting has been opened!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update voting status: {str(e)}")
    
    def load_results(self):
        try:
            # Calculate results - 3 points for 1st preference, 2 for 2nd, 1 for 3rd
            results = execute_query("""
                SELECT c.name, c.party, 
                       SUM(CASE WHEN v.preference = 1 THEN 3
                                WHEN v.preference = 2 THEN 2
                                WHEN v.preference = 3 THEN 1
                                ELSE 0 END) as total_points
                FROM candidates c
                LEFT JOIN votes v ON c.candidate_id = v.candidate_id
                GROUP BY c.candidate_id, c.name, c.party
                ORDER BY total_points DESC
            """)
            
            self.results_table.setRowCount(0)
            
            if not results:
                return
            
            for row_idx, (name, party, points) in enumerate(results):
                self.results_table.insertRow(row_idx)
                self.results_table.setItem(row_idx, 0, QTableWidgetItem(name))
                self.results_table.setItem(row_idx, 1, QTableWidgetItem(party))
                self.results_table.setItem(row_idx, 2, QTableWidgetItem(str(points or 0)))
                
                # Highlight the winner(s)
                if row_idx == 0:
                    for col in range(3):
                        item = self.results_table.item(row_idx, col)
                        item.setBackground(QColor(46, 204, 113, 100))  # Light green
                        item.setFont(QFont('Segoe UI', 10, QFont.Bold))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load results: {str(e)}")
    
    def load_candidates(self):
        try:
            candidates = execute_query("""
                SELECT candidate_id, name, party, province, district, photo
                FROM candidates
                ORDER BY name
            """)
            
            self.candidates_table.setRowCount(0)
            
            if not candidates:
                return
            
            for row_idx, (candidate_id, name, party, province, district, photo) in enumerate(candidates):
                self.candidates_table.insertRow(row_idx)
                
                # ID
                id_item = QTableWidgetItem(str(candidate_id))
                id_item.setTextAlignment(Qt.AlignCenter)
                self.candidates_table.setItem(row_idx, 0, id_item)
                
                # Name
                self.candidates_table.setItem(row_idx, 1, QTableWidgetItem(name))
                
                # Party
                self.candidates_table.setItem(row_idx, 2, QTableWidgetItem(party))
                
                # Province
                self.candidates_table.setItem(row_idx, 3, QTableWidgetItem(province))
                
                # District
                self.candidates_table.setItem(row_idx, 4, QTableWidgetItem(district))
                
                # Photo
                photo_cell = QTableWidgetItem()
                photo_cell.setTextAlignment(Qt.AlignCenter)
                
                if photo:
                    photo_cell.setText("View")
                    photo_cell.setForeground(QColor(52, 152, 219))  # Blue
                else:
                    photo_cell.setText("None")
                    photo_cell.setForeground(QColor(189, 195, 199))  # Gray
                
                self.candidates_table.setItem(row_idx, 5, photo_cell)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout()
                actions_layout.setContentsMargins(5, 0, 5, 0)
                actions_layout.setSpacing(5)
                
                edit_btn = QToolButton()
                edit_btn.setIcon(QIcon.fromTheme("document-edit"))
                edit_btn.setToolTip("Edit Candidate")
                edit_btn.setCursor(Qt.PointingHandCursor)
                edit_btn.clicked.connect(lambda _, cid=candidate_id: self.edit_candidate(cid))
                
                delete_btn = QToolButton()
                delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
                delete_btn.setToolTip("Delete Candidate")
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.clicked.connect(lambda _, cid=candidate_id: self.delete_candidate(cid))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                actions_layout.addStretch()
                
                actions_widget.setLayout(actions_layout)
                self.candidates_table.setCellWidget(row_idx, 6, actions_widget)
            
            # Connect double-click on photo cell to view photo
            self.candidates_table.cellDoubleClicked.connect(self.handle_cell_double_click)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load candidates: {str(e)}")
    
    def handle_cell_double_click(self, row, column):
        if column == 5 and self.candidates_table.item(row, column).text() == "View":
            candidate_id = int(self.candidates_table.item(row, 0).text())
            self.view_candidate_photo(candidate_id)
    
    def view_candidate_photo(self, candidate_id):
        try:
            photo_data = execute_query(
                "SELECT photo, name FROM candidates WHERE candidate_id = %s",
                (candidate_id,)
            )
            
            if not photo_data or not photo_data[0][0]:
                QMessageBox.information(self, "No Photo", "No photo available for this candidate.")
                return
            
            photo_bytes, name = photo_data[0]
            
            # Create a dialog to display the photo
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Photo: {name}")
            dialog.setMinimumSize(400, 500)
            
            layout = QVBoxLayout()
            
            # Convert photo bytes to QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(photo_bytes)
            
            # Scale pixmap to fit dialog while maintaining aspect ratio
            pixmap = pixmap.scaled(380, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            photo_label = QLabel()
            photo_label.setPixmap(pixmap)
            photo_label.setAlignment(Qt.AlignCenter)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            
            layout.addWidget(photo_label)
            layout.addWidget(close_btn)
            dialog.setLayout(layout)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load photo: {str(e)}")
    
    def add_candidate(self):
        """Open dialog to add a new candidate"""
        # Create dialog
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
        name_input = QLineEdit()
        party_input = QLineEdit()
        
        # Province dropdown
        province_input = QComboBox()
        provinces = list(districts_by_province.keys())
        province_input.addItems(provinces)
        
        # District dropdown
        district_input = QComboBox()
        district_input.setEnabled(False)
        
        # Update districts when province changes
        def update_districts():
            district_input.clear()
            province = province_input.currentText()
            
            if not province:
                district_input.setEnabled(False)
                return
            
            district_input.setEnabled(True)
            
            # Use the districts_by_province dictionary to populate districts
            if province in districts_by_province:
                district_input.addItems(districts_by_province[province])
        
        province_input.currentTextChanged.connect(update_districts)
        
        # Photo upload
        photo_path = ""
        
        def upload_photo():
            nonlocal photo_path
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "Select Candidate Photo", "", "Image Files (*.png *.jpg *.jpeg)"
            )
            if file_path:
                photo_path = file_path
                photo_label.setText(f"Selected: {os.path.basename(file_path)}")
        
        photo_btn = QPushButton("Upload Photo")
        photo_btn.setIcon(QIcon.fromTheme("insert-image"))
        photo_btn.clicked.connect(upload_photo)
        photo_label = QLabel("No photo selected")
        photo_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        
        # Add fields to form
        form.addRow("Full Name:", name_input)
        form.addRow("Political Party:", party_input)
        form.addRow("Province:", province_input)
        form.addRow("District:", district_input)
        form.addRow("Photo:", photo_btn)
        form.addRow("", photo_label)
        
        form_container.setLayout(form)
        
        # Dialog buttons
        btn_container = QWidget()
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        
        def save_candidate():
            # Get values from form
            name = name_input.text().strip()
            party = party_input.text().strip()
            province = province_input.currentText()
            district = district_input.currentText()
            
            if not all([name, party, province, district]):
                QMessageBox.warning(dialog, "Error", "All fields are required")
                return
            
            try:
                # Process photo if selected
                photo_data = None
                if photo_path:
                    with open(photo_path, 'rb') as f:
                        photo_data = f.read()
                
                # Insert candidate into database
                execute_query(
                    """INSERT INTO candidates (name, party, province, district, photo)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (name, party, province, district, photo_data)
                )
                
                QMessageBox.information(dialog, "Success", "Candidate added successfully!")
                self.load_candidates()  # Refresh the table
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error",
                    f"Failed to add candidate: {str(e)}")
        
        submit_btn = QPushButton("Add Candidate")
        submit_btn.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setIcon(QIcon.fromTheme("dialog-cancel"))
        
        submit_btn.clicked.connect(save_candidate)
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
        
        # Initialize districts
        update_districts()
        
        # Show dialog
        dialog.exec_()
    
    def edit_candidate(self, candidate_id):
        """Open dialog to edit an existing candidate"""
        try:
            # Get candidate data
            candidate_data = execute_query(
                """SELECT name, party, province, district, photo 
                   FROM candidates WHERE candidate_id = %s""",
                (candidate_id,)
            )
            
            if not candidate_data:
                QMessageBox.warning(self, "Error", "Candidate not found")
                return
            
            name, party, province, district, photo = candidate_data[0]
            
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Candidate")
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
            title = QLabel("Edit Candidate")
            title.setFont(QFont('Segoe UI', 16, QFont.Bold))
            title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
            
            # Form container
            form_container = QWidget()
            form = QFormLayout()
            form.setVerticalSpacing(20)
            form.setLabelAlignment(Qt.AlignLeft)
            
            # Form fields
            name_input = QLineEdit(name)
            party_input = QLineEdit(party)
            
            # Province dropdown
            province_input = QComboBox()
            provinces = list(districts_by_province.keys())
            province_input.addItems(provinces)
            province_input.setCurrentText(province)
            
            # District dropdown
            district_input = QComboBox()
            
            # Update districts when province changes
            def update_districts():
                district_input.clear()
                current_province = province_input.currentText()
                
                if not current_province:
                    district_input.setEnabled(False)
                    return
                
                district_input.setEnabled(True)
                
                # Use the districts_by_province dictionary to populate districts
                if current_province in districts_by_province:
                    district_input.addItems(districts_by_province[current_province])
                    
                    # Try to set the previous district if it exists in the new province
                    if district in districts_by_province[current_province]:
                        district_input.setCurrentText(district)
            
            province_input.currentTextChanged.connect(update_districts)
            
            # Initialize districts
            update_districts()
            
            # Photo upload
            photo_path = ""
            
            def upload_photo():
                nonlocal photo_path
                file_path, _ = QFileDialog.getOpenFileName(
                    dialog, "Select Candidate Photo", "", "Image Files (*.png *.jpg *.jpeg)"
                )
                if file_path:
                    photo_path = file_path
                    photo_label.setText(f"Selected: {os.path.basename(file_path)}")
            
            photo_btn = QPushButton("Upload New Photo")
            photo_btn.setIcon(QIcon.fromTheme("insert-image"))
            photo_btn.clicked.connect(upload_photo)
            
            photo_label = QLabel("Keep existing photo" if photo else "No photo")
            photo_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
            
            # View current photo button
            view_photo_btn = QPushButton("View Current Photo")
            view_photo_btn.setEnabled(photo is not None)
            view_photo_btn.clicked.connect(lambda: self.view_candidate_photo(candidate_id))
            
            # Add fields to form
            form.addRow("Full Name:", name_input)
            form.addRow("Political Party:", party_input)
            form.addRow("Province:", province_input)
            form.addRow("District:", district_input)
            form.addRow("Current Photo:", view_photo_btn)
            form.addRow("New Photo:", photo_btn)
            form.addRow("", photo_label)
            
            form_container.setLayout(form)
            
            # Dialog buttons
            btn_container = QWidget()
            btn_layout = QHBoxLayout()
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(10)
            
            def save_candidate():
                # Get values from form
                new_name = name_input.text().strip()
                new_party = party_input.text().strip()
                new_province = province_input.currentText()
                new_district = district_input.currentText()
                
                if not all([new_name, new_party, new_province, new_district]):
                    QMessageBox.warning(dialog, "Error", "All fields are required")
                    return
                
                try:
                    # Process photo if a new one was selected
                    if photo_path:
                        with open(photo_path, 'rb') as f:
                            photo_data = f.read()
                        
                        # Update with new photo
                        execute_query(
                            """UPDATE candidates 
                               SET name = %s, party = %s, province = %s, district = %s, photo = %s
                               WHERE candidate_id = %s""",
                            (new_name, new_party, new_province, new_district, photo_data, candidate_id)
                        )
                    else:
                        # Update without changing photo
                        execute_query(
                            """UPDATE candidates 
                               SET name = %s, party = %s, province = %s, district = %s
                               WHERE candidate_id = %s""",
                            (new_name, new_party, new_province, new_district, candidate_id)
                        )
                    
                    QMessageBox.information(dialog, "Success", "Candidate updated successfully!")
                    self.load_candidates()  # Refresh the table
                    dialog.accept()
                    
                except Exception as e:
                    QMessageBox.critical(dialog, "Error",
                        f"Failed to update candidate: {str(e)}")
            
            submit_btn = QPushButton("Save Changes")
            submit_btn.setIcon(QIcon.fromTheme("dialog-ok-apply"))
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setIcon(QIcon.fromTheme("dialog-cancel"))
            
            submit_btn.clicked.connect(save_candidate)
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
            
            # Show dialog
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to edit candidate: {str(e)}")
    
    def delete_candidate(self, candidate_id):
        """Delete a candidate after confirmation"""
        try:
            # Get candidate name
            candidate_data = execute_query(
                "SELECT name FROM candidates WHERE candidate_id = %s",
                (candidate_id,)
            )
            
            if not candidate_data:
                QMessageBox.warning(self, "Error", "Candidate not found")
                return
            
            candidate_name = candidate_data[0][0]
            
            # Confirm deletion
            reply = QMessageBox.question(
                self, 'Confirm Deletion',
                f"Are you sure you want to delete candidate '{candidate_name}'?\n\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            # Check if candidate has votes
            votes = execute_query(
                "SELECT COUNT(*) FROM votes WHERE candidate_id = %s",
                (candidate_id,)
            )
            
            if votes and votes[0][0] > 0:
                # If candidate has votes, ask for confirmation again
                reply = QMessageBox.warning(
                    self, 'Votes Exist',
                    f"Candidate '{candidate_name}' has received votes. Deleting will also remove all votes for this candidate.\n\nAre you absolutely sure you want to proceed?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
                
                # Delete votes first
                execute_query(
                    "DELETE FROM votes WHERE candidate_id = %s",
                    (candidate_id,)
                )
            
            # Delete candidate
            execute_query(
                "DELETE FROM candidates WHERE candidate_id = %s",
                (candidate_id,)
            )
            
            QMessageBox.information(self, "Success", f"Candidate '{candidate_name}' has been deleted.")
            self.load_candidates()  # Refresh the table
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete candidate: {str(e)}")
    
    def logout(self):
        """Handle admin logout"""
        reply = QMessageBox.question(
            self, 'Confirm Logout',
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
