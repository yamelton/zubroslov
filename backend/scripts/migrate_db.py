#!/usr/bin/env python3
"""
Migration script to add new columns for the smart word selection algorithm.
This script adds:
- words_shown_counter to the user table
- last_shown_position and exp_error_rate to the wordprogress table

Usage:
    python migrate_db.py [--test]  # Use --test flag for test environment
"""
import asyncio
import os
import sys
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from pydantic_settings import BaseSettings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine environment
is_test = len(sys.argv) > 1 and sys.argv[1] == "--test"
env = "test" if is_test else "prod"
logger.info(f"Using {env.upper()} environment")

# Load settings from appropriate .env file
class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env.test" if is_test else ".env"

settings = Settings()
logger.info(f"Using database from {settings.Config.env_file}")

# Convert to async URL for SQLAlchemy
if settings.DATABASE_URL.startswith('postgresql'):
    ASYNC_DATABASE_URL = settings.DATABASE_URL.replace('postgresql', 'postgresql+asyncpg')
else:
    ASYNC_DATABASE_URL = settings.DATABASE_URL
    logger.warning(f"Non-PostgreSQL database URL detected")

async def add_columns():
    """Add the new columns to the database tables."""
    try:
        # Create async engine
        engine = create_async_engine(ASYNC_DATABASE_URL)
        
        async with engine.begin() as conn:
            # Check if words_shown_counter column exists in user table
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name = 'words_shown_counter'
            """))
            if result.fetchone() is None:
                logger.info("Adding words_shown_counter column to user table")
                await conn.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN words_shown_counter INTEGER DEFAULT 0
                """))
                logger.info("words_shown_counter column added successfully")
            else:
                logger.info("words_shown_counter column already exists")
            
            # Check if last_shown_position column exists in wordprogress table
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'wordprogress' 
                AND column_name = 'last_shown_position'
            """))
            if result.fetchone() is None:
                logger.info("Adding last_shown_position column to wordprogress table")
                await conn.execute(text("""
                    ALTER TABLE wordprogress 
                    ADD COLUMN last_shown_position INTEGER DEFAULT 0
                """))
                logger.info("last_shown_position column added successfully")
            else:
                logger.info("last_shown_position column already exists")
            
            # Check if exp_error_rate column exists in wordprogress table
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'wordprogress' 
                AND column_name = 'exp_error_rate'
            """))
            if result.fetchone() is None:
                logger.info("Adding exp_error_rate column to wordprogress table")
                await conn.execute(text("""
                    ALTER TABLE wordprogress 
                    ADD COLUMN exp_error_rate FLOAT DEFAULT 0.5
                """))
                logger.info("exp_error_rate column added successfully")
            else:
                logger.info("exp_error_rate column already exists")
        
        logger.info("Migration completed successfully")
    
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(add_columns())
