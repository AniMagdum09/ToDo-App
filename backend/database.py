"""
database.py — HOW THIS WORKS:
-------------------------------
SQLAlchemy is an ORM (Object Relational Mapper).
Instead of writing raw SQL like:
    cursor.execute("SELECT * FROM users WHERE id = 1")
We write Python like:
    db.query(User).filter(User.id == 1).first()

Here we:
1. Create an "engine" — the actual connection to PostgreSQL
2. Create a "SessionLocal" — each request gets its own database session
3. Create "Base" — our Python models (tables) will inherit from this
4. Define get_db() — FastAPI calls this to give each route a fresh DB session
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

DATABASE_URL = "sqlite:///./todo.db"

# Engine = the actual connection pool to PostgreSQL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal = factory that creates individual sessions
# autocommit=False → we manually commit transactions (safer, we control when to save)
# autoflush=False  → changes aren't sent to DB until we call commit()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = parent class for all our models (User, Todo)
# When we create models, SQLAlchemy reads their class definition
# and knows which table to create in PostgreSQL
Base = declarative_base()


def get_db():
    """
    This is a FastAPI dependency.
    FastAPI calls this function for every request that needs a DB session.
    
    The 'yield' makes it a generator:
    - Before yield: opens the DB session
    - FastAPI uses the session in the route function
    - After yield (in finally): always closes session, even if there's an error
    
    Usage in routes:
        @router.get("/todos")
        def get_todos(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
