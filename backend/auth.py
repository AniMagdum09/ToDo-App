"""
auth.py — HOW THIS WORKS:
---------------------------
This is the security core of the app. Three main responsibilities:

1. PASSWORD HASHING
   - Use bcrypt (industry standard) via passlib
   - bcrypt is a one-way function: "password123" → "$2b$12$..." (cannot reverse)
   - Each hash includes a random "salt" so same password produces different hashes

2. JWT TOKEN CREATION
   - After login, we create a JWT with: {"sub": user_id, "exp": expiry_time}
   - We SIGN it with SECRET_KEY — only our server can create valid tokens
   - Client stores this token and sends it with every request

3. GET CURRENT USER (FastAPI Dependency)
   - FastAPI calls get_current_user() for protected routes automatically
   - It extracts the token from Authorization header, decodes it, fetches user from DB
   - If token is invalid/expired → 401 Unauthorized automatically
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-change-in-production")
ALGORITHM = "HS256"   # HMAC + SHA256 — the JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# CryptContext handles password hashing and verification
# bcrypt is the recommended algorithm — it's slow on purpose (makes brute-force hard)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer tells FastAPI:
# "look for the token in the Authorization header as 'Bearer <token>'"
# tokenUrl="/auth/login" — just for documentation (Swagger UI uses this)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """
    Convert plain text password to bcrypt hash.
    Example: "mypassword" → "$2b$12$KIx3GVHJ8..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if plain_password matches the stored hash.
    bcrypt.verify() re-hashes the input and compares — returns True/False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a signed JWT token.
    
    Example payload: {"sub": "42", "exp": 1729012345}
    - "sub" (subject) = user ID — who this token belongs to
    - "exp" (expiry) = Unix timestamp — token invalid after this time
    
    The token is SIGNED with SECRET_KEY. If anyone tampers with the payload,
    the signature won't match and jwt.decode() will raise JWTError.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # jwt.encode() creates: header.payload.signature (3 Base64-encoded parts joined by dots)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    FastAPI Dependency — used in protected routes like:
        @router.get("/todos")
        def get_todos(current_user = Depends(get_current_user)):
            ...
    
    Flow:
    1. FastAPI extracts token from "Authorization: Bearer <token>" header
    2. We decode the JWT to get the user_id
    3. We fetch that user from the database
    4. We return the User object — the route gets it as current_user
    
    If anything fails (invalid token, expired, user deleted), we raise 401.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT — this also checks if signature is valid and token isn't expired
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(user_id=int(user_id))
    except JWTError:
        # JWTError catches: invalid signature, expired token, malformed token
        raise credentials_exception

    # Fetch user from DB to ensure they still exist
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    return user   # This becomes the current_user in our route functions
