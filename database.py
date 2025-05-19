import mysql.connector
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QComboBox, QInputDialog
)

# --- Dialog for Creating a New Table ---
class CreateTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Table")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Table Name:"))
        self.table_name_input = QLineEdit()
        layout.addWidget(self.table_name_input)

        layout.addWidget(QLabel("Column Name:"))
        self.column_name_input = QLineEdit()
        layout.addWidget(self.column_name_input)

        layout.addWidget(QLabel("Data Type:"))
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["VARCHAR(255)", "INT", "INT(10)", "DATE", "TEXT"])
        layout.addWidget(self.data_type_combo)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_table_name(self):
        return self.table_name_input.text().strip()

    def get_column_name(self):
        return self.column_name_input.text().strip()

    def get_data_type(self):
        return self.data_type_combo.currentText()

# --- Dialog for Adding a Column ---
class AddColumnDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Column")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Column Name:"))
        self.column_name_input = QLineEdit()
        layout.addWidget(self.column_name_input)

        layout.addWidget(QLabel("Data Type:"))
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["VARCHAR(255)", "INT", "DATE", "TEXT"])
        layout.addWidget(self.data_type_combo)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_column_name(self):
        return self.column_name_input.text().strip()

    def get_data_type(self):
        return self.data_type_combo.currentText()

# --- Dialog for Deleting a Column ---
class DeleteColumnDialog(QDialog):
    def __init__(self, column_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Column")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select Column to Delete:"))
        self.column_combo = QComboBox()
        self.column_combo.addItems(column_names)
        layout.addWidget(self.column_combo)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_column_to_delete(self):
        return self.column_combo.currentText()

# --- Dialog for Locker Data Input ---
class LockerDataInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Locker Data Input")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("User ID:"))
        self.user_id_input = QLineEdit()
        layout.addWidget(self.user_id_input)

        layout.addWidget(QLabel("Object in Locker:"))
        self.object_input = QLineEdit()
        layout.addWidget(self.object_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_user_id(self):
        return self.user_id_input.text().strip()

    def get_object_in_locker(self):
        return self.object_input.text().strip()

# --- Main Admin Viewer ---
class AdminViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Table Viewer")
        self.setFixedSize(1100, 700)

        self.layout = QVBoxLayout(self)

        self.table_selector = QComboBox()
        self.table_selector.currentIndexChanged.connect(self.load_data_from_selected_table)
        self.layout.addWidget(self.table_selector)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        for name, slot in [
            ("Create New Table", self.show_create_table_dialog),
            ("Add Column", self.show_add_column_dialog),
            ("Delete Column", self.show_delete_column_dialog),
            ("Remove User", self.show_remove_user_dialog),
            ("Refresh Data", self.load_data),
            ("Save Changes", self.save_changes),
            ("Locker Data Input", self.show_locker_data_input_dialog),
        ]:
            btn = QPushButton(name)
            btn.clicked.connect(slot)
            btn_layout.addWidget(btn)
        self.layout.addLayout(btn_layout)

        self.load_data()

    def db_connect(self):
        return mysql.connector.connect(
            host="localhost", user="adminuser", password="adminpass", database="locker_system"
        )

    def load_data(self):
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            self.table_selector.clear()
            for table in tables:
                self.table_selector.addItem(table[0])
            cursor.close()
            conn.close()
            self.load_data_from_selected_table()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_data_from_selected_table(self):
        selected_table = self.table_selector.currentText()
        if not selected_table:
            return
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {selected_table}")
            cols = [c[0] for c in cursor.fetchall()]
            cursor.execute(f"SELECT * FROM {selected_table}")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            self.table.setColumnCount(len(cols))
            self.table.setHorizontalHeaderLabels(cols)
            self.table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    self.table.setItem(r, c, QTableWidgetItem(str(val)))
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_create_table_dialog(self):
        dlg = CreateTableDialog(self)
        if dlg.exec() == QDialog.Accepted:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute(f"CREATE TABLE {dlg.get_table_name()} ({dlg.get_column_name()} {dlg.get_data_type()})")
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", "Table created.")
                self.load_data()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", str(e))

    def show_add_column_dialog(self):
        dlg = AddColumnDialog(self)
        if dlg.exec() == QDialog.Accepted:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute(f"ALTER TABLE {self.table_selector.currentText()} ADD COLUMN {dlg.get_column_name()} {dlg.get_data_type()}")
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", "Column added.")
                self.load_data()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", str(e))

    def show_delete_column_dialog(self):
        selected_table = self.table_selector.currentText()
        if not selected_table:
            return
        try:
            conn = self.db_connect()
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE {selected_table}")
            columns = [c[0] for c in cursor.fetchall()]
            cursor.close()
            conn.close()

            dlg = DeleteColumnDialog(columns, self)
            if dlg.exec() == QDialog.Accepted:
                column_to_delete = dlg.get_column_to_delete()
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute(f"ALTER TABLE {selected_table} DROP COLUMN {column_to_delete}")
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", f"Column {column_to_delete} deleted.")
                self.load_data()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_remove_user_dialog(self):
        user_to_remove, ok = QInputDialog.getText(self, "Remove User", "Enter user ID:")
        if ok and user_to_remove:
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM users WHERE user_id = {user_to_remove}")
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", f"User {user_to_remove} removed.")
                self.load_data()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", str(e))

    def show_locker_data_input_dialog(self):
        dlg = LockerDataInputDialog(self)
        if dlg.exec() == QDialog.Accepted:
            user_id = dlg.get_user_id()
            object_in_locker = dlg.get_object_in_locker()
            try:
                conn = self.db_connect()
                cursor = conn.cursor()
                for locker_id in [1, 2]:
                    cursor.execute(f"UPDATE lockers SET user_id = %s, object_in_locker = %s WHERE locker_id = %s",
                                   (user_id, object_in_locker, locker_id))
                conn.commit()
                cursor.close()
                conn.close()
                QMessageBox.information(self, "Success", "Locker data updated.")
                self.load_data()
            except mysql.connector.Error as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_changes(self):
        selected_table = self.table_selector.currentText()
        if not selected_table:
            return
        
        try:
            conn = self.db_connect()
            cursor = conn.cursor()

            # Handle the users table separately
            if selected_table == 'users':
                for row in range(self.table.rowCount()):
                    user_id = self.table.item(row, 0).text()  # Assuming first column is user_id
                    set_values = []
                    for col in range(1, self.table.columnCount()):  # Start from 1 to skip user_id
                        col_name = self.table.horizontalHeaderItem(col).text()
                        set_values.append(f"{col_name} = '{self.table.item(row, col).text()}'")
                    set_clause = ", ".join(set_values)
                    cursor.execute(f"UPDATE {selected_table} SET {set_clause} WHERE user_id = {user_id}")

            # Handle the lockers table separately
            elif selected_table == 'lockers':
                for row in range(self.table.rowCount()):
                    locker_id = self.table.item(row, 0).text()  # Assuming first column is locker_id
                    set_values = []
                    for col in range(1, self.table.columnCount()):  # Start from 1 to skip locker_id
                        col_name = self.table.horizontalHeaderItem(col).text()
                        set_values.append(f"{col_name} = '{self.table.item(row, col).text()}'")
                    set_clause = ", ".join(set_values)
                    cursor.execute(f"UPDATE {selected_table} SET {set_clause} WHERE locker_id = {locker_id}")

            conn.commit()
            cursor.close()
            conn.close()
            QMessageBox.information(self, "Success", "Changes saved.")
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Error", str(e))

# --- Main Program ---
if __name__ == "__main__":
    app = QApplication([])
    viewer = AdminViewer()
    viewer.show()
    app.exec()


