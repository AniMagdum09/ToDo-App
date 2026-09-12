"""
schemas.py — HOW THIS WORKS:
------------------------------
Pydantic schemas define the SHAPE of data coming in (requests) and going out (responses).

Why separate from models.py?
- models.py = database structure (how data is STORED)
- schemas.py = API structure (how data is SENT/RECEIVED)

Example: When a user registers, we receive {username, email, password}.
But we NEVER send back the hashed_password in a response!
Schemas let us control exactly what fields are exposed.

FastAPI uses these to:
1. VALIDATE incoming request data automatically (wrong type → 422 error)
2. SERIALIZE outgoing response data (Python object → JSON)
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─── USER SCHEMAS ──────────────────────────────────────────────

class UserCreate(BaseModel):
    """What we expect when a user registers."""
    username: str
    email: EmailStr          # Pydantic validates email format automatically
    password: str            # Plain text — we'll hash this in the route


class UserLogin(BaseModel):
    """What we expect when a user logs in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """What we RETURN about a user — notice: NO password field!"""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
        # This tells Pydantic: "you might receive a SQLAlchemy object,
        # not just a plain dict — read attributes from it directly"
        # Without this, Pydantic can't read from SQLAlchemy model instances.


# ─── TOKEN SCHEMAS ──────────────────────────────────────────────

class Token(BaseModel):
    """What we return after a successful login."""
    access_token: str
    token_type: str          # Always "bearer"


class TokenData(BaseModel):
    """Data we decode from a JWT token."""
    user_id: Optional[int] = None


# ─── TODO SCHEMAS ───────────────────────────────────────────────

class TodoCreate(BaseModel):
    """What we expect when creating a new todo."""
    title: str
    description: Optional[str] = None   # Optional — can be None


class TodoUpdate(BaseModel):
    """
    What we accept when updating a todo.
    All fields Optional — user might update only title, or only completed status.
    This is called a PATCH schema (partial update).
    """
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    """What we return for a todo."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
