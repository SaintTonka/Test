from fastapi import Depends, HTTPException
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import services, auth
from app.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.models import User, Account, Payment
from app.auth import (
    get_admin_user, 
    get_current_user,
)
from app.schemas import PaymentCreate, UserAdminCreate, UserAdminUpdate
from app.security import get_password_hash
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter()

@router.post("/process_payment")
async def process_payment(data: PaymentCreate, db: AsyncSession = Depends(get_db)):
    try:
        await services.process_payment(data.dict(), db)
        return {"status": "success"}
    except HTTPException as e:
        raise e
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail} for transaction_id: {data.transaction_id}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)} for transaction_id: {data.transaction_id}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await auth.authenticate_user(db, form_data.username, form_data.password)
        access_token = auth.create_access_token(
            data={"sub": user.email, "is_admin": user.is_admin}
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login failed for username: {form_data.username} with error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid credentials")

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    logger.info(f"Fetching data for user: {user.email}")
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name
    }

@router.get("/accounts")
async def get_accounts(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Account).where(Account.user_id == user.id))
        accounts = result.scalars().all()
        logger.info(f"Found {len(accounts)} accounts for user {user.email}")
        return [{"id": acc.id, "balance": float(acc.balance)} for acc in accounts]
    except Exception as e:
        logger.error(f"Error fetching accounts for user {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching accounts")

@router.get("/payments")
async def get_payments(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Payment).where(Payment.user_id == user.id))
        payments = result.scalars().all()
        logger.info(f"Found {len(payments)} payments for user {user.email}")
        return [{"transaction_id": p.transaction_id, "amount": float(p.amount)} for p in payments]
    except Exception as e:
        logger.error(f"Error fetching payments for user {user.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching payments")


#admin
@router.get("/admin/users")
async def admin_get_users(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "full_name": u.full_name} for u in users]

@router.post("/admin/users", response_model=dict)
async def create_user(
    user_data: UserAdminCreate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):

    existing_user = await db.execute(select(User).where(User.email == user_data.email))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=get_password_hash(user_data.password),
        is_admin=user_data.is_admin
    )
    
    db.add(new_user)
    
    try:
        await db.commit()
        await db.refresh(new_user)
    except exc.SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")
    
    return {
        "id": new_user.id,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "is_admin": new_user.is_admin
    }

@router.patch("/admin/users/{user_id}")
async def update_user(
    user_id: int,
    update_data: UserAdminUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.email and update_data.email != user.email:
        existing = await db.execute(select(User).where(User.email == update_data.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = update_data.email

    if update_data.full_name:
        user.full_name = update_data.full_name

    if update_data.password:
        user.password_hash = get_password_hash(update_data.password)

    if update_data.is_admin is not None:
        user.is_admin = update_data.is_admin

    try:
        await db.commit()
        await db.refresh(user)
    except exc.SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")

    return {"status": "success"}

@router.delete("/admin/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    try:
        await db.delete(user)
        await db.commit()
    except exc.SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database operation failed")
    
    return {"status": "success", "message": "User deleted successfully"}