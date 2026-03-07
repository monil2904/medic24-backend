from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.config import settings
from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(user_id: str, email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)
    to_encode = {
        "sub": str(user_id),
        "email": email,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def verify_google_token(token: str) -> dict:
    try:
        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        
        # We only want basic information
        return {
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "google_id": idinfo.get("sub")
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
