-- Заставляем БД воспринимать текст в строках на русском языке, без этой команды будем ловить ошибки при попытке вставки русского текста
ALTER DATABASE attendance CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci; 

-- Должности
CREATE TABLE IF NOT EXISTS attendance.emp_position(
	position_id int NOT NULL AUTO_INCREMENT,
	position_name varchar(255) NOT NULL,
	PRIMARY key(position_id)
);

-- Сотрудники
CREATE TABLE IF NOT EXISTS attendance.employee(
	employee_id int NOT NULL AUTO_INCREMENT,
	last_name varchar(255) NOT NULL,
	first_name varchar(255),
	birth_date date,
	works_since date,
	position_id int NOT NULL,
	FOREIGN KEY (position_id) REFERENCES emp_position(position_id),
	PRIMARY KEY (employee_id)
);

-- Терминалы
CREATE TABLE IF NOT EXISTS attendance.terminal (
	terminal_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	terminal_uuid varchar(36) NOT NULL,
	is_active bool NOT null,
	deployed_at timestamp
);

-- Отпечатки пальцев - хранятся в виде uuid, подразумевается шифрование биометрии на уровне БД
CREATE TABLE IF NOT EXISTS attendance.emp_fingerprint(
	fingerprint_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	fingerprint_uuid varchar(36) NOT null,
	employee_id int NOT NULL REFERENCES employee(employee_id)
);

-- Зафиксированные попытки приложить палец к терминалу
CREATE TABLE IF NOT EXISTS attendance.visit(
	visit_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	terminal_id int NOT NULL REFERENCES terminal(terminal_id),
	fingerprint_uuid varchar(36) NOT null,
	is_matched bool NOT NULL,
	visit_ts timestamp NOT NULL
);