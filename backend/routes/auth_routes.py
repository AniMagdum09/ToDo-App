"""
auth_routes.py — HOW THIS WORKS:
----------------------------------
Two endpoints:

POST /auth/register → Create new user account
POST /auth/login    → Verify credentials, return JWT token

The "router" is a mini FastAPI app. We include it in main.py.
This keeps code organized — each file handles its own group of routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import auth

# prefix="/auth" means all routes here start with /auth
# tags=["Authentication"] groups them in Swagger docs
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    POST /auth/register
    Body: { "username": "ani", "email": "ani@gmail.com", "password": "mypass123" }
    Returns: User object (without password)
    
    Steps:
    1. Check if email/username already exists
    2. Hash the password
    3. Save new user to DB
    4. Return the user (Pydantic converts it to JSON automatically)
    """

    # Step 1: Check for duplicate email or username
    existing_user = db.query(models.User).filter(
        (models.User.email == user_data.email) |
        (models.User.username == user_data.username)
    ).first()
    # The | operator = OR in SQLAlchemy filters

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )

    # Step 2: Hash the password BEFORE storing
    hashed_password = auth.hash_password(user_data.password)

    # Step 3: Create new User instance and save to DB
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)       # Stage the new user (like git add)
    db.commit()            # Save to PostgreSQL (like git commit)
    db.refresh(new_user)   # Reload from DB to get auto-generated fields (id, created_at)

    return new_user
    # FastAPI sees response_model=UserResponse → converts User to UserResponse schema
    # This automatically REMOVES hashed_password from the response!


@router.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    POST /auth/login
    Body: { "email": "ani@gmail.com", "password": "mypass123" }
    Returns: { "access_token": "eyJ...", "token_type": "bearer" }
    
    Steps:
    1. Find user by email
    2. Verify password against stored hash
    3. Create JWT token with user ID
    4. Return the token
    """

    # Step 1: Find user by email
    user = db.query(models.User).filter(models.User.email == user_data.email).first()

    # Step 2: Verify password
    # We use the same 'or' pattern — if user not found OR password wrong, same error
    # (Don't say "email not found" — that tells attackers which emails are registered!)
    if not user or not auth.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Step 3: Create JWT token
    # We put user.id (as string) in the "sub" (subject) field of the token
    access_token = auth.create_access_token(data={"sub": str(user.id)})

    # Step 4: Return token
    return {"access_token": access_token, "token_type": "bearer"}
