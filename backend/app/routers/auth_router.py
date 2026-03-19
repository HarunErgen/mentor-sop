from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr
from app.db.database import get_db
from app.db.models import User, VerificationCode
from app.auth.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    generate_verification_code,
    send_verification_email,
    SECRET_KEY,
    ALGORITHM
)
import os
from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
import jwt
from jwt.exceptions import InvalidTokenError
from app.utils.usage import check_and_reset_tokens

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class VerifyEmail(BaseModel):
    email: EmailStr
    code: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_verified: bool
    auth_provider: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_verified=False,
        auth_provider="local"
    )
    db.add(new_user)
    await db.flush()

    code = generate_verification_code()
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    new_code = VerificationCode(email=user_in.email, code=code, expires_at=expires.replace(tzinfo=None))
    db.add(new_code)
    await db.commit()

    await send_verification_email(user_in.email, code)

    return {"msg": "User created. Verification code sent to email."}

@router.post("/verify")
async def verify_user(verify_in: VerifyEmail, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VerificationCode)
        .where(VerificationCode.email == verify_in.email)
        .where(VerificationCode.code == verify_in.code)
    )
    db_code = result.scalars().first()

    if not db_code:
        raise HTTPException(status_code=400, detail="Invalid verification code")

    if datetime.utcnow() > db_code.expires_at:
        raise HTTPException(status_code=400, detail="Verification code expired")

    user_result = await db.execute(select(User).where(User.email == verify_in.email))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await db.delete(db_code)
    await db.commit()

    return {"msg": "Email verified successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or user.auth_provider != "local" or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

class GoogleLoginRequest(BaseModel):
    token: str

@router.post("/google/login", response_model=Token)
async def google_login(request: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Auth is not configured on the server")

    try:
        idinfo = id_token.verify_oauth2_token(request.token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=5)
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = idinfo['email']
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {e}")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        user = User(
            email=email,
            hashed_password=None, 
            is_verified=True,     
            auth_provider="google"
        )
        db.add(user)
        await db.commit()
    elif user.auth_provider != "google":
        user.auth_provider = "google"
        user.is_verified = True
        await db.commit()
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    
    # Check and reset tokens monthly
    user = await check_and_reset_tokens(user, db)
    
    return user
