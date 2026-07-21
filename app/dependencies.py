import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select

# We reuse the Base from database setup to pull the user object later if needed
from app.database import AsyncSessionLocal, get_db
from app.models import User
from app.schemas.user import TokenData

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise ValueError("JWT_SECRET environment variable is missing!")

# Indicates where FastAPI should look to extract the token payload
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    # Query the user model from the database using SQLAlchemy 2.0 select syntax
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalars().first()
    
    if user is None:
        raise credentials_exception
    return user