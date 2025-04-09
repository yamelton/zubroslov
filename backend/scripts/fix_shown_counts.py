#!/usr/bin/env python3
"""
Script to fix shown_count values in the WordProgress table.
This corrects the double-counting bug by setting shown_count to the actual number of 'shown' events.

Usage:
    python fix_shown_counts.py [--test]  # Use --test flag for test environment
"""
import asyncio
import sys
import logging
from sqlalchemy import select, func
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

# Import after settings are loaded to ensure correct database connection
from src.database import async_session_maker
from src.models.word import WordProgress, UserWordEvent

async def fix_shown_counts():
    """Fix shown_count values in the WordProgress table."""
    try:
        async with async_session_maker() as session:
            # Get all user-word pairs that have progress records
            query = select(WordProgress.user_id, WordProgress.word_id)
            result = await session.execute(query)
            user_word_pairs = result.all()
            
            count_fixed = 0
            total_records = len(user_word_pairs)
            logger.info(f"Found {total_records} WordProgress records to check")
            
            for user_id, word_id in user_word_pairs:
                # Count actual 'shown' events for this user-word pair
                event_count_query = select(func.count()).where(
                    UserWordEvent.user_id == user_id,
                    UserWordEvent.word_id == word_id,
                    UserWordEvent.event_type == 'shown'
                )
                event_count_result = await session.execute(event_count_query)
                actual_shown_count = event_count_result.scalar() or 0
                
                # Get the current progress record
                progress_query = select(WordProgress).where(
                    WordProgress.user_id == user_id,
                    WordProgress.word_id == word_id
                )
                progress_result = await session.execute(progress_query)
                progress = progress_result.scalar_one_or_none()
                
                if progress and progress.shown_count != actual_shown_count:
                    # Update the shown_count to the correct value
                    old_count = progress.shown_count
                    progress.shown_count = actual_shown_count
                    count_fixed += 1
                    logger.info(f"Fixed user {user_id}, word {word_id}: {old_count} → {actual_shown_count}")
            
            await session.commit()
            logger.info(f"Fixed {count_fixed} out of {total_records} records")
            
            # Additional check for records where shown_count is approximately twice correct_count + error_count
            # This helps identify records that might still be affected by the double-counting bug
            query = select(WordProgress).where(
                WordProgress.shown_count > (WordProgress.correct_count + WordProgress.error_count) * 1.8
            )
            result = await session.execute(query)
            suspicious_records = result.scalars().all()
            
            if suspicious_records:
                logger.warning(f"Found {len(suspicious_records)} suspicious records where shown_count is much higher than correct_count + error_count")
                logger.warning("You may want to manually review these records or run this script again")
                
                for record in suspicious_records[:10]:  # Show first 10 as examples
                    logger.warning(f"User {record.user_id}, Word {record.word_id}: shown={record.shown_count}, correct={record.correct_count}, error={record.error_count}")
            
            return count_fixed
    
    except Exception as e:
        logger.error(f"Error fixing shown_counts: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(fix_shown_counts())
