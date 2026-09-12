"""
models.py — HOW THIS WORKS:
-----------------------------
Each Python class here = one table in PostgreSQL.
Each class attribute = one column in that table.

When we run: Base.metadata.create_all(bind=engine)
SQLAlchemy reads these classes and runs CREATE TABLE SQL automatically.

Relationship between User and Todo:
- One User can have MANY Todos (One-to-Many)
- Each Todo belongs to ONE User (foreign key: owner_id)
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"  # This is the actual table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    # primary_key → unique identifier for each row
    # index=True → creates a DB index (makes lookups by id faster)

    username = Column(String, unique=True, index=True)
    # unique=True → no two users can have same username
    # index=True → fast lookup by username

    email = Column(String, unique=True, index=True)

    hashed_password = Column(String)
    # NEVER store plain password! We always hash it with bcrypt before saving.
    # Even if DB is hacked, attacker can't recover original passwords.

    created_at = Column(DateTime, default=datetime.utcnow)
    # default → automatically sets current time when a user is created

    todos = relationship("Todo", back_populates="owner")
    # This is NOT a column — it's a Python-level helper.
    # It lets us access user.todos to get all todos for that user.
    # SQLAlchemy runs a JOIN query behind the scenes.


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    # nullable=True → description is optional, can be NULL in DB

    completed = Column(Boolean, default=False)
    # Boolean → true/false. Default is False (not completed).

    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    # ForeignKey → this column MUST match an id in the users table.
    # This is how we link todos to their owner.
    # PostgreSQL enforces this — you can't add a todo with a non-existent user.

    owner = relationship("User", back_populates="todos")
    # Lets us access todo.owner to get the User object.
