import hashlib
from sqlalchemy.orm import Session
from app.models import Account, Payment
from fastapi import HTTPException
from app.config import SECRET_KEY

def generate_signature(data: dict) -> str:
    keys = sorted(data.keys())
    raw_string = ''.join(f"{key}{data[key]}" for key in keys)
    raw_string += SECRET_KEY
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

def process_payment(data: dict, db: Session):
    signature = data.pop("signature")
    if generate_signature(data) != signature:
        raise HTTPException(status_code=400, detail="Invalid signature")

    account = db.query(Account).filter(Account.id == data["account_id"]).first()
    if not account:
        account = Account(id=data["account_id"], user_id=data["user_id"])
        db.add(account)

    existing_payment = db.query(Payment).filter(Payment.transaction_id == data["transaction_id"]).first()
    if existing_payment:
        raise HTTPException(status_code=400, detail="Transaction already processed")

    payment = Payment(
        transaction_id=data["transaction_id"],
        amount=data["amount"],
        account_id=data["account_id"],
        user_id=data["user_id"]
    )
    account.balance += data["amount"]
    db.add(payment)
    db.commit()
