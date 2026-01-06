#!/bin/bash
# Run IronLog in development mode
# Usage: ./scripts/run_dev.sh

set -e

echo "🏋️ Starting IronLog in development mode..."

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Run ./scripts/bootstrap.sh first."
        exit 1
    fi
fi

# Check if briefcase is installed
if ! command -v briefcase &> /dev/null; then
    echo "Installing briefcase..."
    pip install briefcase
fi

# Run in development mode
echo "Starting app..."
briefcase dev

# Note: On Linux without a GUI, this will fail.
# For Codespaces, you can still run tests and develop code.
