#!/bin/bash
# Run IronLog tests
# Usage: ./scripts/test.sh [pytest args]

set -e

echo "🧪 Running IronLog tests..."

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
fi

# Run pytest with any additional arguments
pytest "$@"
