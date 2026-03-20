import os
import random
import string
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import jwt

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_verification_code() -> str:
    return "".join(random.choices(string.digits, k=6))

from email.message import EmailMessage
import aiosmtplib

async def send_verification_email(email: str, code: str) -> None:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_host or not smtp_user or not smtp_password or smtp_user == "your_email@gmail.com":
        print(f"WARNING: SMTP credentials missing or placeholder used in .env. Mocking email to {email} with code {code}.")
        print(f"DEBUG: Verification code for {email}: {code}")
        return

    message = EmailMessage()
    message["From"] = smtp_user
    message["To"] = email
    message["Subject"] = "MentorSOP - Your Verification Code"
    message.set_content(f"Your verification code is {code}. It will expire in 15 minutes.")

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_host,
            port=smtp_port,
            start_tls=True,
            username=smtp_user,
            password=smtp_password,
        )
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
        print(f"WARNING: Falling back to console. Verification code for {email}: {code}")
