from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.voting_tab import VotingTab

class DashboardWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"PNG Electoral System - {self.user_data['district']}")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
        """)
        
        # Main layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar - Modern Style
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignTop)
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        
        # App Title in Sidebar
        app_title = QLabel("PNG Electoral System")
        app_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border-bottom: 1px solid #34495e;
            }
        """)
        app_title.setAlignment(Qt.AlignCenter)
        
        # Sidebar buttons
        btn_style = """
            QPushButton {
                color: white;
                background: transparent;
                text-align: left;
                padding: 12px 25px;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #2980b9;
            }
        """
        
        self.voting_btn = QPushButton("🗳️ Voting")
        self.results_btn = QPushButton("📊 Results")
        self.reports_btn = QPushButton("📄 Reports")
        
        for btn in [self.voting_btn, self.results_btn, self.reports_btn]:
            btn.setStyleSheet(btn_style)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont('Segoe UI', 11))
            sidebar_layout.addWidget(btn)
        
        # User info at bottom
        user_info = QLabel(f"Logged in as:\n{self.user_data['full_name']}")
        user_info.setStyleSheet("""
            QLabel {
                color: #bdc3c7;
                font-size: 12px;
                padding: 15px;
                border-top: 1px solid #34495e;
            }
        """)
        user_info.setAlignment(Qt.AlignCenter)
        
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(user_info)
        sidebar.setLayout(sidebar_layout)
        
        # Content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        self.content_stack = QStackedWidget()
        
        # Add voting tab (others will be placeholders)
        self.voting_tab = VotingTab(self.user_data)
        self.content_stack.addWidget(self.voting_tab)
        
        # Add placeholder tabs
        self.content_stack.addWidget(QLabel("Results will appear here"))
        self.content_stack.addWidget(QLabel("Reports will appear here"))
        
        scroll.setWidget(self.content_stack)
        
        # Connect buttons
        self.voting_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(0))
        self.results_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(1))
        self.reports_btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(2))
        
        # Add to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(scroll)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)