import pymysql
import pandas as pd
import tkinter as tk
from tkinter import ttk
from pandastable import Table
from os.path import dirname, abspath



host = "****" # Название хоста
user = "****" # Имя пользователя
password = "****" # Пароль
database = "****" # Название базы данных

connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    cursorclass=pymysql.cursors.DictCursor,
    port=3306
)



query = """
SELECT employee.employee_id, employee.first_name, employee.last_name
FROM employee
INNER JOIN emp_fingerprint ON employee.employee_id = emp_fingerprint.employee_id
INNER JOIN visit ON emp_fingerprint.fingerprint_uuid = visit.fingerprint_uuid
WHERE MONTH(visit.visit_ts) = 5
GROUP BY employee.employee_id
"""



with connection.cursor() as cursor:
    cursor.execute(query)
    records = cursor.fetchall()

def open_new_window():
    selected_employee = combo.get().split(', ')
    employee_id = int(selected_employee[0])
    employee_name = selected_employee[1]

    month = russian_months.index(month_var.get()) + 1

    query = f"""
    SELECT DATE(visit_ts) as visit_date, 
           TIME_TO_SEC(TIMEDIFF(MAX(visit_ts), MIN(visit_ts)))/3600 as hours_on_work
    FROM visit 
    INNER JOIN emp_fingerprint ON visit.fingerprint_uuid = emp_fingerprint.fingerprint_uuid
    WHERE MONTH(visit_ts) = {month} AND emp_fingerprint.employee_id = {employee_id}
    GROUP BY DATE(visit_ts)
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        visit_records = cursor.fetchall()

    df = pd.DataFrame(visit_records)

    df.rename(columns={
        'visit_date': 'Дата',
        'hours_on_work': 'Времени на работе'
    }, inplace=True)

    df['Времени на работе'] = df['Времени на работе'].apply(lambda x: f"{int(x)} hours {int((x % 1) * 60)} minutes")

    total_hours = df['Времени на работе'].apply(lambda x: pd.Timedelta(x)).sum()
    print(type(total_hours))
    total_hours_row = pd.DataFrame(
        {'Дата': ['Всего часов'], 'Времени на работе': [str(total_hours.total_seconds() // 3600) + " часов"]})
    df = pd.concat([df, total_hours_row], ignore_index=True)

    new_window = tk.Toplevel(window)
    new_window.geometry("800x900")
    new_window.title('Табель Т13')
    tk.Label(new_window, text=f"Выбранный сотрудник: {employee_name}", font=('Arial', 14)).pack()
    frame = tk.Frame(new_window)
    frame.pack(fill='both', expand=True)
    pt = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    pt.autoResizeColumns()
    pt.show()



window = tk.Tk()
window.title('Табель ГК Альянс: 2C')
window.geometry('500x500')
window.configure(bg='#FFFF7F')


title = tk.Label(window, text="Выберите сотрудника и месяц", font=('Arial', 20), bg='#FFFF7F')
title.pack(pady=30)

employee_dict = {record['employee_id']: f"{record['employee_id']}, {record['first_name']} {record['last_name']}" for record in records}

employee_label = tk.Label(window, text="Выберите сотрудника", font=('Arial', 16), bg='#FFFF7F')
employee_label.pack(pady=20)
combo = ttk.Combobox(window, values=list(employee_dict.values()), font=('Arial', 14))
combo.pack(pady=20)

month_label = tk.Label(window, text="Выберите месяц", font=('Arial', 16), bg='#FFFF7F')
month_label.pack(pady=20)

month_var = tk.StringVar()
russian_months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']


month_combobox = ttk.Combobox(window, values=russian_months, textvariable=month_var, font=('Arial', 14))
month_combobox.pack(pady=20)

button = tk.Button(window, text="Сделать табель", command=open_new_window, font=('Arial', 16), bg='#FFFFE4')

button.pack(pady=30)

window.mainloop()

