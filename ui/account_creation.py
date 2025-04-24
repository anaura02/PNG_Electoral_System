from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFormLayout, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from database.db_connection import execute_query

class AccountCreationDialog(QDialog):
    def __init__(self, is_new_user=False):
        super().__init__()
        self.is_new_user = is_new_user
        self.setup_ui()
        self.setup_styles()
        self.setWindowTitle("Complete Account Setup")
        self.setMinimumSize(550, 500)  # Allows resizing
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(25)
        
        # Title
        title = QLabel("Complete Your Account")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # Subtitle
        subtitle_text = "Please create your new account" if self.is_new_user else "Please update your account details"
        subtitle = QLabel(subtitle_text)
        subtitle.setFont(QFont('Segoe UI', 10))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        
        # Form Container
        form_container = QWidget()
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(20)
        form_layout.setHorizontalSpacing(20)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Personal Info Section
        personal_header = QLabel("Personal Information")
        personal_header.setFont(QFont('Segoe UI', 12, QFont.Bold))
        
        self.fullname_input = self.create_styled_input("Full Name")
        self.province_input = self.create_styled_input("Province")
        self.district_input = self.create_styled_input("District")
        
        # Account Info Section
        account_header = QLabel("Account Credentials")
        account_header.setFont(QFont('Segoe UI', 12, QFont.Bold))
        
        self.username_input = self.create_styled_input("Username")
        self.password_input = self.create_password_input("Password")
        self.confirm_password_input = self.create_password_input("Confirm Password")
        
        # Add to form
        form_layout.addRow(personal_header)
        form_layout.addRow("Full Name:", self.fullname_input)
        form_layout.addRow("Province:", self.province_input)
        form_layout.addRow("District:", self.district_input)
        
        form_layout.addRow(account_header)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Confirm:", self.confirm_password_input)
        
        form_container.setLayout(form_layout)
        
        # Submit Button
        submit_btn = QPushButton("SAVE ACCOUNT")
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.setMinimumHeight(45)
        submit_btn.clicked.connect(self.save_account)
        
        # Add to main layout
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(form_container)
        main_layout.addWidget(submit_btn)
        
        self.setLayout(main_layout)
    
    def create_styled_input(self, placeholder):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setMinimumHeight(40)
        input_field.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 8px 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        return input_field
    
    def create_password_input(self, placeholder):
        input_field = self.create_styled_input(placeholder)
        input_field.setEchoMode(QLineEdit.Password)
        return input_field
    
    def setup_styles(self):
        # Modern color scheme
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a6ca8;
            }
        """)
    
    def save_account(self):
        # Get all field values
        fullname = self.fullname_input.text().strip()
        province = self.province_input.text().strip()
        district = self.district_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # Validation
        error = None
        if not all([fullname, province, district, username, password, confirm_password]):
            error = "All fields are required"
        elif password != confirm_password:
            error = "Passwords do not match"
        elif len(password) < 6:
            error = "Password must be at least 6 characters"
        elif ' ' in username:
            error = "Username cannot contain spaces"
            
        if error:
            QMessageBox.warning(self, "Validation Error", error)
            return
            
        # Check if username exists (for new users)
        if self.is_new_user:
            existing = execute_query(
                "SELECT username FROM users WHERE username = %s",
                (username,)
            )
            if existing:
                QMessageBox.warning(self, "Error", "Username already exists")
                return
        
        try:
            if self.is_new_user:
                # Create brand new user
                execute_query(
                    """INSERT INTO users 
                    (username, password, full_name, province, district)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (username, password, fullname, province, district)
                )
                success_msg = "Account created successfully!"
            else:
                # Update existing user (password reset case)
                execute_query(
                    """UPDATE users SET 
                    password = %s,
                    full_name = %s,
                    province = %s,
                    district = %s
                    WHERE username = %s""",
                    (password, fullname, province, district, username)
                )
                success_msg = "Account updated successfully!"
            
            QMessageBox.information(
                self, 
                "Success", 
                f"{success_msg}\n\nUsername: {username}\nPlease login with your new credentials."
            )
            
            # Return to login page instead of closing
            self.return_to_login()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Database Error", 
                f"Could not save account:\n{str(e)}"
            )
    
    def return_to_login(self):
        """Closes this dialog and reopens the login window"""
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()