from fastapi import Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from app.security import pwd_context
from app.models import User
from app.config import SECRET_KEY, ALGORITHM
from app.database import get_db
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user

async def authenticate_user(db: AsyncSession, email: str, password: str):
    print(f"Attempting to authenticate user: {email}")
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    
    if not user:
        print(f"User not found: {email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not pwd_context.verify(password, user.password_hash):
        print(f"Password verification failed for user: {email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return user