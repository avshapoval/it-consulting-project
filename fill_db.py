from faker import Faker
import random
import uuid
import pymysql
import datetime

fake = Faker(locale='ru_RU')

con_params = {}
with open ('./.env', 'r') as f:
    con_params['HOST'] = '84.201.158.141'
    for line in f.readlines():
        param_value = line.strip('\n').split('=')
        con_params[param_value[0].strip()] = param_value[1].strip()


# Подключение к базе данных
db = pymysql.connect(host=con_params['HOST'],
                     user=con_params['MYSQL_USER'],
                     password=con_params['MYSQL_PASSWORD'],
                     db=con_params['MYSQL_DATABASE'])

cursor = db.cursor()

# Список позиций (должностей)
positions = ["Инженер", "Разработчик", "Менеджер", "Аналитик", "Дизайнер", "Архитектор", "Тестировщик", "Администратор", "Консультант", "Поддержка"]

# Добавление позиций в базу данных
for position in positions:
    sql = "INSERT INTO emp_position (position_name) VALUES (%s)"
    cursor.execute(sql, (position,))

# Создание и добавление 120 фиктивных сотрудников в базу данных
for _ in range(120):
    last_name = fake.last_name()
    first_name = fake.first_name()
    birth_date = fake.date_of_birth(minimum_age=22, maximum_age=65)
    works_since = fake.date_between(start_date='-5y', end_date='today')
    position_id = random.randint(1, 10)
    
    sql = "INSERT INTO employee (last_name, first_name, birth_date, works_since, position_id) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (last_name, first_name, birth_date, works_since, position_id))
    
    # Добавление отпечатка пальца для каждого сотрудника
    fingerprint_uuid = str(uuid.uuid4())
    employee_id = cursor.lastrowid
    sql = "INSERT INTO emp_fingerprint (fingerprint_uuid, employee_id) VALUES (%s, %s)"
    cursor.execute(sql, (fingerprint_uuid, employee_id))

# Создание и добавление 3 терминалов в базу данных
for _ in range(3):
    terminal_uuid = str(uuid.uuid4())
    is_active = 1
    deployed_at = datetime.datetime.now()
    
    sql = "INSERT INTO terminal (terminal_uuid, is_active, deployed_at) VALUES (%s, %s, %s)"
    cursor.execute(sql, (terminal_uuid, is_active, deployed_at))

# Commit транзакции
db.commit()

# Закрытие соединения с базой данных
db.close()
