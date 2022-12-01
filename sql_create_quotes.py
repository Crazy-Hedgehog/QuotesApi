import sqlite3

create_quotes = """
INSERT INTO
quotes (author,text)
VALUES
('Yoggi Berra', 'В теории, теория и практика неразделимы. На практике это не так.'),
('Mosher’s Law of Software Engineering', 'Не волнуйтесь, если что-то не работает. Если бы всё работало, вас бы уволили.');
"""

# Подключение в БД
connection = sqlite3.connect("test.db")
# Создаем cursor, он позволяет делать SQL-запросы
cursor = connection.cursor()
# Выполняем запрос:
cursor.execute(create_quotes)
# Фиксируем выполнение(транзакцию)
connection.commit()
# Закрыть курсор:
cursor.close()
# Закрыть соединение:
connection.close()
