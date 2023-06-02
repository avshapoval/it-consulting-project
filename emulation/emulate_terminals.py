import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QLabel
from PyQt5.QtCore import Qt
import pymysql

class EmployeeTimeSheet(QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.db_connection = db_connection

        self.setWindowTitle('Employee Time Sheet')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.employee_combo_box = QComboBox(self)
        self.employee_combo_box.addItem('Выберите сотрудника', None)
        self.employee_combo_box.currentIndexChanged.connect(self.update_table)

        self.month_combo_box = QComboBox(self)
        self.month_combo_box.addItem('Выберите месяц', None)
        self.month_combo_box.currentIndexChanged.connect(self.update_table)

        layout.addWidget(QLabel('Сотрудник'))
        layout.addWidget(self.employee_combo_box)
        layout.addWidget(QLabel('Месяц'))
        layout.addWidget(self.month_combo_box)

        self.time_sheet_table = QTableWidget(0, 2)
        self.time_sheet_table.setHorizontalHeaderLabels(['День', 'Отработанные часы'])
        layout.addWidget(self.time_sheet_table)

        self.load_employees_and_months()

    def load_employees_and_months(self):
        cursor = self.db_connection.cursor()
        cursor.execute('SELECT employee_id, last_name, first_name FROM employee')
        for row in cursor.fetchall():
            self.employee_combo_box.addItem(f'{row[1]} {row[2]}', row[0])

        cursor.execute('SELECT DISTINCT EXTRACT(YEAR_MONTH FROM visit_ts) FROM visit')
        for row in cursor.fetchall():
            self.employee_combo_box.addItem(f'{row[0]}')

    def update_table(self):
        self.time_sheet_table.setRowCount(0) 

        employee_id = self.employee_combo_box.currentData()
        month = self.month_combo_box.currentData()

        if employee_id is None or month is None:
            return

        cursor = self.db_connection.cursor()
        cursor.execute('''
            SELECT DAY(visit_ts), HOUR(TIMEDIFF(MAX(visit_ts), MIN(visit_ts)))
            FROM visit 
            JOIN emp_fingerprint ON visit.fingerprint_uuid = emp_fingerprint.fingerprint_uuid 
            WHERE emp_fingerprint.employee_id = %s AND MONTH(visit_ts) = %s
            GROUP BY DAY(visit_ts)
        ''', (employee_id, month))

        for day, hours in cursor.fetchall():
            self.time_sheet_table.insertRow(self.time_sheet_table.rowCount())
            self.time_sheet_table.setItem(self.time_sheet_table.rowCount()-1, 0, QTableWidgetItem(str(day)))
            self.time_sheet_table.setItem(self.time_sheet_table.rowCount()-1, 1, QTableWidgetItem(str(hours)))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    con_params = {...}  # Заполните собственными параметрами подключения.
    db = pymysql.connect(
        host=con_params['HOST'],
        user=con_params['MYSQL_USER'],
        password=con_params['MYSQL_PASSWORD'],
        db=con_params['MYSQL_DATABASE']
    )

    main_window = EmployeeTimeSheet(db)
    main_window.show()

    sys.exit(app.exec_())
