import sys
import time
from datetime import date
import random
import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QFormLayout,
    QDateEdit, QInputDialog
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from gpiozero import OutputDevice, Buzzer

# single age‑calculator used by both forms
def calculate_age(qdate):
    today = date.today()
    return today.year - qdate.year() - ((today.month, today.day) < (qdate.month(), qdate.day()))

# theme colors
BG_COLOR = "#F4F4F4"
TEXT_COLOR = "#333333"
BORDER_COLOR = "#CCCCCC"
ACCENT_COLOR = "#4CAF50"
ACCENT_HOVER = "#45A049"
WIDGET_FONT = "Segoe UI"

class LockerSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Shapers' Smart Lock System")
        self.setFixedSize(1000, 700)
        self.setStyleSheet(f"""
            QWidget {{ background-color: {BG_COLOR}; font-family: {WIDGET_FONT}; }}
            QLabel {{ color: {TEXT_COLOR}; }}
            QLineEdit {{ background-color: white; border:1px solid {BORDER_COLOR}; border-radius:8px; padding:12px; }}
            QPushButton {{ background-color: {ACCENT_COLOR}; color:white; border:none; border-radius:8px; padding:12px 24px; }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        """)

        # Title
        title = QLabel("System Shapers' Smart Lock System", alignment=Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Segoe UI", 18))
        self.username_input.setStyleSheet("padding: 12px;")

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Segoe UI", 18))
        self.password_input.setStyleSheet("padding: 12px;")

        # Buttons
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Segoe UI", 18))
        login_btn.setStyleSheet("padding: 12px 24px;")
        login_btn.clicked.connect(self.login)

        reg_btn = QPushButton("Register")
        reg_btn.setFont(QFont("Segoe UI", 18))
        reg_btn.setStyleSheet("padding: 12px 24px;")
        reg_btn.clicked.connect(self.register_user)

        fp_btn = QPushButton("Forgot Password")
        fp_btn.setFont(QFont("Segoe UI", 18))
        fp_btn.setStyleSheet("padding: 12px 24px;")
        fp_btn.clicked.connect(self.forgot_password)

        # Layouts
        form = QVBoxLayout()
        form.setSpacing(20)
        form.addWidget(self.username_input)
        form.addWidget(self.password_input)
        form.addWidget(login_btn)

        lower = QHBoxLayout()
        lower.setSpacing(20)
        lower.addWidget(reg_btn)
        lower.addWidget(fp_btn)

        main = QVBoxLayout()
        main.setContentsMargins(80, 80, 80, 80)
        main.setSpacing(30)
        main.addWidget(title)
        main.addLayout(form)
        main.addLayout(lower)

        self.setLayout(main)

    def login(self):
        u, p = self.username_input.text(), self.password_input.text()
        try:
            conn = mysql.connector.connect(
                host="localhost", user="adminuser", password="adminpass", database="locker_system"
            )
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (u, p))
            if c.fetchone():
                QMessageBox.information(self, "Login", "Welcome " + u + "!")
                self.hide()
                self.lw = LockerStatusWindow(u, self)
                self.lw.show()
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid credentials.")
            c.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def register_user(self):
        RegisterWindow().exec()

    def forgot_password(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Input Required", "Please enter your username before proceeding.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="adminuser",
                password="adminpass",
                database="locker_system"
            )
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=%s", (username,))
            result = c.fetchone()
            c.close()
            conn.close()

            if result:
                ForgotWindow(username, self).exec()  # ✅ Correct usage
            else:
                QMessageBox.warning(self, "User Not Found", "The username you entered does not exist.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register New User")
        self.setFixedSize(1000, 700)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_COLOR}; font-family: {WIDGET_FONT}; }}
            QLabel {{ color: {TEXT_COLOR}; font-size:16px; }}
            QLineEdit, QDateEdit {{ background-color:white; border:1px solid {BORDER_COLOR}; border-radius:8px; padding:8px; }}
            QPushButton {{ background-color: {ACCENT_COLOR}; color:white; border:none; border-radius:8px; padding:8px 16px; }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
            QPushButton:disabled {{ background-color:#95a5a6; }}
        """)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(15)

        self.un = QLineEdit()
        form.addRow("Username:", self.un)
        self.un.editingFinished.connect(self.check_username_availability)

        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.pw)

        self.nm = QLineEdit()
        form.addRow("Name:", self.nm)

        self.bd = QDateEdit(calendarPopup=True)
        self.bd.setDisplayFormat("MM/dd/yyyy")
        self.bd.setDate(date.today())
        form.addRow("Birthday:", self.bd)

        self.age_lbl = QLabel()
        form.addRow("Age:", self.age_lbl)
        self.bd.dateChanged.connect(self.on_bd_change)
        self.on_bd_change(self.bd.date())

        self.btn = QPushButton("Register")
        self.btn.clicked.connect(self.save)
        form.addRow("", self.btn)

        self.setLayout(form)

    def on_bd_change(self, d):
        age = calculate_age(d)
        self.age_lbl.setText(str(age) if age >= 0 else "")

    def check_username_availability(self):
        username = self.un.text().strip()
        if not username:
            return
        try:
            conn = mysql.connector.connect(
                host="localhost", user="adminuser", password="adminpass", database="locker_system"
            )
            c = conn.cursor()
            c.execute("SELECT 1 FROM users WHERE username=%s", (username,))
            if c.fetchone():
                QMessageBox.warning(self, "Username Taken", f"The username '{username}' is already in use.")
                self.un.clear()
                self.un.setFocus()
            c.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def save(self):
        username = self.un.text().strip()
        password = self.pw.text().strip()
        name = self.nm.text().strip()
        birthday = self.bd.date().toString("yyyy-MM-dd")
        age = calculate_age(self.bd.date())

        if not username or not password or not name:
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost", user="adminuser", password="adminpass", database="locker_system"
            )
            c = conn.cursor()

            # Check duplicate username
            c.execute("SELECT 1 FROM users WHERE username=%s", (username,))
            if c.fetchone():
                QMessageBox.warning(self, "Duplicate Username", "This username is already taken.")
                c.close()
                conn.close()
                return

            # Check duplicate name + birthday
            c.execute("SELECT 1 FROM users WHERE name=%s AND birthday=%s", (name, birthday))
            if c.fetchone():
                QMessageBox.warning(self, "Duplicate User", "A user with the same name and birthday already exists.")
                c.close()
                conn.close()
                return

            # Insert new user
            c.execute(
                "INSERT INTO users(username, password, name, age, birthday, role) VALUES (%s, %s, %s, %s, %s, 'user')",
                (username, password, name, age, birthday)
            )
            conn.commit()
            c.close()
            conn.close()

            QMessageBox.information(self, "Success", "Registered successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))


class ForgotWindow(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Forgot Password")
        self.setFixedSize(1000, 700)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {BG_COLOR}; font-family: {WIDGET_FONT}; }}
            QLabel {{ color: {TEXT_COLOR}; font-size: 16px; }}
            QLineEdit, QDateEdit {{
                background-color: white;
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 8px;
            }}
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
        """)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignCenter)
        form.setHorizontalSpacing(20)
        form.setVerticalSpacing(15)

        self.fn = QLineEdit()
        form.addRow("Full Name:", self.fn)

        self.bd2 = QDateEdit(calendarPopup=True)
        self.bd2.setDisplayFormat("MM/dd/yyyy")
        self.bd2.setDate(date.today())
        form.addRow("Birthday:", self.bd2)

        self.age2 = QLabel()
        form.addRow("Age:", self.age2)
        self.bd2.dateChanged.connect(self.on_bd2)
        self.on_bd2(self.bd2.date())

        vbtn = QPushButton("Verify")
        vbtn.clicked.connect(self.verify)
        form.addRow("", vbtn)

        self.otp = QLineEdit()
        self.otp.setPlaceholderText("OTP")
        form.addRow("OTP:", self.otp)

        self.np = QLineEdit()
        self.np.setPlaceholderText("New Password")
        self.np.setEchoMode(QLineEdit.Password)
        form.addRow("New Pass:", self.np)

        self.rt = QPushButton("Reset")
        self.rt.clicked.connect(self.reset)
        form.addRow("", self.rt)

        for w in (self.otp, self.np, self.rt):
            w.setEnabled(False)

        self.setLayout(form)

    def on_bd2(self, d):
        self.age2.setText(str(calculate_age(d)))

    def verify(self):
        fn = self.fn.text()
        bd = self.bd2.date().toString("yyyy-MM-dd")
        ag = self.age2.text()

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="adminuser",
                password="adminpass",
                database="locker_system"
            )
            c = conn.cursor()
            c.execute("SELECT user_id FROM users WHERE username=%s AND name=%s AND birthday=%s AND age=%s", (self.username, fn, bd, ag))
            r = c.fetchone()
            if r:
                self.uid = r[0]
                otp = str(random.randint(100000, 999999))
                c.execute("UPDATE users SET otp=%s WHERE user_id=%s", (otp, self.uid))
                conn.commit()
                QMessageBox.information(self, "OTP Sent", f"Your OTP: {otp}")
                for w in (self.otp, self.np, self.rt):
                    w.setEnabled(True)
            else:
                QMessageBox.warning(self, "Verify Failed", "Info mismatch.")
            c.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def reset(self):
        ent = self.otp.text()
        newp = self.np.text().strip()
        if not newp:
            QMessageBox.warning(self, "Invalid Password", "Password cannot be blank or only spaces.")
            return

        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="adminuser",
                password="adminpass",
                database="locker_system"
            )
            c = conn.cursor()
            c.execute("SELECT otp FROM users WHERE user_id=%s", (self.uid,))
            result = c.fetchone()

            if result and str(result[0]) == ent:
                c.execute("UPDATE users SET password=%s, otp=0 WHERE user_id=%s", (newp, self.uid))
                conn.commit()
                QMessageBox.information(self, "Success", "Password reset successfully.")
                self.accept()
            else:
                QMessageBox.warning(self, "OTP Failed", "Incorrect OTP.")
            c.close()
            conn.close()
        except Exception as e:
            QMessageB

class LockerStatusWindow(QWidget):
    def __init__(self, logged_in_user, login_window):
        super().__init__()
        self.setWindowTitle("Locker Status")
        self.setFixedSize(1000, 700)
        self.logged_in_user = logged_in_user
        self.login_window = login_window

        # Solenoid locks and buzzer setup (gpiozero)
        self.solenoid_lock_1 = OutputDevice(17, active_high=False, initial_value=False)
        self.solenoid_lock_2 = OutputDevice(27, active_high=False, initial_value=False)
        self.buzzer = Buzzer(22)

        # UI setup
        top = QHBoxLayout()
        lbl = QLabel(f"Welcome, {self.logged_in_user}")
        lbl.setFont(QFont("Segoe UI", 34, QFont.Weight.Bold))
        top.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignLeft)
        back = QPushButton("←")
        back.setFixedSize(40, 40)
        back.clicked.connect(self.go_back)
        top.addWidget(back, alignment=Qt.AlignmentFlag.AlignRight)

        self.title_labels = []
        self.status_labels = []
        self.boxes = []

        lockers = QHBoxLayout()
        lockers.setSpacing(30)

        for i in range(2):
            col = QVBoxLayout()
            col.setSpacing(10)

            title = QLabel(f"Locker {i+1}")
            title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            status = QLabel("Status: Closed")
            status.setFont(QFont("Segoe UI", 16))
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)

            box = QLabel("")
            box.setFixedSize(400, 400)
            box.setStyleSheet("border:2px solid #2c3e50; border-radius:8px;")
            box.mousePressEvent = lambda e, idx=i: self.handle_locker_click(idx)

            col.addWidget(title)
            col.addWidget(status)
            col.addWidget(box, alignment=Qt.AlignmentFlag.AlignCenter)

            lockers.addLayout(col)
            self.title_labels.append(title)
            self.status_labels.append(status)
            self.boxes.append(box)

        main = QVBoxLayout()
        main.setContentsMargins(40, 20, 40, 20)
        main.setSpacing(30)
        main.addLayout(top)
        main.addLayout(lockers)
        self.setLayout(main)

        self.update_lockers()

    def beep_opening(self):
        for _ in range(2):
            self.buzzer.on()
            time.sleep(0.2)
            self.buzzer.off()
            time.sleep(0.1)

    def beep_closing(self):
        self.buzzer.on()
        time.sleep(0.5)
        self.buzzer.off()

    def go_back(self):
        self.solenoid_lock_1.off()
        self.solenoid_lock_2.off()
        self.buzzer.off()        # Turn off buzzer
        self.solenoid_lock_1.close()
        self.solenoid_lock_2.close()
        self.buzzer.close()      # Properly release buzzer pin

        reply = QMessageBox.question(self, "Logout", "Do you want to log out?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.login_window.username_input.clear()
            self.login_window.password_input.clear()
            self.close()
            self.login_window.show()

    def update_lockers(self):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="adminuser",
                password="adminpass", database="locker_system"
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT lockers.locker_id, users.username, lockers.object_in_locker
                FROM lockers
                LEFT JOIN users ON lockers.user_id=users.user_id
            """)
            rows = cursor.fetchall()
            for i in range(2):
                if i < len(rows) and rows[i][1] == self.logged_in_user:
                    self.title_labels[i].setText(f"Locker {i+1} - {self.logged_in_user}")
                else:
                    self.title_labels[i].setText(f"Locker {i+1}")

                occupied = (i < len(rows) and rows[i][1] is not None)
                if occupied:
                    color = "#e74c3c"  # Red for occupied
                    status_text = "Status: Closed"
                else:
                    color = "#2ecc71"  # Green for free
                    status_text = "Status: Open"

                self.boxes[i].setStyleSheet(
                    f"background-color: {color}; border:2px solid #2c3e50; border-radius:8px;"
                )
                self.status_labels[i].setText(status_text)
                self.status_labels[i].setStyleSheet(f"color: {color};")

            cursor.close()
            conn.close()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def handle_locker_click(self, index):
        locker_id = index + 1
        try:
            conn = mysql.connector.connect(
                host="localhost", user="adminuser",
                password="adminpass", database="locker_system"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE username=%s", (self.logged_in_user,))
            user_id = cursor.fetchone()[0]
            cursor.execute("SELECT user_id, object_in_locker FROM lockers WHERE locker_id=%s", (locker_id,))
            assigned, obj = cursor.fetchone()

            if assigned is None:
                text, ok = QInputDialog.getText(self, f"Locker {locker_id}", "Enter object to place:")
                if ok and text:
                    cursor.execute(
                        "UPDATE lockers SET user_id=%s, object_in_locker=%s WHERE locker_id=%s",
                        (user_id, text, locker_id)
                    )
                    conn.commit()

                    if locker_id == 1:
                        self.beep_opening()
                        self.solenoid_lock_1.on()
                        self.status_labels[0].setText("Status: Open")
                        time.sleep(5)
                        self.beep_closing()
                        self.solenoid_lock_1.off()
                        self.status_labels[0].setText("Status: Closed")
                    elif locker_id == 2:
                        self.beep_opening()
                        self.solenoid_lock_2.on()
                        self.status_labels[1].setText("Status: Open")
                        time.sleep(5)
                        self.beep_closing()
                        self.solenoid_lock_2.off()
                        self.status_labels[1].setText("Status: Closed")

            elif assigned == user_id:
                if QMessageBox.question(self, "Claim?", f"Claim '{obj}' from Locker {locker_id}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    cursor.execute(
                        "UPDATE lockers SET user_id=NULL, object_in_locker=NULL WHERE locker_id=%s",
                        (locker_id,)
                    )
                    conn.commit()

                    if locker_id == 1:
                        self.beep_opening()
                        self.solenoid_lock_1.on()
                        self.status_labels[0].setText("Status: Open")
                        time.sleep(5)
                        self.beep_closing()
                        self.solenoid_lock_1.off()
                        self.status_labels[0].setText("Status: Closed")
                    elif locker_id == 2:
                        self.beep_opening()
                        self.solenoid_lock_2.on()
                        self.status_labels[1].setText("Status: Open")
                        time.sleep(5)
                        self.beep_closing()
                        self.solenoid_lock_2.off()
                        self.status_labels[1].setText("Status: Closed")
            else:
                QMessageBox.warning(self, "Denied", "Not your locker.")

            cursor.close()
            conn.close()
            self.update_lockers()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Database Error", str(e))

            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LockerSystem()
    window.show()
    sys.exit(app.exec())


