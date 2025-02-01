from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str

class PaymentCreate(BaseModel):
    transaction_id: str
    amount: float
    account_id: int
    user_id: int
    signature: str