"""
main.py — HOW THIS WORKS:
---------------------------
This is the entry point. It:
1. Creates the FastAPI app instance
2. Configures CORS (so React on port 5173 can talk to FastAPI on port 8000)
3. Creates all DB tables if they don't exist
4. Registers the auth and todo routers

Run with: uvicorn main:app --reload
- "main" = this file (main.py)
- "app" = the FastAPI() instance
- "--reload" = auto-restart when code changes (development mode)

After starting, visit: http://localhost:8000/docs
FastAPI auto-generates interactive Swagger documentation!
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth_routes, todo_routes

# Create all tables defined in models.py
# SQLAlchemy checks if tables exist first — won't overwrite existing data
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo App API",
    description="A full-stack todo app with JWT authentication",
    version="1.0.0"
)

# ─── CORS MIDDLEWARE ────────────────────────────────────────────────
# CORS = Cross-Origin Resource Sharing
# By default, browsers BLOCK requests from one origin (port 5173) to another (port 8000).
# This middleware tells the browser: "it's OK, these origins are allowed."

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server (React)
        "http://localhost:3000",  # Create React App (alternative)
    ],
    allow_credentials=True,   # Allow cookies/auth headers
    allow_methods=["*"],      # Allow all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"],      # Allow all headers (including Authorization for JWT)
)

# ─── REGISTER ROUTERS ───────────────────────────────────────────────
# Include the auth router — all its routes get the /auth prefix
app.include_router(auth_routes.router)

# Include the todo router — all its routes get the /todos prefix
app.include_router(todo_routes.router)


@app.get("/")
def health_check():
    """Quick check that the API is running."""
    return {
        "status": "running",
        "message": "Todo App API is live!",
        "docs": "Visit /docs for interactive API documentation"
    }


# ─── HOW TO RUN ─────────────────────────────────────────────────────
# 1. Create PostgreSQL database: createdb tododb
# 2. Copy .env.example to .env and fill in values
# 3. Install packages: pip install -r requirements.txt
# 4. Start server: uvicorn main:app --reload
# 5. Test at: http://localhost:8000/docs
