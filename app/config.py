import os

DB_HOST = os.getenv("DB_HOST", "localhost")  
DB_USER = "postgres"
DB_PASSWORD = "111"
DB_NAME = "app_db"
DB_PORT = 5432

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
SECRET_KEY = "gfdmhghif38yrf9ew0jkf32" # ONLY FOR TEST PURPOSES!!!!!!
ALGORITHM = "HS256"
