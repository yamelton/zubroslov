#!/bin/bash
# Script to import words to PostgreSQL database
# Run this script after the PostgreSQL connection is working

set -e  # Exit on error

echo "Importing words to PostgreSQL database..."
docker exec zubroslov-api python /app/scripts/import_words.py

echo "Words import complete!"
