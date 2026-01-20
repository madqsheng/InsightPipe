#!/bin/bash
# start.sh - Start both Backend and Frontend

# Kill existing processes just in case
pkill -f "uvicorn server.main:app"
pkill -f "vite --host"

echo "🚀 Starting InsightPipe..."

# Start Backend
echo "Starting Backend (FastAPI)..."
nohup python -m uvicorn server.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
BACKEND_PID=$!

# Start Frontend
echo "Starting Frontend (Vue 3)..."
cd web
nohup npm run dev -- --host > ../web.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "✅ InsightPipe is running!"
echo "   - Web UI: http://localhost:5173"
echo "   - API:    http://localhost:8000"
echo ""
echo "📝 Logs are being written to server.log and web.log"
echo "💡 Run './stop.sh' to stop everything."
