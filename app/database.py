from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import Base, User, Account, Payment
from app.config import DATABASE_URL
from app.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

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
            logger.info("Admin user created.")

        if not await session.get(User, 2):  
            user = User(
                email="user@example.com",
                full_name="Test User",
                password_hash=get_password_hash("pass"),
                is_admin=False
            )
            session.add(user)
            await session.commit()
            logger.info("Test user created.")
        
        user = await session.get(User, 2)
        if user:
            existing_account = await session.execute(
                select(Account).filter(Account.user_id == user.id)
            )
            account = existing_account.scalar_one_or_none()

            if not account:
                account = Account(user_id=user.id, balance=100.0)
                session.add(account)
                await session.commit()
                logger.info(f"Account created for user {user.id}.")
            
            await session.refresh(account)
            logger.info(f"Account refreshed: {account.id}")

            # Создание транзакций
            existing_payment = await session.execute(
                select(Payment).filter(Payment.transaction_id == 'transaction_1')
            )
            if not existing_payment.scalars().first():
                payment1 = Payment(
                    transaction_id="transaction_1",
                    amount=50.0,
                    account_id=account.id,
                    user_id=user.id
                )
                session.add(payment1)
                logger.info("Transaction 1 created.")

            existing_payment = await session.execute(
                select(Payment).filter(Payment.transaction_id == 'transaction_2')
            )
            if not existing_payment.scalars().first():
                payment2 = Payment(
                    transaction_id="transaction_2",
                    amount=30.0,
                    account_id=account.id,
                    user_id=user.id
                )
                session.add(payment2)
                logger.info("Transaction 2 created.")

            await session.commit()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session