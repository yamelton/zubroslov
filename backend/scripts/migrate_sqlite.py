#!/usr/bin/env python3
"""
Migration script to add new columns for the smart word selection algorithm to SQLite database.
This script adds:
- words_shown_counter to the user table
- last_shown_position and exp_error_rate to the wordprogress table

Usage:
    python migrate_sqlite.py <database_path>
"""
import sys
import logging
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_sqlite(db_path):
    """Add the new columns to the SQLite database tables."""
    try:
        # Connect to the SQLite database
        logger.info(f"Connecting to SQLite database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if words_shown_counter column exists in user table
        logger.info("Checking user table schema...")
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'words_shown_counter' not in columns:
            logger.info("Adding words_shown_counter column to user table")
            cursor.execute('ALTER TABLE "user" ADD COLUMN words_shown_counter INTEGER DEFAULT 0')
            logger.info("words_shown_counter column added successfully")
        else:
            logger.info("words_shown_counter column already exists")
        
        # Check if last_shown_position column exists in wordprogress table
        logger.info("Checking wordprogress table schema...")
        cursor.execute("PRAGMA table_info(wordprogress)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'last_shown_position' not in columns:
            logger.info("Adding last_shown_position column to wordprogress table")
            cursor.execute('ALTER TABLE wordprogress ADD COLUMN last_shown_position INTEGER DEFAULT 0')
            logger.info("last_shown_position column added successfully")
        else:
            logger.info("last_shown_position column already exists")
        
        if 'exp_error_rate' not in columns:
            logger.info("Adding exp_error_rate column to wordprogress table")
            cursor.execute('ALTER TABLE wordprogress ADD COLUMN exp_error_rate FLOAT DEFAULT 0.5')
            logger.info("exp_error_rate column added successfully")
        else:
            logger.info("exp_error_rate column already exists")
        
        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
        logger.info("Migration completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_sqlite.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    success = migrate_sqlite(db_path)
    sys.exit(0 if success else 1)
