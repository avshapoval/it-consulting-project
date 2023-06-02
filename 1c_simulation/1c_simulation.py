import pymysql
import pandas as pd
import tkinter as tk
from tkinter import ttk
from pandastable import Table
from os.path import dirname, abspath

# Параметры подключения к базе данных
con_params = {}
parent_dir = dirname(dirname(abspath(__file__)))

with open (f'{parent_dir}/.env', 'r') as f:
    con_params['HOST'] = '84.201.158.141'
    for line in f.readlines():
        param_value = line.strip('\n').split('=')
        con_params[param_value[0].strip()] = param_value[1].strip()

# Создаем подключение к базе данных
connection = pymysql.connect(host=con_params['HOST'],
                     user=con_params['MYSQL_USER'],
                     password=con_params['MYSQL_PASSWORD'],
                     db=con_params['MYSQL_DATABASE'],
                     cursorclass=pymysql.cursors.DictCursor,
                     port=3306)

# Запрос на получение имен и фамилий сотрудников
query = """
SELECT employee.employee_id, employee.first_name, employee.last_name
FROM employee
INNER JOIN emp_fingerprint ON employee.employee_id = emp_fingerprint.employee_id
INNER JOIN visit ON emp_fingerprint.fingerprint_uuid = visit.fingerprint_uuid
WHERE MONTH(visit.visit_ts) = 5
GROUP BY employee.employee_id
"""


# Выполняем запрос и получаем все записи
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

    # Выполняем запрос и получаем все записи
    with connection.cursor() as cursor:
        cursor.execute(query)
        visit_records = cursor.fetchall()

    # Конвертируем записи в Pandas DataFrame
    df = pd.DataFrame(visit_records)

    # Переименовываем столбцы
    df.rename(columns={
        'visit_date': 'Дата',
        'hours_on_work': 'Времени на работе'
    }, inplace=True)

    # Переводим дробное количество часов в часы и минуты
    df['Времени на работе'] = df['Времени на работе'].apply(lambda x: f"{int(x)} hours {int((x % 1) * 60)} minutes")

    # Добавляем сумму времени на работе внизу таблицы
    total_hours = df['Времени на работе'].apply(lambda x: pd.Timedelta(x)).sum()
    print(type(total_hours))
    total_hours_row = pd.DataFrame(
        {'Дата': ['Всего часов'], 'Времени на работе': [str(total_hours.total_seconds() // 3600) + " часов"]})
    df = pd.concat([df, total_hours_row], ignore_index=True)

    # Создаем новое окно и отображаем информацию о выбранном сотруднике и его рабочем времени в виде таблицы
    new_window = tk.Toplevel(window)
    new_window.geometry("800x900")  # Устанавливаем ширину 800 пикселей и высоту 600 пикселей
    new_window.title('Табель Т13')
    tk.Label(new_window, text=f"Выбранный сотрудник: {employee_name}", font=('Arial', 14)).pack()
    frame = tk.Frame(new_window)
    frame.pack(fill='both', expand=True)  # Размещаем frame так, чтобы он заполнял все доступное пространство
    pt = Table(frame, dataframe=df, showtoolbar=True, showstatusbar=True)
    pt.autoResizeColumns()  # Автоматически изменяем размеры столбцов под их содержимое
    pt.show()


# Создаем окно
window = tk.Tk()
window.title('Табель ГК Альянс: 2C')
window.geometry('500x500')
window.configure(bg='#FFFF7F')

# Добавляем заголовок
title = tk.Label(window, text="Выберите сотрудника и месяц", font=('Arial', 20), bg='#FFFF7F')
title.pack(pady=30)

# Создаем словарь, где ключ - это id сотрудника, а значение - его имя и фамилия
employee_dict = {record['employee_id']: f"{record['employee_id']}, {record['first_name']} {record['last_name']}" for record in records}

# Создаем выпадающий список с именами и фамилиями сотрудников
employee_label = tk.Label(window, text="Выберите сотрудника", font=('Arial', 16), bg='#FFFF7F')
employee_label.pack(pady=20)
combo = ttk.Combobox(window, values=list(employee_dict.values()), font=('Arial', 14))
combo.pack(pady=20)

# Создаем выпадающий список с месяцами
month_label = tk.Label(window, text="Выберите месяц", font=('Arial', 16), bg='#FFFF7F')
month_label.pack(pady=20)

month_var = tk.StringVar()
russian_months = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']


# Создаем выпадающий список с названиями месяцев на русском языке
month_combobox = ttk.Combobox(window, values=russian_months, textvariable=month_var, font=('Arial', 14))
month_combobox.pack(pady=20)

# Добавляем кнопку, при нажатии на которую открывается новое окно с выбранным сотрудником и месяцем
button = tk.Button(window, text="Сделать табель", command=open_new_window, font=('Arial', 16), bg='#FFFFE4')

button.pack(pady=30)

window.mainloop()
