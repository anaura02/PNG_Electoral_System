from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QRadioButton, QButtonGroup, QPushButton,
    QScrollArea, QGridLayout, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor
from database.db_connection import execute_query, create_connection
import os

class VotingTab(QWidget):
    def __init__(self, user_id):
        super().__init__()
        
        # If user_id is a dictionary, extract the ID
        if isinstance(user_id, dict):
            self.user_data = user_id
            self.user_id = user_id['user_id']
        else:
            self.user_id = user_id
            
            # Get user data from database
            user_data = execute_query(
                """SELECT u.full_name, u.province, u.district
                    FROM users u WHERE u.user_id = %s""",
                (self.user_id,)
            )
            
            if user_data and len(user_data) > 0 and len(user_data[0]) >= 3:
                self.user_data = {
                    'name': user_data[0][0],
                    'province': user_data[0][1],
                    'district': user_data[0][2]
                }
            else:
                self.user_data = {
                    'name': 'Unknown',
                    'province': 'Unknown',
                    'district': 'Unknown'
                }
        
        # Initialize choice attributes
        self.first_choice = None
        self.second_choice = None
        self.third_choice = None
        
        # Initialize preference groups dictionary
        self.preference_groups = {}
        
        # Get candidates for this district
        self.candidates = self.get_candidates()
        
        self.setup_ui()
        self.check_voting_status()
        
        # Add timer to refresh leaderboard every 30 seconds
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_leaderboard)
        self.refresh_timer.start(30000)  # 30 seconds
    
    def check_voting_status(self):
        """Check if voting is open or closed"""
        voting_status = execute_query("SELECT value FROM system_settings WHERE key = 'voting_status'")
        
        if voting_status and voting_status[0][0] == 'closed':
            # Voting is closed
            self.disable_voting_controls()
            QMessageBox.information(self, "Voting Closed",
                                "Voting is currently closed. You can view the results but cannot submit votes.")
        
        # Also check if user has already voted
        has_voted = execute_query(
            "SELECT COUNT(*) FROM votes WHERE user_id = %s",
            (self.user_id,)
        )
        
        if has_voted and has_voted[0][0] > 0:
            self.disable_voting_controls()
            QMessageBox.information(self, "Already Voted",
                                "You have already submitted your vote. You can view the results but cannot vote again.")

    def disable_voting_controls(self):
        """Disable all voting controls"""
        # Disable all radio buttons
        for candidate_id in self.preference_groups:
            for pref in self.preference_groups[candidate_id].values():
                pref.setEnabled(False)
        
        # Disable submit button
        self.submit_btn.setEnabled(False)
        self.submit_btn.setToolTip("Voting is not available")
        
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
        
        # Create hidden labels for tracking selections (we'll keep these for internal use)
        self.first_pref_label = QLabel("1st Preference: Not selected")
        self.first_pref_label.setVisible(False)
        self.second_pref_label = QLabel("2nd Preference: Not selected")
        self.second_pref_label.setVisible(False)
        self.third_pref_label = QLabel("3rd Preference: Not selected")
        self.third_pref_label.setVisible(False)
        
        # Submit button - ALWAYS ENABLED
        self.submit_btn = QPushButton("Submit Vote")
        self.submit_btn.setStyleSheet("""
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
        """)
        # Always enable the button
        self.submit_btn.setEnabled(True)
        
        # Connect with direct method reference
        self.submit_btn.clicked.connect(self.submit_vote)
        print("Submit button connected to submit_vote method")  # Debug
        
        # Leaderboard section
        leaderboard_frame = QFrame()
        leaderboard_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                padding: 15px;
            }
        """)
        
        leaderboard_layout = QVBoxLayout()
        
        # Leaderboard title
        leaderboard_title = QLabel("Current Leaderboard")
        leaderboard_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        leaderboard_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Leaderboard table
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setColumnCount(4)
        self.leaderboard_table.setHorizontalHeaderLabels([
            "Candidate", "Party", "First Preference Votes", "Total Points"
        ])
        self.leaderboard_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.leaderboard_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.leaderboard_table.verticalHeader().setVisible(False)
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.leaderboard_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
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
        
        # Add to leaderboard layout
        leaderboard_layout.addWidget(leaderboard_title)
        leaderboard_layout.addWidget(self.leaderboard_table)
        leaderboard_layout.addWidget(self.winner_label)
        leaderboard_frame.setLayout(leaderboard_layout)
        
        # Add to main layout
        main_layout.addWidget(title)
        main_layout.addWidget(instructions)
        main_layout.addWidget(scroll)
        main_layout.addWidget(self.submit_btn, alignment=Qt.AlignCenter)
        main_layout.addWidget(leaderboard_frame)
        self.setLayout(main_layout)
        
        # Initialize leaderboard
        self.update_leaderboard()


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
        pref1 = QRadioButton("1st Preference")
        pref2 = QRadioButton("2nd Preference")
        pref3 = QRadioButton("3rd Preference")
        
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
        
        # Connect each radio button directly
        candidate_id = candidate['id']
        
        # Direct connections for each preference
        pref1.clicked.connect(lambda: self.set_preference(candidate_id, 1))
        pref2.clicked.connect(lambda: self.set_preference(candidate_id, 2))
        pref3.clicked.connect(lambda: self.set_preference(candidate_id, 3))
        
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
    
    def set_preference(self, candidate_id, preference):
        """Set a preference for a candidate"""
        print(f"Setting preference: candidate={candidate_id}, preference={preference}")  # Debug
        
        # Update the appropriate choice attribute based on preference
        if preference == 1:
            self.first_choice = candidate_id
        elif preference == 2:
            self.second_choice = candidate_id
        elif preference == 3:
            self.third_choice = candidate_id
        
        # Debug - print current selections
        print(f"Current selections: 1st={self.first_choice}, 2nd={self.second_choice}, 3rd={self.third_choice}")

       
    
    
    def set_default_photo(self, photo_label):
        """Set default user icon when no photo available"""
        default_icon = QIcon.fromTheme("user")
        if default_icon.isNull():
            photo_label.setText("No Image")
            photo_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        else:
            photo_label.setPixmap(default_icon.pixmap(150, 150))
            
    
    def submit_vote(self):
        """Submit the user's vote"""
        print("Submit vote button clicked")  # Debug message
        
        # Get the selected preferences (could be None)
        selected_candidates = [self.first_choice, self.second_choice, self.third_choice]
        print(f"Selected candidates: {selected_candidates}")
        
        # Filter out None values
        valid_selections = [c for c in selected_candidates if c is not None]
        print(f"Valid selections: {valid_selections}")
        
        # Check if any preferences are selected
        if not valid_selections:
            QMessageBox.warning(self, "No Selection",
                            "Please select at least one preference before submitting.")
            return
        
        # Confirm vote
        preferences_text = ""
        if self.first_choice:
            preferences_text += f"1st Preference: {self.get_candidate_name(self.first_choice)}\n"
        if self.second_choice:
            preferences_text += f"2nd Preference: {self.get_candidate_name(self.second_choice)}\n"
        if self.third_choice:
            preferences_text += f"3rd Preference: {self.get_candidate_name(self.third_choice)}\n"
        
        reply = QMessageBox.question(
            self, 'Confirm Vote',
            f"Are you sure you want to submit your vote with the following preferences?\n\n"
            f"{preferences_text}\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        # Submit vote to database
        from database.db_connection import create_connection
        
        conn = None
        cursor = None
        try:
            print("Attempting to connect to database...")  # Debug
            conn = create_connection()
            if not conn:
                print("Failed to create database connection")  # Debug
                QMessageBox.critical(self, "Error", "Failed to connect to database")
                return
                
            cursor = conn.cursor()
            print("Database connection established")  # Debug
            
            # Check if user has already voted
            cursor.execute(
                "SELECT COUNT(*) FROM votes WHERE user_id = %s",
                (self.user_id,)
            )
            vote_count = cursor.fetchone()[0]
            print(f"User has {vote_count} existing votes")  # Debug
            
            if vote_count > 0:
                QMessageBox.warning(self, "Already Voted",
                                "You have already submitted your vote.")
                return
            
            # Insert votes for each valid preference
            for preference, candidate_id in enumerate([c for c in selected_candidates if c is not None], 1):
                print(f"Inserting vote: user_id={self.user_id}, candidate_id={candidate_id}, preference={preference}")  # Debug
                cursor.execute(
                    "INSERT INTO votes (user_id, candidate_id, preference) VALUES (%s, %s, %s)",
                    (self.user_id, candidate_id, preference)
                )
            
            conn.commit()
            print("Votes committed to database")  # Debug
            QMessageBox.information(self, "Success", "Your vote has been recorded successfully!")
            
            # Disable voting controls
            self.disable_voting_controls()
            
            # Update leaderboard
            self.update_leaderboard()
            
        except Exception as e:
            print(f"Error submitting vote: {e}")  # Debug
            QMessageBox.critical(self, "Error", f"Failed to submit vote: {str(e)}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass           

    
        
    def get_candidate_name(self, candidate_id):
        """Get candidate name from ID"""
        from database.db_connection import execute_query
        
        result = execute_query(
            "SELECT name FROM candidates WHERE candidate_id = %s",
            (candidate_id,)
        )
        
        if result and result[0]:
            return result[0][0]
        return "Unknown Candidate"
    
    def get_candidates(self):
        district = self.user_data.get('district', 'Unknown')
        
        candidates = execute_query(
            """SELECT candidate_id, name, party, photo 
            FROM candidates 
            WHERE district = %s""",
            (district,)
        )
        
        if not candidates:
            return []
            
        return [
            {
                'id': c[0],
                'name': c[1],
                'party': c[2],
                'photo': c[3] if len(c) > 3 else None
            }
            for c in candidates
        ]
        
    def update_leaderboard(self):
        # Check if voting is closed
        voting_status = execute_query("SELECT value FROM system_settings WHERE key = 'voting_status'")
        is_closed = False
        
        if voting_status and voting_status[0][0] == 'closed':
            is_closed = True
        
        # Get leaderboard data for this district
        results = execute_query(
            """SELECT c.name, c.party,
                SUM(CASE WHEN v.preference = 1 THEN 1 ELSE 0 END) as first_prefs,
                SUM(CASE WHEN v.preference = 1 THEN 3
                          WHEN v.preference = 2 THEN 2
                         WHEN v.preference = 3 THEN 1 ELSE 0 END) as total_points
            FROM candidates c
            LEFT JOIN votes v ON c.candidate_id = v.candidate_id
            WHERE c.district = %s
            GROUP BY c.candidate_id, c.name, c.party
            ORDER BY total_points DESC, first_prefs DESC""",
            (self.user_data['district'],)
        )
        
        # Update table
        if results:
            self.leaderboard_table.setRowCount(len(results))
            
            for row, (name, party, first_prefs, total_points) in enumerate(results):
                # Set values
                name_item = QTableWidgetItem(name)
                party_item = QTableWidgetItem(party)
                first_prefs_item = QTableWidgetItem(str(first_prefs or 0))
                total_points_item = QTableWidgetItem(str(total_points or 0))
                
                # Center align
                for item in [name_item, party_item, first_prefs_item, total_points_item]:
                    item.setTextAlignment(Qt.AlignCenter)
                
                # Highlight winner row if voting is closed
                if is_closed and row == 0:
                    for item in [name_item, party_item, first_prefs_item, total_points_item]:
                        item.setBackground(QColor("#e8f8f5"))
                        item.setForeground(QColor("#27ae60"))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                
                # Add to table
                self.leaderboard_table.setItem(row, 0, name_item)
                self.leaderboard_table.setItem(row, 1, party_item)
                self.leaderboard_table.setItem(row, 2, first_prefs_item)
                self.leaderboard_table.setItem(row, 3, total_points_item)
        else:
            self.leaderboard_table.setRowCount(0)
        
        # Show winner if voting is closed
        if is_closed and results and len(results) > 0:
            winner_name, winner_party, _, _ = results[0]
            self.winner_label.setText(f"WINNER: {winner_name} ({winner_party})")
            self.winner_label.setVisible(True)
        else:
            self.winner_label.setVisible(False)
       
    
    def handle_candidate_selection(self, candidate_id, preference):
        """Handle when a candidate is selected for a preference"""
        print(f"Selection made: Candidate {candidate_id} for preference {preference}")  # Debug
        
        # Update the appropriate choice attribute based on preference
        if preference == 1:
            self.first_choice = candidate_id
        elif preference == 2:
            self.second_choice = candidate_id
        elif preference == 3:
            self.third_choice = candidate_id
        
        # Debug - print current selections
        print(f"Current selections: 1st={self.first_choice}, 2nd={self.second_choice}, 3rd={self.third_choice}")

     
    def update_selection_display(self):
        """Update the display to show current selections"""
        # Update first preference display
        if self.first_choice:
            candidate_name = self.get_candidate_name(self.first_choice)
            self.first_pref_label.setText(f"1st Preference: {candidate_name}")
            self.first_pref_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.first_pref_label.setText("1st Preference: Not selected")
            self.first_pref_label.setStyleSheet("color: #7f8c8d;")
        
        # Update second preference display
        if self.second_choice:
            candidate_name = self.get_candidate_name(self.second_choice)
            self.second_pref_label.setText(f"2nd Preference: {candidate_name}")
            self.second_pref_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.second_pref_label.setText("2nd Preference: Not selected")
            self.second_pref_label.setStyleSheet("color: #7f8c8d;")
        
        # Update third preference display
        if self.third_choice:
            candidate_name = self.get_candidate_name(self.third_choice)
            self.third_pref_label.setText(f"3rd Preference: {candidate_name}")
            self.third_pref_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.third_pref_label.setText("3rd Preference: Not selected")
            self.third_pref_label.setStyleSheet("color: #7f8c8d;")
        
        # Enable submit button if all preferences are selected
        if self.first_choice and self.second_choice and self.third_choice:
            print("All preferences selected, enabling submit button")  # Debug
            self.submit_btn.setEnabled(True)
        else:
            print(f"Not all preferences selected: 1st={bool(self.first_choice)}, 2nd={bool(self.second_choice)}, 3rd={bool(self.third_choice)}")  # Debug
            self.submit_btn.setEnabled(False)


                
