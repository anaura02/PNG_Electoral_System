from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Reports will be generated here"))
        self.setLayout(layout)