from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Account, Payment
from app.config import DATABASE_URL
from app.security import get_password_hash

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def create_all_async(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        if not await session.get(User, 1):
            admin = User(
            email="admin@example.com",
            full_name="Admin User",
            password_hash=get_password_hash("adminpass"),
            is_admin=True
        )
            session.add(admin)
            await session.commit()

    async with AsyncSessionLocal() as session:
        if not await session.get(User, 2):
            user = User(
                email="user@example.com",
                full_name="Test User",
                password_hash=get_password_hash("pass"),
                is_admin=False
            )
            session.add(user)
            await session.commit()

        user = await session.get(User, 2)
        if user:
            account = Account(user_id=user.id, balance=100.0)
            session.add(account)
            await session.commit()

            payment1 = Payment(
                transaction_id="transaction_1",
                amount=50.0,
                account_id=account.id,
                user_id=user.id
            )
            payment2 = Payment(
                transaction_id="transaction_2",
                amount=30.0,
                account_id=account.id,
                user_id=user.id
            )

            session.add(payment1)
            session.add(payment2)
            await session.commit()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session