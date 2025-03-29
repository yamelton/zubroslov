from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .database import create_db_and_tables
from .routers import auth, words, progress
from .config import settings

app = FastAPI(title="Zubroslov API")

# create a static directory to store the static files
static_dir = Path('./static')
static_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zubroslov.ru",  # Production
        "http://localhost:5173",  # Local development
        "http://localhost:3000"   # Alternative local port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Подключение роутеров
app.include_router(auth.router)
app.include_router(words.router)
app.include_router(progress.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Zubroslov API!"}
