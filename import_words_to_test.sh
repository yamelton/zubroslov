#!/bin/bash
# Script to import words to test database
# Run this script after the test environment is running

set -e  # Exit on error

# Директория проекта
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Prepare arguments for the common script
ARGS="--container zubroslov-api-test --env test"

# Pass through any arguments to the common script
while [[ $# -gt 0 ]]; do
  ARGS="$ARGS $1 $2"
  shift 2
done

# Call the common script
./import_words_common.sh $ARGS
