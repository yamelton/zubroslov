from collections.abc import AsyncGenerator
import os
import re
import logging
from urllib.parse import urlparse, parse_qs
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from passlib.context import CryptContext
import uuid

from .config import settings
from .models.models import User, Base, Progress

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse the DATABASE_URL to extract components
DATABASE_URL = settings.DATABASE_URL
parsed_url = urlparse(DATABASE_URL)

# Handle different database types
if parsed_url.scheme.startswith('postgresql'):
    # Extract components
    db_user = parsed_url.username
    db_password = parsed_url.password
    db_host = parsed_url.hostname
    db_port = parsed_url.port or 5432
    db_name = parsed_url.path.lstrip('/')
    
    # Log connection info (without password)
    logger.info(f"Connecting to PostgreSQL database: {db_host}:{db_port}/{db_name} as {db_user}")
    
    # Construct a clean URL without query parameters
    clean_url = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    # Create engine with appropriate connect_args
    engine = create_async_engine(
        clean_url,
        echo=False,  # Set to True for debugging
        pool_pre_ping=True,  # Check connection before using from pool
    )
elif parsed_url.scheme.startswith('sqlite'):
    # For SQLite, use aiosqlite
    logger.info("Using SQLite database")
    sqlite_url = DATABASE_URL.replace("sqlite:", "sqlite+aiosqlite:")
    engine = create_async_engine(sqlite_url)
else:
    # Default case
    logger.warning(f"Unknown database type: {parsed_url.scheme}")
    engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_test_user(session: AsyncSession):
    try:
        # Try to find the test user by username
        result = await session.execute(select(User).where(User.username == "testuser"))
        test_user = result.scalars().first()

        if not test_user:
            # Create a new test user
            logger.info("Creating new test user")
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
            logger.info("Test user created")
        else:
            # Test user exists, make sure it has all required fields
            logger.info("Test user already exists, checking fields")
            
            # Check if the user has an email field
            try:
                # Try to access the email field
                email = test_user.email
                logger.info(f"Test user email: {email}")
            except Exception as e:
                # If the email field doesn't exist, recreate the user
                if "has no attribute 'email'" in str(e) or "column user.email does not exist" in str(e):
                    logger.warning("Test user missing email field, recreating user")
                    
                    # Delete the existing user
                    await session.delete(test_user)
                    await session.commit()
                    
                    # Create a new user with all required fields
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
                    logger.info("Test user recreated with email field")
                else:
                    # Some other error occurred
                    raise
    except Exception as e:
        logger.error(f"Error in create_test_user: {str(e)}")
        # Don't raise the exception, just log it
        # This allows the application to start even if there are issues with the test user

async def create_db_and_tables():
    from .models.word import Word
    try:
        logger.info("Creating database tables...")
        async with engine.begin() as conn:
            # Check if we're using PostgreSQL
            if parsed_url.scheme.startswith('postgresql'):
                # For PostgreSQL, we need to be careful about creating tables
                # as the schema might already exist and be different
                logger.info("Using PostgreSQL - checking if tables exist before creating")
                try:
                    # Try to create tables, but catch any errors
                    await conn.run_sync(Base.metadata.create_all)
                except Exception as e:
                    logger.warning(f"Error creating tables: {str(e)}")
                    logger.warning("Tables may already exist with a different schema")
                    # Continue without creating tables
            else:
                # For SQLite, we can safely create tables
                await conn.run_sync(Base.metadata.create_all)
        
        # Create test user in both development and production
        logger.info("Creating/checking test user...")
        async with async_session_maker() as session:
            await create_test_user(session)
        
        logger.info("Database initialization complete")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Re-raise the exception to let FastAPI handle it
        raise

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
