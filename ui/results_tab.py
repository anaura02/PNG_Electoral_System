from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QTableView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from database.db_connection import execute_query

class ResultsTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Election Results")
        title.setFont(QFont('Segoe UI', 14, QFont.Bold))
        
        # Province/District selectors
        selector_layout = QHBoxLayout()
        
        self.province_combo = QComboBox()
        self.province_combo.addItems(self.get_provinces())
        self.province_combo.currentTextChanged.connect(self.update_districts)
        
        self.district_combo = QComboBox()
        self.district_combo.addItems(self.get_districts())
        self.district_combo.currentTextChanged.connect(self.update_results)
        
        selector_layout.addWidget(QLabel("Province:"))
        selector_layout.addWidget(self.province_combo)
        selector_layout.addWidget(QLabel("District:"))
        selector_layout.addWidget(self.district_combo)
        
        # Results Chart
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(300)
        
        # Results Table
        self.results_table = QTableView()
        
        layout.addWidget(title)
        layout.addLayout(selector_layout)
        layout.addWidget(self.chart_view)
        layout.addWidget(self.results_table)
        self.setLayout(layout)
        
        # Initial load
        self.update_results()
    
    def get_provinces(self):
        return [p[0] for p in execute_query(
            "SELECT DISTINCT province FROM candidates"
        )]
    
    def get_districts(self):
        return [d[0] for d in execute_query(
            """SELECT DISTINCT district FROM candidates 
            WHERE province = %s""",
            (self.province_combo.currentText(),)
        )]
    
    def update_districts(self):
        self.district_combo.clear()
        self.district_combo.addItems(self.get_districts())
    
    def update_results(self):
        district = self.district_combo.currentText()
        if not district:
            return
            
        # Get results data
        results = execute_query(
            """SELECT c.name, c.party, 
            SUM(CASE WHEN v.preference = 1 THEN 1 ELSE 0 END) as first_prefs,
            SUM(CASE WHEN v.preference = 2 THEN 1 ELSE 0 END) as second_prefs,
            SUM(CASE WHEN v.preference = 3 THEN 1 ELSE 0 END) as third_prefs
            FROM candidates c
            LEFT JOIN votes v ON c.candidate_id = v.candidate_id
            WHERE c.district = %s
            GROUP BY c.candidate_id
            ORDER BY first_prefs DESC""",
            (district,)
        )
        
        # Update chart
        series = QPieSeries()
        for name, party, first, _, _ in results:
            series.append(f"{name} ({party}) - {first}", first)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(f"First Preference Votes - {district}")
        self.chart_view.setChart(chart)
        
        # TODO: Implement table model for results display