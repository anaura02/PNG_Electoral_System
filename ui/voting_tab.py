from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QRadioButton, QButtonGroup, QPushButton,
    QScrollArea, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPixmap, QIcon
from database.db_connection import execute_query
import os

class VotingTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data  # Now contains user_id
        self.candidates = self.get_candidates()
        self.preference_groups = {}
        self.setup_ui()
        
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Title
        title = QLabel(f"Voting - {self.user_data['district']} District")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        # Instructions
        instructions = QLabel(
            "Select your 1st, 2nd, and 3rd preferences for candidates\n"
            "Click on a candidate's image to view more details"
        )
        instructions.setFont(QFont('Segoe UI', 10))
        instructions.setStyleSheet("color: #7f8c8d;")
        
        # Candidates grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        grid_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add candidates to grid (3 per row)
        for i, candidate in enumerate(self.candidates):
            row = i // 3
            col = i % 3
            self.grid_layout.addWidget(self.create_candidate_card(candidate), row, col)
        
        grid_container.setLayout(self.grid_layout)
        scroll.setWidget(grid_container)
        
        # Submit button with connection
        submit_btn = QPushButton("SUBMIT VOTE")
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px;
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.submit_vote)
        
        # Add to main layout
        main_layout.addWidget(title)
        main_layout.addWidget(instructions)
        main_layout.addWidget(scroll)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)
    
    def create_candidate_card(self, candidate):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                border: 1px solid #3498db;
            }
        """)
        card.setFixedSize(300, 380)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Candidate photo - with proper null handling
        photo = QLabel()
        photo.setAlignment(Qt.AlignCenter)
        photo.setFixedSize(150, 150)
        
        if candidate.get('photo'):
            try:
                pixmap = QPixmap()
                pixmap.loadFromData(candidate['photo'])
                if not pixmap.isNull():
                    photo.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.set_default_photo(photo)
            except:
                self.set_default_photo(photo)
        else:
            self.set_default_photo(photo)
        
        # Candidate info
        name = QLabel(candidate['name'])
        name.setFont(QFont('Segoe UI', 12, QFont.Bold))
        name.setStyleSheet("color: #2c3e50;")
        name.setAlignment(Qt.AlignCenter)
        
        party = QLabel(candidate['party'])
        party.setFont(QFont('Segoe UI', 10))
        party.setStyleSheet("color: #7f8c8d;")
        party.setAlignment(Qt.AlignCenter)
        
        # Preferences selection
        pref_group = QButtonGroup()
        pref1 = QRadioButton("1st Preference")
        pref2 = QRadioButton("2nd Preference")
        pref3 = QRadioButton("3rd Preference")
        
        # Store selections in dictionary
        self.preference_groups[candidate['id']] = {
            1: pref1,
            2: pref2,
            3: pref3
        }
        
        # Style radio buttons
        radio_style = """
            QRadioButton {
                spacing: 8px;
                font-size: 12px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """
        for rb in [pref1, pref2, pref3]:
            rb.setStyleSheet(radio_style)
        
        # Add to layout
        layout.addWidget(photo, alignment=Qt.AlignCenter)
        layout.addWidget(name)
        layout.addWidget(party)
        layout.addSpacing(10)
        layout.addWidget(pref1)
        layout.addWidget(pref2)
        layout.addWidget(pref3)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def set_default_photo(self, photo_label):
        """Set default user icon when no photo available"""
        default_icon = QIcon.fromTheme("user")
        if default_icon.isNull():
            photo_label.setText("No Image")
            photo_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        else:
            photo_label.setPixmap(default_icon.pixmap(150, 150))
    
    def submit_vote(self):
        # Validate selections
        selected_preferences = {}
        for candidate_id, prefs in self.preference_groups.items():
            for pref_level, radio_btn in prefs.items():
                if radio_btn.isChecked():
                    if pref_level in selected_preferences:
                        QMessageBox.warning(self, "Invalid Selection",
                            "You can only select one candidate per preference level")
                        return
                    selected_preferences[pref_level] = candidate_id
        
        # Check all preferences are selected
        if len(selected_preferences) < 3:
            QMessageBox.warning(self, "Incomplete Selection",
                "Please select 1st, 2nd, and 3rd preferences for three different candidates")
            return
        
        try:
            # Save to database - using user_id from user_data
            execute_query(
                """INSERT INTO votes 
                (user_id, candidate_id, preference) 
                VALUES (%s, %s, 1), (%s, %s, 2), (%s, %s, 3)""",
                (
                    self.user_data['user_id'],  # Now properly accessed
                    selected_preferences[1],
                    self.user_data['user_id'],
                    selected_preferences[2],
                    self.user_data['user_id'],
                    selected_preferences[3]
                )
            )
            
            # Disable voting after submission
            for prefs in self.preference_groups.values():
                for radio_btn in prefs.values():
                    radio_btn.setEnabled(False)
            
            QMessageBox.information(self, "Vote Submitted",
                "Your vote has been successfully recorded!\n\n"
                f"1st: {self.get_candidate_name(selected_preferences[1])}\n"
                f"2nd: {self.get_candidate_name(selected_preferences[2])}\n"
                f"3rd: {self.get_candidate_name(selected_preferences[3])}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error",
                f"Failed to submit vote: {str(e)}")
            
    def get_candidate_name(self, candidate_id):
        for candidate in self.candidates:
            if candidate['id'] == candidate_id:
                return candidate['name']
        return "Unknown"        
    
    def get_candidates(self):
        candidates = execute_query(
            """SELECT candidate_id, name, party, photo 
            FROM candidates 
            WHERE district = %s""",
            (self.user_data['district'],)
        )
        return [
            {
                'id': c[0],
                'name': c[1],
                'party': c[2],
                'photo': c[3] if len(c) > 3 else None
            }
            for c in candidates
        ]