#!/bin/bash
# Lint IronLog codebase
# Usage: ./scripts/lint.sh

set -e

echo "🔍 Linting IronLog..."

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

EXIT_CODE=0

# Run ruff check
echo -e "\n${YELLOW}Running ruff check...${NC}"
if ruff check app/ tests/; then
    echo -e "${GREEN}✓ ruff check passed${NC}"
else
    echo -e "${RED}✗ ruff check found issues${NC}"
    EXIT_CODE=1
fi

# Run ruff format check
echo -e "\n${YELLOW}Checking formatting with ruff...${NC}"
if ruff format --check app/ tests/; then
    echo -e "${GREEN}✓ ruff format check passed${NC}"
else
    echo -e "${RED}✗ Code needs formatting. Run: ruff format app/ tests/${NC}"
    EXIT_CODE=1
fi

# Run mypy
echo -e "\n${YELLOW}Running mypy type check...${NC}"
if mypy app/ --ignore-missing-imports; then
    echo -e "${GREEN}✓ mypy check passed${NC}"
else
    echo -e "${RED}✗ mypy found type issues${NC}"
    EXIT_CODE=1
fi

# Summary
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}=========================================="
    echo "✅ All checks passed!"
    echo -e "==========================================${NC}"
else
    echo -e "${RED}=========================================="
    echo "❌ Some checks failed"
    echo -e "==========================================${NC}"
fi

exit $EXIT_CODE
