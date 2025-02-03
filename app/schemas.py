from pydantic import BaseModel, EmailStr, field_validator
from decimal import *
import re

class UserAdminCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    is_admin: bool = False
    @field_validator('full_name')
    def name_must_be_valid(cls, value):
        if not re.match(r'^[A-Za-zА-Яа-яЁё]+$', value):
            raise ValueError('letters only!')
        return value

class UserAdminUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_admin: bool | None = None
    @field_validator('full_name')
    def name_must_be_valid(cls, value):
        if not re.match(r'^[A-Za-zА-Яа-яЁё]+$', value):
            raise ValueError('letters only!')
        return value

class PaymentCreate(BaseModel):
    transaction_id: str
    amount: Decimal
    account_id: int
    user_id: int
    signature: str