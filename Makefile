# перед всеми командами надо ввести: mingw32-make
install-lib:
	pip install $(lib)

# Удаление указанной библиотеки
uninstall-lib:
	pip uninstall -y $(lib)

# Создание файла requirements.txt
freeze:
	pip freeze > requirements.txt

# Запуск FastAPI проекта на порту 8000
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Создать миграции
make-migrate:
	alembic revision --autogenerate -m $(MIGRATE)

# Применить миграции
migrate:
	alembic upgrade head

# Узнать PID, порт, хост
server_info:
	netstat -ano | findstr :8000

# Принудительная остановка сервера=/F по PID (Process ID) — это уникальный идентификатор процесса
server_kill:
	taskkill /PID $(PID) /F