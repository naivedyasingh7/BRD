
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo -e "${GREEN}🧞  BRD Genie — Starting...${NC}"

if [ ! -f "$ROOT/.env" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo -e "${YELLOW}⚠️  .env created from example. Add your GROQ_API_KEY before using AI features.${NC}"
fi

if [ ! -f "$ROOT/.venv/bin/python3" ]; then
  echo -e "${YELLOW}📦  Setting up Python venv...${NC}"
  PYTHON=$(command -v python3.13 || command -v python3.12 || command -v python3.11 || command -v python3)
  $PYTHON -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install --upgrade pip -q
  "$ROOT/.venv/bin/pip" install --no-user -r "$ROOT/requirements.txt"
fi

if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo -e "${YELLOW}📦  Installing frontend dependencies...${NC}"
  cd "$ROOT/frontend" && npm install -q
fi

cleanup() {
  echo -e "\n${RED}🛑  Shutting down...${NC}"
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}🚀  Starting backend on http://127.0.0.1:8000${NC}"
cd "$ROOT"
.venv/bin/uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}🚀  Starting frontend on http://localhost:3000${NC}"
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✅  Both servers running. Press Ctrl+C to stop.${NC}"

wait "$BACKEND_PID" "$FRONTEND_PID"
