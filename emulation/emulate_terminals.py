import pymysql
import random
import uuid
from datetime import datetime
import time

# Получаем параметры подключения к БД из .env файла
con_params = {}
with open ('con_params', 'r') as f:
    con_params['HOST'] = 'mydb'
    for line in f.readlines():
        param_value = line.strip('\n').split('=')
        con_params[param_value[0].strip()] = param_value[1].strip()

# Функция для извлечения всех fingerprint_uuid из базы данных и сохранения их в список
def get_fingerprints():
    # Устанавливаем соединение с базой данных
    db = pymysql.connect(host=con_params['HOST'],
                         user=con_params['MYSQL_USER'],
                         password=con_params['MYSQL_PASSWORD'],
                         db=con_params['MYSQL_DATABASE'])
    cursor = db.cursor()
    # Выполняем SQL запрос, чтобы получить все fingerprint_uuid
    sql = "SELECT fingerprint_uuid FROM emp_fingerprint"
    cursor.execute(sql)
    # Получаем результат запроса и сохраняем его в список
    fingerprints = [row[0] for row in cursor.fetchall()]
    # Закрываем соединение с базой данных
    db.close()
    return fingerprints

# Получаем список отпечатков пальцев
fingerprints = get_fingerprints()

# Функция, которая будет выполняться каждые 30 секунд
def visit_logs():
    # Устанавливаем соединение с базой данных
    db = pymysql.connect(host=con_params['HOST'],
                         user=con_params['MYSQL_USER'],
                         password=con_params['MYSQL_PASSWORD'],
                         db=con_params['MYSQL_DATABASE'])
    cursor = db.cursor()
    
    # Генерируем случайное число
    rand = random.random()
    # С вероятностью 80% выбираем существующий отпечаток пальца
    if rand < 0.8:
        fingerprint = random.choice(fingerprints)
        is_matched = True
    # С вероятностью 10% генерируем случайный отпечаток пальца
    elif rand < 0.9:
        fingerprint = str(uuid.uuid4())
        is_matched = fingerprint in fingerprints
    # С вероятностью 10% не распознаем отпечаток пальца
    else:
        fingerprint = None
        is_matched = False
    
    # Случайным образом выбираем один из терминалов
    terminal_id = random.randint(1, 3)
    
    # Получаем текущее время
    visit_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Вставляем данные в таблицу visit
    sql = "INSERT INTO visit (terminal_id, fingerprint_uuid, is_matched, visit_ts) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (terminal_id, fingerprint, is_matched, visit_ts))
    
    # Commit транзакции
    db.commit()
    # Закрываем соединение с базой данных
    db.close()

# Запускаем функцию
while True:
    visit_logs()
    time.sleep(30)
