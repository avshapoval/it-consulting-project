import pymysql
import random
from datetime import datetime, timedelta, time

# Подключение к базе данных
con_params = {}
with open ('./.env', 'r') as f:
    con_params['HOST'] = '84.201.158.141'
    for line in f.readlines():
        param_value = line.strip('\n').split('=')
        con_params[param_value[0].strip()] = param_value[1].strip()

db = pymysql.connect(host=con_params['HOST'],
                     user=con_params['MYSQL_USER'],
                     password=con_params['MYSQL_PASSWORD'],
                     db=con_params['MYSQL_DATABASE'])

cursor = db.cursor()

# Получение списка всех сотрудников
cursor.execute("SELECT employee_id FROM employee")
employee_ids = [item[0] for item in cursor.fetchall()]

# Выбор 20 случайных сотрудников
selected_employees = random.sample(employee_ids, 20)

# Получение списка всех терминалов
cursor.execute("SELECT terminal_id FROM terminal")
terminal_ids = [item[0] for item in cursor.fetchall()]

# Задаем начальную и конечную дату мая 2023 года
start_date = datetime(2023, 5, 1)
end_date = datetime(2023, 5, 31)

# Для каждого дня между начальной и конечной датой
date = start_date
while date <= end_date:
    # Для каждого выбранного сотрудника
    for employee_id in selected_employees:
        # С вероятностью 95% сотрудник приходит и уходит
        if random.random() < 0.95:
            # Выбираем случайный терминал
            terminal_id = random.choice(terminal_ids)
            # Получение UUID отпечатка пальца сотрудника
            cursor.execute(f"SELECT fingerprint_uuid FROM emp_fingerprint WHERE employee_id = {employee_id}")
            fingerprint_uuid = cursor.fetchone()[0]

            # Генерируем случайное время прихода и ухода сотрудника
            arrival_hour = random.randint(7, 8)
            arrival_minute = random.randint(30, 59) if arrival_hour == 7 else random.randint(0, 30)
            arrival_time = datetime.combine(date, time(arrival_hour, arrival_minute))

            departure_hour = random.randint(16, 19)
            departure_minute = random.randint(0, 59)
            departure_time = datetime.combine(date, time(departure_hour, departure_minute))

            # Вставляем данные о приходе и уходе сотрудника в таблицу visit
            for visit_time in [arrival_time, departure_time]:
                cursor.execute("INSERT INTO visit (terminal_id, fingerprint_uuid, is_matched, visit_ts) VALUES (%s, %s, %s, %s)",
                               (terminal_id, fingerprint_uuid, True, visit_time))

    # Переходим к следующему дню
    date += timedelta(days=1)

# Подтверждаем изменения в базе данных
db.commit()

# Закрываем соединение с базой данных
db.close()
