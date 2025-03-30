import os
from pydantic_settings import BaseSettings

# Determine which environment file to use
env_file = ".env.test" if os.environ.get("ENV") == "test" else ".env"

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    class Config:
        env_file = env_file

settings = Settings()

def get_settings() -> Settings:
    return settings
