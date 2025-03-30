import os
from pydantic_settings import BaseSettings

# Get the current environment
ENV = os.environ.get("ENV", "prod")

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    ENV: str = ENV  # Store the environment

    class Config:
        env_file = ".env"

settings = Settings()

def get_settings() -> Settings:
    return settings
