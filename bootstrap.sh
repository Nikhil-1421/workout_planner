#!/bin/bash
# Bootstrap script for IronLog development environment
# Usage: ./scripts/bootstrap.sh

set -e

echo "🏋️ IronLog Development Environment Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    echo -e "${RED}Error: Python 3.11+ required. Found $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}Installing runtime dependencies...${NC}"
pip install -r requirements.txt > /dev/null
echo -e "${GREEN}✓ Runtime dependencies installed${NC}"

echo -e "\n${YELLOW}Installing development dependencies...${NC}"
pip install -r requirements-dev.txt > /dev/null
echo -e "${GREEN}✓ Development dependencies installed${NC}"

# Install package in editable mode
echo -e "\n${YELLOW}Installing package in development mode...${NC}"
pip install -e . > /dev/null
echo -e "${GREEN}✓ Package installed${NC}"

# Create app data directory
echo -e "\n${YELLOW}Creating app data directory...${NC}"
mkdir -p ~/.ironlog
echo -e "${GREEN}✓ App data directory created${NC}"

# Run initial tests
echo -e "\n${YELLOW}Running initial tests...${NC}"
if pytest --tb=short -q; then
    echo -e "${GREEN}✓ All tests passed${NC}"
else
    echo -e "${RED}⚠ Some tests failed${NC}"
fi

# Final message
echo -e "\n${GREEN}=========================================="
echo "🎉 Setup complete!"
echo "=========================================="
echo -e "${NC}"
echo "To start developing:"
echo "  source venv/bin/activate"
echo "  ./scripts/run_dev.sh"
echo ""
echo "Other commands:"
echo "  ./scripts/lint.sh   - Run linting"
echo "  ./scripts/test.sh   - Run tests"
echo ""
echo "For iOS build, see README.md 'Mac Handoff' section."
