# INSRTUCTION
#Non Docker
1) python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate     # Для Windows
Сам я использую conda

2) pip install -r requirements.txt

3) Создайте базу данных (CУБД PostgreSQL) и настройте параметры подключения в файле config.py.user: postgres:111@localhost:5432/app_db

4) Запустите миграции python -m app.database

5) Запустите сервер uvicorn app.main:app --reload

6) Для проверки работы API можете перейти по ссылке http://localhost:8000/docs, откроется SWAGGER

# WIth Docker

1) docker-compose up --build

2) Также можете перейти по ссылке http://localhost:8000/docs

#SWAGGER

1) Авторизация:
Admin:
username: admin@example.com
password: adminpass
Пользователь:
username: user@example.com
password: pass
(У пользователя уже есть платежи и баланс)

2) Можете тестировать методы, ОДНАКО!!! для проверки метода (через Пользователя) process payment в тело запроса надо будет указать подпись, для этого необходимо будем запустить sign_generator.py
python sign_generator.py
Для Докера вначале:
docker exec -it test-app-1 /bin/bas
У вас в консоли появиться подпись.
Для проверки используйте след.данные
{
  "transaction_id": "transaction_123",
  "amount": 50.0,
  "account_id": 2,
  "user_id": 2,
  "signature": "(Сюда вставите значение из консоли)"
}
Вроде бы все
