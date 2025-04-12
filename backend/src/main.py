from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .database import create_db_and_tables
from .routers import words, progress, wordsets
from .auth.router import fastapi_users, auth_backend, current_active_user
from .schemas import UserRead, UserCreate, UserUpdate
from .models.models import User
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables and initial data on startup
    await create_db_and_tables()
    yield

app = FastAPI(title="Zubroslov API", lifespan=lifespan)

# create a static directory to store the static files
static_dir = Path('./static')
static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zubroslov.ru",  # Production frontend
        "https://api.zubroslov.ru",  # Production API
        "https://test.zubroslov.ru",  # Test frontend
        "https://api-test.zubroslov.ru",  # Test API
        "http://localhost:5173",  # Local development
        "http://localhost:3000",  # Alternative local port
        "http://localhost:5174",  # Another local port
        "http://localhost:5175",  # Another local port
        "http://localhost:5176",  # Another local port
        "http://localhost:5177",  # Another local port
        "http://localhost:5178",  # Another local port
        "*",  # Allow all origins (for development only)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/api/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/users",
    tags=["users"],
)

# Other routers
app.include_router(words.router)
app.include_router(progress.router)
app.include_router(wordsets.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Zubroslov API!"}

@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
