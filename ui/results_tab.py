from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QTableWidget, QTableWidgetItem,
    QPushButton, QFrame, QGridLayout, QSplitter,
    QHeaderView
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QColor, QIcon, QPalette
from database.db_connection import execute_query

class ResultsTab(QWidget):
    def __init__(self, user_id):
        super().__init__()
        
        # If user_id is a dictionary, extract the ID
        if isinstance(user_id, dict):
            self.user_data = user_id
            self.user_id = user_id['user_id']
        else:
            self.user_id = user_id
            
        # PNG Provinces in alphabetical order
        self.provinces = [
            "Bougainville", "Central", "Chimbu", "East New Britain", 
            "East Sepik", "Eastern Highlands", "Enga", "Gulf", 
            "Hela", "Jiwaka", "Madang", "Manus", "Milne Bay", 
            "Morobe", "New Ireland", "Oro", "Southern Highlands", 
            "West New Britain", "West Sepik", "Western", "Western Highlands"
        ]
        
        # Initialize UI
        self.setup_ui()
        
        # Set up refresh timer (every 60 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_current_results)
        self.refresh_timer.start(60000)  # 60 seconds
        
        # Track current district
        self.current_district = None
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header section
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Election Results")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        # Instructions
        instructions = QLabel(
            "View election results by province and district. Results update automatically every minute."
        )
        instructions.setFont(QFont('Segoe UI', 10))
        instructions.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(instructions)
        
        # Content section
        content_container = QFrame()
        content_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a splitter for provinces/districts and results
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e0e0e0;
            }
        """)
        
        # Left side - Provinces and Districts
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Create scrollable area for provinces
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8f9fa;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        provinces_widget = QWidget()
        provinces_widget.setStyleSheet("background-color: #f8f9fa;")
        provinces_layout = QVBoxLayout(provinces_widget)
        provinces_layout.setContentsMargins(15, 15, 15, 15)
        provinces_layout.setSpacing(15)
        
        # Add provinces and their districts
        self.district_buttons = {}  # Store district buttons for later access
        
        for province in self.provinces:
            # Province header
            province_frame = QFrame()
            province_frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 6px;
                    border: 1px solid #e0e0e0;
                }
            """)
            province_layout = QVBoxLayout(province_frame)
            province_layout.setContentsMargins(15, 15, 15, 15)
            province_layout.setSpacing(10)
            
            province_label = QLabel(province)
            province_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
            province_label.setStyleSheet("color: #2c3e50;")
            province_layout.addWidget(province_label)
            
            # Add separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setStyleSheet("background-color: #e0e0e0;")
            province_layout.addWidget(separator)
            
            # Get districts for this province
            districts = self.get_districts_for_province(province)
            
            if not districts:
                # If no districts, show a message
                no_districts = QLabel("No districts available")
                no_districts.setStyleSheet("color: #95a5a6; font-style: italic;")
                province_layout.addWidget(no_districts)
            else:
                # Add district buttons
                districts_grid = QGridLayout()
                districts_grid.setSpacing(8)
                
                for i, district in enumerate(districts):
                    district_btn = QPushButton(district)
                    district_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f8f9fa;
                            border: 1px solid #e0e0e0;
                            border-radius: 4px;
                            padding: 8px;
                            text-align: left;
                            color: #34495e;
                        }
                        QPushButton:hover {
                            background-color: #edf2f7;
                            border-color: #cbd5e0;
                        }
                        QPushButton:pressed {
                            background-color: #e2e8f0;
                        }
                        QPushButton:checked {
                            background-color: #3498db;
                            color: white;
                            border-color: #2980b9;
                        }
                    """)
                    district_btn.setCursor(Qt.PointingHandCursor)
                    district_btn.setCheckable(True)
                    
                    # Connect button to show results
                    district_btn.clicked.connect(lambda checked, d=district, b=district_btn: self.handle_district_click(d, b))
                    
                    # Store button reference
                    self.district_buttons[district] = district_btn
                    
                    # Add to grid - 2 columns
                    row = i // 2
                    col = i % 2
                    districts_grid.addWidget(district_btn, row, col)
                
                province_layout.addLayout(districts_grid)
            
            provinces_layout.addWidget(province_frame)
        
        provinces_layout.addStretch()
        provinces_widget.setLayout(provinces_layout)
        scroll.setWidget(provinces_widget)
        
        left_layout.addWidget(scroll)
        
        # Right side - Results display
        right_widget = QWidget()
        right_widget.setStyleSheet("background-color: white;")
        self.results_layout = QVBoxLayout(right_widget)
        self.results_layout.setContentsMargins(20, 20, 20, 20)
        self.results_layout.setSpacing(20)
        
        # Initial message
        self.results_container = QFrame()
        self.results_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
        """)
        results_container_layout = QVBoxLayout(self.results_container)
        results_container_layout.setContentsMargins(20, 20, 20, 20)
        
        self.results_message = QLabel("Select a district to view results")
        self.results_message.setFont(QFont('Segoe UI', 14))
        self.results_message.setStyleSheet("color: #7f8c8d;")
        self.results_message.setAlignment(Qt.AlignCenter)
        
        # Last updated time
        self.last_updated = QLabel("")
        self.last_updated.setStyleSheet("color: #95a5a6; font-size: 11px;")
        self.last_updated.setAlignment(Qt.AlignRight)
        
        # Leaderboard table
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(4)
        self.leaderboard_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.leaderboard_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.leaderboard_table.verticalHeader().setVisible(False)
        self.leaderboard_table.horizontalHeader().setVisible(True)
        self.leaderboard_table.setShowGrid(True)
        self.leaderboard_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e8f4fc;
                color: #2c3e50;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        
        # Set headers
        self.leaderboard_table.setHorizontalHeaderLabels([
            "Candidate Name", "Party", "1st Preference", "Total Votes"
        ])
        
        # Set column widths
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)  # Candidate Name
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)  # Party
        self.leaderboard_table.setColumnWidth(2, 150)  # 1st Preference
        self.leaderboard_table.setColumnWidth(3, 150)  # Total Votes
        
        # Winner declaration (initially hidden)
        self.winner_label = QLabel()
        self.winner_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        self.winner_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                background-color: #e8f8f5;
                padding: 15px;
                border-radius: 5px;
                border: 1px solid #2ecc71;
            }
        """)
        self.winner_label.setAlignment(Qt.AlignCenter)
        self.winner_label.setVisible(False)
        
        # Add to results container layout
        results_container_layout.addWidget(self.results_message)
        results_container_layout.addWidget(self.leaderboard_table)
        results_container_layout.addWidget(self.winner_label)
        results_container_layout.addWidget(self.last_updated)
        
        # Add results container to results layout
        self.results_layout.addWidget(self.results_container)
        
        # Hide table initially
        self.leaderboard_table.setVisible(False)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes (30% left, 70% right)
        splitter.setSizes([300, 700])
        
        # Add splitter to content layout
        content_layout.addWidget(splitter)
        
        # Add containers to main layout
        main_layout.addWidget(header_container)
        main_layout.addWidget(content_container, 1)  # Give it stretch factor
        
        self.setLayout(main_layout)
    
    def get_districts_for_province(self, province):
        """Get districts for a province from the database"""
        districts = execute_query(
            "SELECT DISTINCT district FROM candidates WHERE province = %s ORDER BY district",
            (province,)
        )
        
        if districts:
            return [district[0] for district in districts]
        else:
            # If no districts in database, return empty list
            return []
    
    def handle_district_click(self, district, button):
        """Handle district button click"""
        # Uncheck all other buttons
        for d, btn in self.district_buttons.items():
            if d != district:
                btn.setChecked(False)
        
        # If this button is checked, show results
        if button.isChecked():
            self.current_district = district
            self.show_district_results(district)
        else:
            # If unchecked, hide results
            self.current_district = None
            self.leaderboard_table.setVisible(False)
            self.winner_label.setVisible(False)
            self.results_message.setText("Select a district to view results")
    
    def show_district_results(self, district):
        """Show election results for the selected district"""
        # Update message
        self.results_message.setText(f"Election Results for {district} District")
        self.results_message.setStyleSheet("color: #2c3e50; font-weight: bold;")
        
        # Check if voting is closed
        voting_status = execute_query("SELECT value FROM system_settings WHERE key = 'voting_status'")
        is_closed = False
        
        if voting_status and voting_status[0][0] == 'closed':
            is_closed = True
        
        # Get results data for this district
        results = execute_query(
            """SELECT c.name, c.party,
                SUM(CASE WHEN v.preference = 1 THEN 1 ELSE 0 END) as first_prefs,
                COUNT(v.vote_id) as total_votes
            FROM candidates c
            LEFT JOIN votes v ON c.candidate_id = v.candidate_id
            WHERE c.district = %s
            GROUP BY c.candidate_id, c.name, c.party
            ORDER BY first_prefs DESC, total_votes DESC""",
            (district,)
        )
        
        # Show table and update data
        self.leaderboard_table.setVisible(True)
        
        if results:
            # Set row count
            self.leaderboard_table.setRowCount(len(results))
            
            for row, (name, party, first_prefs, total_votes) in enumerate(results):
                # Set values
                name_item = QTableWidgetItem(name)
                party_item = QTableWidgetItem(party)
                first_prefs_item = QTableWidgetItem(str(first_prefs or 0))
                total_votes_item = QTableWidgetItem(str(total_votes or 0))
                
                # Center align numeric columns
                first_prefs_item.setTextAlignment(Qt.AlignCenter)
                total_votes_item.setTextAlignment(Qt.AlignCenter)
                
                # Highlight winner row if voting is closed
                if is_closed and row == 0:
                    for item in [name_item, party_item, first_prefs_item, total_votes_item]:
                        item.setBackground(QColor("#e8f8f5"))
                        item.setForeground(QColor("#27ae60"))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                
                # Add to table
                self.leaderboard_table.setItem(row, 0, name_item)
                self.leaderboard_table.setItem(row, 1, party_item)
                self.leaderboard_table.setItem(row, 2, first_prefs_item)
                self.leaderboard_table.setItem(row, 3, total_votes_item)
        else:
            # No results
            self.leaderboard_table.setRowCount(0)
        
        # Show winner if voting is closed
        if is_closed and results and len(results) > 0:
            winner_name, winner_party, _, _ = results[0]
            self.winner_label.setText(f"WINNER: {winner_name} ({winner_party})")
            self.winner_label.setVisible(True)
        else:
            self.winner_label.setVisible(False)
        
        # Update last updated time
        from datetime import datetime
        current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        self.last_updated.setText(f"Last updated: {current_time}")
    
    def refresh_current_results(self):
        """Refresh the currently displayed results"""
        if self.current_district:
            self.show_district_results(self.current_district)
        
        

