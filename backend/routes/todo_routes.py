"""
todo_routes.py — HOW THIS WORKS:
-----------------------------------
All todo routes are PROTECTED — you must be logged in (valid JWT) to use them.

CRUD Operations:
- CREATE  → POST   /todos/
- READ    → GET    /todos/         (all todos for current user)
           GET    /todos/{id}     (single todo)
- UPDATE  → PUT    /todos/{id}
- DELETE  → DELETE /todos/{id}

Key concept: Depends(auth.get_current_user)
This means FastAPI automatically:
1. Extracts JWT from request header
2. Decodes it to get user_id
3. Fetches that user from DB
4. Injects the User object into our function as current_user

If no valid token → 401 Unauthorized before route even runs!
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.post("/", response_model=schemas.TodoResponse, status_code=201)
def create_todo(
    todo_data: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
    # current_user is automatically injected from the JWT token!
):
    """
    POST /todos/
    Body: { "title": "Buy groceries", "description": "Milk, eggs" }
    
    Notice: we use current_user.id as owner_id.
    Users can ONLY create todos for themselves — no way to fake ownership.
    """
    new_todo = models.Todo(
        title=todo_data.title,
        description=todo_data.description,
        owner_id=current_user.id  # Ownership set from JWT, not from request body
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@router.get("/", response_model=List[schemas.TodoResponse])
def get_all_todos(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    GET /todos/
    Returns all todos belonging to the currently logged-in user.
    
    The WHERE owner_id = current_user.id ensures users ONLY see their own todos.
    """
    todos = db.query(models.Todo).filter(
        models.Todo.owner_id == current_user.id
    ).all()
    return todos


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def get_single_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    GET /todos/{todo_id}
    
    We filter by BOTH todo_id AND owner_id.
    This prevents User A from accessing User B's todos by guessing IDs.
    If todo not found (or belongs to someone else) → 404 Not Found.
    """
    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.owner_id == current_user.id
    ).first()

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with id {todo_id} not found"
        )
    return todo


@router.put("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int,
    todo_data: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    PUT /todos/{todo_id}
    Body: { "completed": true }  (only send fields you want to change)
    
    We check if each field is not None before updating.
    This allows partial updates — send only what changed.
    """
    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.owner_id == current_user.id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")

    # Only update fields that were actually sent in the request
    if todo_data.title is not None:
        todo.title = todo_data.title
    if todo_data.description is not None:
        todo.description = todo_data.description
    if todo_data.completed is not None:
        todo.completed = todo_data.completed

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=200)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """DELETE /todos/{todo_id}"""
    todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id,
        models.Todo.owner_id == current_user.id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")

    db.delete(todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
