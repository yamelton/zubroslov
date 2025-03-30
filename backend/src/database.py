from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from passlib.context import CryptContext
import uuid

from .config import settings
from .models.models import User, Base, Progress

# Convert SQLite URL to async version if needed
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("sqlite:"):
    DATABASE_URL = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
elif DATABASE_URL.startswith("postgresql:"):
    # Remove SSL parameters from the URL
    import re
    DATABASE_URL = DATABASE_URL.replace("postgresql:", "postgresql+asyncpg:")
    DATABASE_URL = re.sub(r"\?sslmode=\w+", "", DATABASE_URL)

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_test_user(session: AsyncSession):
    result = await session.execute(select(User).where(User.username == "testuser"))
    test_user = result.scalars().first()

    if not test_user:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        new_user = User(
            email="testuser@example.com",
            username="testuser",
            hashed_password=pwd_context.hash("testpass"),
            is_active=True,
            is_verified=True,
            is_superuser=False
        )
        session.add(new_user)
        await session.commit()
        print("Test user created")
    else:
        print("Test user already exists")

async def create_db_and_tables():
    from .models.word import Word
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session_maker() as session:
        await create_test_user(session)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
