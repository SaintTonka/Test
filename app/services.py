import hashlib,logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Account, Payment
from fastapi import HTTPException
from app.config import SECRET_KEY
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def generate_signature(data: dict) -> str:
    required_fields = ["transaction_id", "account_id", "user_id", "amount"]
    sorted_data = {k: data[k] for k in sorted(required_fields)}
    raw_string = ''.join(f"{k}{v}" for k, v in sorted_data.items()) + SECRET_KEY
    return hashlib.sha256(raw_string.encode()).hexdigest()

async def process_payment(data: dict, db: AsyncSession):
    signature = data.pop("signature")
    logger.info(f"Received signature: {signature}")
    
    generated_signature = generate_signature(data)
    logger.info(f"Generated signature: {generated_signature}")
    
    if generated_signature != signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    result = await db.execute(
        select(Account).where(Account.id == data["account_id"])
    )
    account = result.scalar_one_or_none()

    if not account:
        account = Account(user_id=data["user_id"]) 
        db.add(account)
        await db.flush()  

    result = await db.execute(
    select(Payment).where(Payment.transaction_id == data["transaction_id"])
    )
    if result.scalar_one_or_none():
        logger.warning(f"Transaction {data['transaction_id']} already processed")
        raise HTTPException(status_code=400, detail="Transaction already processed")

    payment = Payment(
        transaction_id=data["transaction_id"],
        amount=data["amount"],
        account_id=data["account_id"],
        user_id=data["user_id"]
    )
    account.balance += data["amount"]
    db.add(payment)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
