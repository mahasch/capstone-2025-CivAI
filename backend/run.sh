#!/bin/bash

set -e

echo "🚀 Starting Capstone Backend..."

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Install Node dependencies
echo -e "${BLUE}📦 Installing Node dependencies...${NC}"
if [ ! -d "node_modules" ]; then
  npm install
else
  echo "Node dependencies already installed"
fi

# 2. Python venv
echo -e "${BLUE}🐍 Setting up Python environment...${NC}"
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python -m venv venv
fi

# Detect OS and activate venv
if [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "msys" ]] || [[ -d "venv/Scripts" ]]; then
  # Windows (Git Bash, PowerShell, CMD)
  source venv/Scripts/activate
else
  # macOS/Linux
  source venv/bin/activate
fi

# 3. Install Python dependencies
echo -e "${BLUE}📚 Installing Python dependencies...${NC}"
python -m pip install -r agent/requirements.txt

# 4. Start
echo -e "${GREEN}✅ Starting Node server on port 3000${NC}"
echo ""

npm start