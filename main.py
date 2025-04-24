import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    
    # Set dark theme (optional)
    app.setStyle("Fusion")
    
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()