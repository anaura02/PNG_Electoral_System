from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QApplication, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor
from database.db_connection import execute_query
from ui.dashboard import DashboardWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        self.setWindowTitle("PNG Electoral System - Login")
        self.setMinimumSize(500, 400)  # Set minimum size but allows resizing
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Title
        title = QLabel("Login into your account")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 30px;")
        
        # Form Container
        form_container = QWidget()
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Username Field
        username_container = QVBoxLayout()
        username_label = QLabel("Username")
        username_label.setFont(QFont('Segoe UI', 12))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(45)
        username_container.addWidget(username_label)
        username_container.addWidget(self.username_input)
        
        # Password Field
        password_container = QVBoxLayout()
        password_label = QLabel("Password")
        password_label.setFont(QFont('Segoe UI', 12))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(45)
        password_container.addWidget(password_label)
        password_container.addWidget(self.password_input)
        
        # Add fields to form
        form_layout.addLayout(username_container)
        form_layout.addLayout(password_container)
        form_container.setLayout(form_layout)
        
        # Login Button
        login_btn = QPushButton("LOG IN")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setMinimumHeight(45)
        
        # Forgot Password (placeholder)
        forgot_pw = QLabel("<a href='#' style='color: #3498db; text-decoration: none;'>Can't access my account?</a>")
        forgot_pw.setFont(QFont('Segoe UI', 10))
        forgot_pw.setAlignment(Qt.AlignCenter)
        forgot_pw.setOpenExternalLinks(False)
        
        # Add widgets to main layout
        main_layout.addWidget(title)
        main_layout.addWidget(form_container)
        main_layout.addWidget(login_btn)
        main_layout.addWidget(forgot_pw)
        
        # Connect signals
        login_btn.clicked.connect(self.handle_login)
        
        self.setLayout(main_layout)
    
    def setup_styles(self):
        # Modern color palette
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))
        palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # Global styles
        self.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #3498db;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a6ca8;
            }
        """)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter both username and password")
            return
        
        # Check for default admin credentials
        if username == "admin" and password == "admin123":
            # Open account creation as a new user
            self.open_account_creation(is_new_user=True)
            return
        
        # Otherwise, check database for user credentials
        user = execute_query(
            "SELECT user_id, password, is_admin FROM users WHERE username = %s",
            (username,)
        )
        
        if user:
            user_id, db_password, is_admin = user[0]
            
            # Check if using default password (admin123)
            if password == "admin123" and db_password == "admin123":
                QMessageBox.information(self, "Password Change", 
                    "Please set a new password")
                self.open_password_change(user_id)
            elif password == db_password:
                if is_admin:
                    self.open_admin_dashboard(user_id)
                else:
                    self.open_dashboard(user_id)
            else:
                QMessageBox.warning(self, "Error", "Incorrect password")
        else:
            QMessageBox.warning(self, "Error", "Username not found")


    def open_account_creation(self, is_new_user=False):
        from ui.account_creation import AccountCreationDialog
        self.account_dialog = AccountCreationDialog(is_new_user=is_new_user)
        self.account_dialog.exec_()
        
    def open_admin_dashboard(self, user_id):
        from ui.admin_dashboard import AdminDashboardWindow
        self.admin_dashboard = AdminDashboardWindow(user_id)
        self.admin_dashboard.show()
        self.close()

    def open_dashboard(self, user_id):        
        user_data = execute_query(
        "SELECT full_name, province, district FROM users WHERE user_id = %s",
        (user_id,)
        )[0]
    
        dashboard_data = {
            'user_id': user_id,  # THIS WAS MISSING - CAUSED THE ERROR
            'full_name': user_data[0],
            'province': user_data[1],
            'district': user_data[2]
        }
        
        from ui.dashboard import DashboardWindow
        self.dashboard = DashboardWindow(dashboard_data)
        self.dashboard.show()
        self.close()