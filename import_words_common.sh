#!/bin/bash
# Common script for importing words to databases
# This script is used by import_words_to_postgres.sh and import_words_to_test.sh

# Parse command line arguments
WORDSET=""
FILE=""
CONTAINER=""
ENV=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --wordset)
      WORDSET="$2"
      shift 2
      ;;
    --file)
      FILE="$2"
      shift 2
      ;;
    --container)
      CONTAINER="$2"
      shift 2
      ;;
    --env)
      ENV="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 --container CONTAINER_NAME [--wordset WORDSET_NAME] [--file FILE_PATH] [--env ENV_NAME]"
      exit 1
      ;;
  esac
done

# Check if container is specified
if [ -z "$CONTAINER" ]; then
  echo "Error: Container name must be specified with --container"
  exit 1
fi

# Check if container is running
if ! docker ps | grep -q $CONTAINER; then
  echo "Error: Container $CONTAINER is not running."
  exit 1
fi

# Build the command
CMD="python"
if [ -n "$ENV" ]; then
  CMD="$CMD -m scripts.import_words --env $ENV"
else
  CMD="$CMD /app/scripts/import_words.py"
fi

if [ -n "$WORDSET" ]; then
  CMD="$CMD --wordset \"$WORDSET\""
fi

if [ -n "$FILE" ]; then
  CMD="$CMD --file \"$FILE\""
fi

echo "Importing words to database..."
echo "Command: $CMD"
docker exec $CONTAINER bash -c "$CMD"

echo "Import complete!"
