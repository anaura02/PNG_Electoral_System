from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.results_tab import ResultsTab

from ui.voting_tab import VotingTab

class DashboardWindow(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)
            
        # Welcome message
        welcome_label = QLabel(f"Welcome, {self.user_data['full_name']}")
        welcome_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        welcome_label.setStyleSheet("color: #2c3e50;")
            
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background: white;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #ddd;
                padding: 10px 15px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
            QTabBar::tab:!selected {
                background: #f8f8f8;
            }
            QTabBar::tab:!selected:hover {
                background: #ddd;
            }
        """)
            
        # Create a simple home tab
        home_tab = QWidget()
        home_layout = QVBoxLayout(home_tab)
            
        home_title = QLabel("Welcome to PNG Electoral System")
        home_title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        home_title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
            
        home_description = QLabel(
            "This system allows you to participate in the electoral process.\n"
            "Use the Voting tab to cast your vote for candidates in your district."
        )
        home_description.setFont(QFont('Segoe UI', 12))
        home_description.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
            
        home_layout.addWidget(home_title)
        home_layout.addWidget(home_description)
        home_layout.addStretch()
            
        # Add tabs
        self.tab_widget.addTab(home_tab, "Home")
            
        self.voting_tab = VotingTab(self.user_data['user_id'])
        self.tab_widget.addTab(self.voting_tab, "Voting")
        
        # Add Results Tab - NEW CODE
        self.results_tab = ResultsTab(self.user_data)
        self.tab_widget.addTab(self.results_tab, "Results")
            
        # Simple logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 4px;
                max-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
            
        # Add to main layout
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(logout_btn, alignment=Qt.AlignRight)  # Align to right
            
        self.setLayout(main_layout)
            
        # Set window properties
        self.setWindowTitle("PNG Electoral System - Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #f9f9f9;")
    
    def logout(self):
        """Handle logout action"""
        self.close()
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
