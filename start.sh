#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo -e "${GREEN}🧞  BRD Genie — Starting...${NC}"

# Check .env
if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo -e "${YELLOW}⚠️  .env created from example. Add your GROQ_API_KEY before using AI features.${NC}"
fi

# Check venv
if [ ! -f "$ROOT/.venv/bin/uvicorn" ]; then
  echo -e "${YELLOW}📦  Setting up Python venv...${NC}"
  python3.11 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install -r "$ROOT/requirements.txt" -q
fi

# Check node_modules
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo -e "${YELLOW}📦  Installing frontend dependencies...${NC}"
  cd "$ROOT/frontend" && npm install -q
fi

# Trap Ctrl+C to kill both servers
cleanup() {
  echo -e "\n${RED}🛑  Shutting down...${NC}"
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo -e "${GREEN}🚀  Starting backend on http://127.0.0.1:8000${NC}"
cd "$ROOT"
.venv/bin/uvicorn backend.main:app --port 8000 &
BACKEND_PID=$!

# Start frontend
echo -e "${GREEN}🚀  Starting frontend on http://localhost:3000${NC}"
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✅  Both servers running. Press Ctrl+C to stop.${NC}"

# Wait for both
wait "$BACKEND_PID" "$FRONTEND_PID"
