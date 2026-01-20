#!/bin/bash
# stop.sh - Stop InsightPipe processes

echo "🛑 Stopping InsightPipe..."

# Kill Backend
if pkill -f "uvicorn server.main:app"; then
    echo "✅ Backend stopped."
else
    echo "⚠️  Backend not found or already stopped."
fi

# Kill Frontend
if pkill -f "vite"; then
    echo "✅ Frontend stopped."
else
    echo "⚠️  Frontend not found or already stopped."
fi

echo "👋 Bye!"
