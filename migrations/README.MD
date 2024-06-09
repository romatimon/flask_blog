Single-database configuration for Flask.

flask db migrate -m "users table" - генерирует сценарий миграции.
flask db upgrade - применяет изменения к базе данных.
flask db downgrade - отменяет и удаляет последнюю миграцию, base - вызывает понижение рейтинга всех миграций до тех пор, пока база данных не останется в исходном состоянии, без таблиц.

db.session.add(u) - добавляет запись в базу данных
db.session.commit() - сохраняет изменения

db.session.scalars() выполняет запрос к базе данных и возвращает итератор результатов
