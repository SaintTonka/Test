import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from logging.config import fileConfig

# Добавляем путь к проекту
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import Base  # Импортируйте вашу базовую модель

# Эта строка берется из alembic.ini
config = context.config

# Настраиваем логгер
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Получаем URL базы данных из конфига
target_metadata = Base.metadata
sqlalchemy_url = config.get_main_option("sqlalchemy.url")

def do_run_migrations(connection):
    # Настраиваем контекст Alembic
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        process_bindings=True,
    )

    # Запускаем миграции
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Асинхронно запускаем миграции"""
    # Создаем асинхронный движок
    engine = create_async_engine(sqlalchemy_url)

    # Подключаемся к базе и запускаем миграции через run_sync
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()

def run_migrations():
    """Запускаем миграции в зависимости от режима"""
    if context.is_offline_mode():
        # Офлайн-режим (генерация SQL)
        url = config.get_main_option("sqlalchemy.url")
        context.configure(
            url=url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )
        with context.begin_transaction():
            context.run_migrations()
    else:
        # Онлайн-режим (асинхронное выполнение)
        asyncio.run(run_migrations_online())

# Запускаем миграции
run_migrations()