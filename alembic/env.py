import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from logging.config import fileConfig

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import Base 

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
sqlalchemy_url = config.get_main_option("sqlalchemy.url")

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        process_bindings=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Асинхронно запускаем миграции"""
    engine = create_async_engine(sqlalchemy_url)

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()

def run_migrations():
    """Запускаем миграции в зависимости от режима"""
    if context.is_offline_mode():
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
        asyncio.run(run_migrations_online())

run_migrations()