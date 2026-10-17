#!/usr/bin/env bash
# ==============================================================================
# ZuvoCloud AI Solution - Full Stack Launcher (Backend + React UI)
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

echo -e "${BOLD}${CYAN}====================================================${NC}"
echo -e "${BOLD}${CYAN}   ZuvoCloud Full-Stack Platform Launcher           ${NC}"
echo -e "${BOLD}${CYAN}====================================================${NC}\n"

# 1. Start FastAPI Backend in background
echo -e "${BLUE}--> Starting FastAPI Backend on http://localhost:8000...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Cleanup trap
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    kill $API_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 2. Start Frontend Dev Server
echo -e "${BLUE}--> Starting React Owner Command Center on http://localhost:3000...${NC}"
cd frontend
npm run dev -- --host 0.0.0.0 --port 3000
