from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SPEECHKIT_API_KEY: str = None
    SPEECHKIT_API_KEY_ID: str = None

    class Config:
        env_file = ".env"

settings = Settings()

def get_settings() -> Settings:
    return settings
