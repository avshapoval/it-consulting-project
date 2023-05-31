# Использование официального образа в качестве родительского
FROM python:3.7
# Копирование requirements.txt
COPY requirements.txt /app/requirements.txt
# Установка рабочего каталога в контейнере
WORKDIR /app
# Установка необходимых пакетов, указанных в requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Выполнение команды
CMD ["python", "emulate_terminals.py"]
