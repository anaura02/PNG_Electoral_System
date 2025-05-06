from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QFileDialog, QMessageBox,
    QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
from database.db_connection import execute_query, log_audit
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime

class ReportsTab(QWidget):
    def __init__(self, user_data):
        super().__init__()
        
        # If user_data is a dictionary, extract the ID
        if isinstance(user_data, dict):
            self.user_data = user_data
            self.user_id = user_data['user_id']
        else:
            self.user_id = user_data
            self.user_data = {'user_id': user_data}
        
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header section
        header_container = QFrame()
        header_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Reports Generation")
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        # Instructions
        instructions = QLabel(
            "Generate various reports in PDF format. Select a report type below."
        )
        instructions.setFont(QFont('Segoe UI', 10))
        instructions.setStyleSheet("color: #7f8c8d;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(instructions)
        
        # Reports section
        reports_container = QFrame()
        reports_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        reports_layout = QVBoxLayout(reports_container)
        reports_layout.setContentsMargins(20, 20, 20, 20)
        reports_layout.setSpacing(20)
        
        # User Information Report
        user_report_frame = self.create_report_card(
            "User Information Report",
            "Generate a comprehensive list of all users in the system with their details.",
            "user_report"
        )
        
        # Election Results Report
        results_report_frame = self.create_report_card(
            "Collated Results Report",
            "Generate a report of election results across all districts.",
            "results_report"
        )
        
        # Audit Trail Report
        audit_report_frame = self.create_report_card(
            "Audit Trail Report",
            "Generate a report of all system activities and user actions.",
            "audit_report"
        )
        
        # Add report cards to layout
        reports_layout.addWidget(user_report_frame)
        reports_layout.addWidget(results_report_frame)
        reports_layout.addWidget(audit_report_frame)
        reports_layout.addStretch()
        
        # Progress bar (initially hidden)
        self.progress_container = QFrame()
        self.progress_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        self.progress_container.setVisible(False)
        
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        
        self.progress_label = QLabel("Generating report...")
        self.progress_label.setFont(QFont('Segoe UI', 12))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        # Add containers to main layout
        main_layout.addWidget(header_container)
        main_layout.addWidget(reports_container, 1)
        main_layout.addWidget(self.progress_container)
        
        self.setLayout(main_layout)
    
    def create_report_card(self, title, description, report_type):
        """Create a card for a report type"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
            QFrame:hover {
                background-color: #edf2f7;
                border-color: #cbd5e0;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side - text
        text_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont('Segoe UI', 10))
        desc_label.setStyleSheet("color: #7f8c8d;")
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        # Right side - button
        generate_btn = QPushButton("Generate PDF")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a6ca8;
            }
        """)
        generate_btn.setCursor(Qt.PointingHandCursor)
        
        # Connect button to appropriate function
        if report_type == "user_report":
            generate_btn.clicked.connect(self.generate_user_report)
        elif report_type == "results_report":
            generate_btn.clicked.connect(self.generate_results_report)
        elif report_type == "audit_report":
            generate_btn.clicked.connect(self.generate_audit_report)
        
        # Add to layout
        layout.addLayout(text_layout, 1)
        layout.addWidget(generate_btn, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        return frame
    
    def show_progress(self, message="Generating report..."):
        """Show progress bar with message"""
        self.progress_container.setVisible(True)
        self.progress_label.setText(message)
        self.progress_bar.setValue(0)
        
        # Simulate progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)
    
    def update_progress(self):
        """Update progress bar value"""
        current = self.progress_bar.value()
        if current < 100:
            self.progress_bar.setValue(current + 5)
        else:
            self.timer.stop()
            self.progress_container.setVisible(False)
    
    def get_save_path(self, default_filename):
        """Get file path to save PDF"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report", default_filename, 
            "PDF Files (*.pdf)", options=options
        )
        return file_path
    
    def generate_user_report(self):
        """Generate PDF report of all users"""
        # Get save location
        default_filename = f"user_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = self.get_save_path(default_filename)
        
        if not file_path:
            return  # User cancelled
        
        # Show progress
        self.show_progress("Generating User Information Report...")
        
        try:
            # Get user data
            users = execute_query(
                """SELECT user_id, username, full_name, province, district, 
                   is_admin, last_login FROM users ORDER BY user_id"""
            )
            
            if not users:
                QMessageBox.warning(self, "No Data", "No user data available to generate report.")
                self.progress_container.setVisible(False)
                return
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'TitleStyle', 
                parent=styles['Heading1'],
                fontSize=18,
                alignment=1  # Center alignment
            )
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray,
                alignment=1  # Center alignment
            )
            
            # Content elements
            elements = []
            
            # Title
            elements.append(Paragraph("User Information Report", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Subtitle with date
            current_date = datetime.now().strftime("%d %B %Y, %H:%M:%S")
            elements.append(Paragraph(f"Generated on {current_date}", subtitle_style))
            elements.append(Spacer(1, 0.5*inch))
            
            # Table data
            data = [["ID", "Username", "Full Name", "Province", "District", "Admin", "Last Login"]]
            
            for user in users:
                user_id, username, full_name, province, district, is_admin, last_login = user
                
                # Format data
                admin_status = "Yes" if is_admin else "No"
                login_time = last_login.strftime("%d-%m-%Y %H:%M:%S") if last_login else "Never"
                
                data.append([
                    str(user_id), username, full_name or "", 
                    province or "", district or "", 
                    admin_status, login_time
                ])
            
            # Create table
            table = Table(data, repeatRows=1)
            
            # Style the table
            table.setStyle(TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Cell style
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                
                # Grid style
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            # Log the action
            log_audit(
                self.user_id, 
                "Generated Report", 
                f"User information report generated and saved to {os.path.basename(file_path)}"
            )
            
            # Show success message
            QMessageBox.information(
                self, "Report Generated", 
                f"User information report has been generated and saved to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
        
        finally:
            self.progress_container.setVisible(False)
    
    def generate_results_report(self):
        """Generate PDF report of election results"""
        # Get save location
        default_filename = f"election_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = self.get_save_path(default_filename)
        
        if not file_path:
            return  # User cancelled
        
        # Show progress
        self.show_progress("Generating Collated Results Report...")
        
        try:
            # Check if voting is closed
            voting_status = execute_query("SELECT value FROM system_settings WHERE key = 'voting_status'")
            is_closed = False
            
            if voting_status and voting_status[0][0] == 'closed':
                is_closed = True
            
            # Get all provinces and districts
            provinces = execute_query(
                "SELECT DISTINCT province FROM candidates ORDER BY province"
            )
            
            if not provinces:
                QMessageBox.warning(self, "No Data", "No election data available to generate report.")
                self.progress_container.setVisible(False)
                return
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
                        # Create custom styles
            title_style = ParagraphStyle(
                'TitleStyle', 
                parent=styles['Heading1'],
                fontSize=18,
                alignment=1  # Center
            )
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray,
                alignment=1  # Center alignment
            )
            
            heading_style = ParagraphStyle(
                'HeadingStyle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            
            subheading_style = ParagraphStyle(
                'SubheadingStyle',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.darkblue,
                spaceAfter=6
            )
            
            # Content elements
            elements = []
            
            # Title
            elements.append(Paragraph("Election Results Report", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Subtitle with date
            current_date = datetime.now().strftime("%d %B %Y, %H:%M:%S")
            elements.append(Paragraph(f"Generated on {current_date}", subtitle_style))
            
            if not is_closed:
                elements.append(Spacer(1, 0.25*inch))
                elements.append(Paragraph("NOTE: Voting is still open. Results are preliminary.", 
                                         ParagraphStyle('Note', parent=styles['Normal'], 
                                                       textColor=colors.red, alignment=1)))
            
            elements.append(Spacer(1, 0.5*inch))
            
            # Process each province
            for province_row in provinces:
                province = province_row[0]
                
                # Add province heading
                elements.append(Paragraph(f"Province: {province}", heading_style))
                
                # Get districts for this province
                districts = execute_query(
                    "SELECT DISTINCT district FROM candidates WHERE province = %s ORDER BY district",
                    (province,)
                )
                
                # Process each district
                for district_row in districts:
                    district = district_row[0]
                    
                    # Add district subheading
                    elements.append(Paragraph(f"District: {district}", subheading_style))
                    
                    # Get results for this district
                    results = execute_query(
                        """SELECT c.name, c.party,
                            SUM(CASE WHEN v.preference = 1 THEN 1 ELSE 0 END) as first_prefs,
                            COUNT(v.vote_id) as total_votes
                        FROM candidates c
                        LEFT JOIN votes v ON c.candidate_id = v.candidate_id
                        WHERE c.district = %s
                        GROUP BY c.candidate_id, c.name, c.party
                        ORDER BY first_prefs DESC, total_votes DESC""",
                        (district,)
                    )
                    
                    if results:
                        # Table data
                        data = [["Candidate Name", "Party", "1st Preference", "Total Votes"]]
                        
                        for row, (name, party, first_prefs, total_votes) in enumerate(results):
                            data.append([
                                name, 
                                party, 
                                str(first_prefs or 0), 
                                str(total_votes or 0)
                            ])
                        
                        # Create table
                        table = Table(data, repeatRows=1)
                        
                        # Style the table
                        table_style = [
                            # Header style
                            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            
                            # Cell style
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                            
                            # Grid style
                            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ]
                        
                        # Highlight winner if voting is closed
                        if is_closed and len(results) > 0:
                            table_style.extend([
                                ('BACKGROUND', (0, 1), (-1, 1), colors.palegreen),
                                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                            ])
                        
                        table.setStyle(TableStyle(table_style))
                        
                        elements.append(table)
                        
                        # Add winner note if voting is closed
                        if is_closed and len(results) > 0:
                            winner_name, winner_party, _, _ = results[0]
                            elements.append(Spacer(1, 0.1*inch))
                            elements.append(Paragraph(
                                f"Winner: {winner_name} ({winner_party})",
                                ParagraphStyle('Winner', parent=styles['Normal'], 
                                              textColor=colors.darkgreen, fontName='Helvetica-Bold')
                            ))
                    else:
                        elements.append(Paragraph("No results available for this district.", 
                                                 styles['Italic']))
                    
                    elements.append(Spacer(1, 0.3*inch))
                
                elements.append(Spacer(1, 0.2*inch))
                elements.append(Paragraph("_" * 65, styles['Normal']))  # Separator
                elements.append(Spacer(1, 0.2*inch))
            
            # Build PDF
            doc.build(elements)
            
            # Log the action
            log_audit(
                self.user_id, 
                "Generated Report", 
                f"Election results report generated and saved to {os.path.basename(file_path)}"
            )
            
            # Show success message
            QMessageBox.information(
                self, "Report Generated", 
                f"Election results report has been generated and saved to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
        
        finally:
            self.progress_container.setVisible(False)
    
    def generate_audit_report(self):
        """Generate PDF report of audit trail"""
        # Get save location
        default_filename = f"audit_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = self.get_save_path(default_filename)
        
        if not file_path:
            return  # User cancelled
        
        # Show progress
        self.show_progress("Generating Audit Trail Report...")
        
        try:
            # Get audit data
            audit_logs = execute_query(
                """SELECT a.log_id, u.username, a.action, a.details, a.timestamp 
                   FROM audit_logs a
                   LEFT JOIN users u ON a.user_id = u.user_id
                   ORDER BY a.timestamp DESC"""
            )
            
            if not audit_logs:
                QMessageBox.warning(self, "No Data", "No audit data available to generate report.")
                self.progress_container.setVisible(False)
                return
            
            # Create PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=0.5*inch, rightMargin=0.5*inch)
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'TitleStyle', 
                parent=styles['Heading1'],
                fontSize=18,
                alignment=1  # Center
            )
            
            subtitle_style = ParagraphStyle(
                'SubtitleStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray,
                alignment=1  # Center alignment
            )
            
            # Content elements
            elements = []
            
            # Title
            elements.append(Paragraph("Audit Trail Report", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Subtitle with date
            current_date = datetime.now().strftime("%d %B %Y, %H:%M:%S")
            elements.append(Paragraph(f"Generated on {current_date}", subtitle_style))
            elements.append(Spacer(1, 0.5*inch))
            
            # Table data
            data = [["ID", "User", "Action", "Details", "Timestamp"]]
            
            for log in audit_logs:
                log_id, username, action, details, timestamp = log
                
                # Format timestamp
                formatted_time = timestamp.strftime("%d-%m-%Y %H:%M:%S")
                
                # Truncate long details
                if details and len(details) > 50:
                    details = details[:47] + "..."
                
                data.append([
                    str(log_id), 
                    username or "System", 
                    action or "", 
                    details or "", 
                    formatted_time
                ])
            
            # Create table
            table = Table(data, repeatRows=1)
            
            # Style the table
            table.setStyle(TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                
                # Cell style
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),  # Smaller font for audit data
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                
                # Grid style
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Column widths
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]))
            
            # Set column widths
            col_widths = [0.5*inch, 1*inch, 1*inch, 3*inch, 1.5*inch]
            table._argW = col_widths
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            # Log the action
            log_audit(
                self.user_id, 
                "Generated Report", 
                f"Audit trail report generated and saved to {os.path.basename(file_path)}"
            )
            
            # Show success message
            QMessageBox.information(
                self, "Report Generated", 
                f"Audit trail report has been generated and saved to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
        
        finally:
            self.progress_container.setVisible(False)
