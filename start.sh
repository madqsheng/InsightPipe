#!/bin/bash

echo "🚀 Starting InsightPipe..."

# 检查端口占用 - 如果占用直接报错退出
if lsof -i:8817 > /dev/null 2>&1; then
    echo "❌ ERROR: Port 8817 is already in use!"
    echo "   Fix: lsof -ti:8817 | xargs -r kill -9"
    exit 1
fi

if lsof -i:5817 > /dev/null 2>&1; then
    echo "❌ ERROR: Port 5817 is already in use!"
    echo "   Fix: lsof -ti:5817 | xargs -r kill -9"
    exit 1
fi

echo "Starting Backend (FastAPI)..."
cd "$(dirname "$0")"

# 使用追加模式 >> 而不是覆盖模式 >
nohup python3 -m uvicorn server.main:app --host 0.0.0.0 --port 8817 >> server.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid

sleep 1

# 检查后端进程是否还活着
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start!"
    echo "   Last 20 lines of server.log:"
    tail -20 server.log
    exit 1
fi

# 检查端口是否真的在监听
if ! lsof -i:8817 > /dev/null 2>&1; then
    echo "❌ Backend not listening on port 8817!"
    echo "   Last 20 lines of server.log:"
    tail -20 server.log
    exit 1
fi

echo "Starting Frontend (Vue 3)..."
cd web

# 使用追加模式
nohup npm run dev >> ../web.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../.frontend.pid
cd ..

sleep 2

# 检查前端进程是否还活着
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start!"
    echo "   Last 20 lines of web.log:"
    tail -20 web.log
    exit 1
fi

# 检查端口是否真的在监听（必须是5817，不允许自动切换）
if ! lsof -i:5817 > /dev/null 2>&1; then
    echo "❌ Frontend not listening on port 5817!"
    echo "   Last 20 lines of web.log:"
    tail -20 web.log
    exit 1
fi

echo "✅ InsightPipe is running!"
echo "   - Web UI: http://localhost:5817"
echo "   - API:    http://localhost:8817"
echo ""
echo "📝 View logs: tail -f server.log (or web.log)"
echo "💡 Run './stop.sh' to stop everything."
