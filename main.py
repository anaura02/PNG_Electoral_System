import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from database.db_connection import initialize_database, initialize_system_settings
from psycopg2.extras import Json


def main():
    initialize_database()
    initialize_system_settings()
    app = QApplication(sys.argv)
    
    # Set dark theme (optional)
    app.setStyle("Fusion")
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()