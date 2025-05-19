import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QComboBox, QInputDialog, QHeaderView
)

# --- Main Admin Viewer (Limited to Basic Info) ---
class AdminViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin User Info Viewer")
        self.resize(11000, 700)  # Make window larger and resizable

        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        refresh_btn = QPushButton("Refresh User Info")
        refresh_btn.clicked.connect(self.load_user_data)
        self.layout.addWidget(refresh_btn)

        self.load_user_data()

    def db_connect(self):
        return mysql.connector.connect(
            host="localhost", user="adminuser", password="adminpass", database="locker_system"
        )

    def load_user_data(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            # Fetch basic user info only
            cursor.execute("""
                SELECT 
                    u.username, 
                    u.name, 
                    u.birthday, 
                    TIMESTAMPDIFF(YEAR, u.birthday, CURDATE()) AS age,
                    l.locker_id
                FROM users u
                LEFT JOIN lockers l ON u.user_id = l.user_id
            """)
            rows = cursor.fetchall()
            headers = ["Username", "Name", "Birthday", "Age", "Locker Used"]

            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)
            self.table.setRowCount(len(rows))

            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem(str(val)))

            cursor.close()
            conn.close()

        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", str(e))

