-- Заставляем БД воспринимать текст в строках на русском языке, без этой команды будем ловить ошибки при попытке вставки русского текста
ALTER DATABASE attendance CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci; 

-- Должности
CREATE TABLE IF NOT EXISTS emp_position(
	position_id int NOT NULL AUTO_INCREMENT,
	position_name varchar(255) NOT NULL,
	PRIMARY key(position_id)
);

-- Сотрудники
CREATE TABLE IF NOT EXISTS employee(
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
CREATE TABLE IF NOT EXISTS terminal (
	terminal_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	terminal_uuid varchar(36) NOT NULL,
	is_active bool NOT null,
	deployed_at timestamp
);

-- Отпечатки пальцев - хранятся в виде uuid, подразумевается шифрование биометрии на уровне БД
CREATE TABLE IF NOT EXISTS emp_fingerprint(
	fingerprint_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	fingerprint_uuid varchar(36) NOT null,
	employee_id int NOT NULL,
	FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
);

-- Зафиксированные попытки приложить палец к терминалу
CREATE TABLE IF NOT EXISTS visit(
	visit_id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
	terminal_id int NOT NULL,
	fingerprint_uuid varchar(36) NOT null,
	is_matched bool NOT NULL,
	visit_ts timestamp NOT NULL,
	FOREIGN KEY (terminal_id) REFERENCES terminal(terminal_id)
);

-- Таблица, связывающая посещения и отпечатки пальцев сотрудников
CREATE TABLE visit_fingerprint (
	visit_id int,
	fingerprint_id int,
	PRIMARY KEY (visit_id, fingerprint_id),
	FOREIGN KEY (visit_id) REFERENCES visit (visit_id),
	FOREIGN KEY (fingerprint_id) REFERENCES emp_fingerprint (fingerprint_id)
);

-- Триггер, выполняемый при каждой вставке в таблицу visit и добавляющий значений в таблицу visit_fingerprint при успешном распознавании отпечатка
delimiter //

CREATE TRIGGER visit_fingerprint_insert AFTER INSERT ON visit
FOR EACH ROW
BEGIN
    DECLARE fp_id INT;
    
    -- Проверка, что fingerprint_uuid не null
    IF NEW.fingerprint_uuid IS NOT NULL THEN
        -- Проверка, существует ли такой отпечаток в таблице emp_fingerprint
        SELECT fingerprint_id INTO fp_id
        FROM emp_fingerprint 
        WHERE fingerprint_uuid = NEW.fingerprint_uuid;

        -- Если такой отпечаток существует, вставляем новую запись в таблицу visit_fingerprint
        IF fp_id IS NOT NULL THEN
            INSERT INTO visit_fingerprint (visit_id, fingerprint_id)
            VALUES (NEW.visit_id, fp_id);
        END IF;
    END IF;
END//

DELIMITER ;
