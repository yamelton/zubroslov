from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import create_db_and_tables
from .routers import auth, words, progress
from .config import settings

app = FastAPI(title="Zubroslov API")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
