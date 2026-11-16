#!/bin/bash

echo "🌐 Starting frontend dev server..."

# Start frontend dev server in background
cd /workspaces/hadiscover/frontend || exit
nohup npm run dev >/tmp/frontend-dev.log 2>&1 &

# Wait a moment for server to start
sleep 3

if pgrep -f "next dev" >/dev/null; then
    echo "✅ Frontend dev server started at http://localhost:8080"
    echo "📋 View logs: tail -f /tmp/frontend-dev.log"
else
    echo "⚠️  Frontend dev server failed to start. Check logs: cat /tmp/frontend-dev.log"
fi

echo ""
echo "🎉 Ready to develop! The frontend is already running."
echo "💡 To start the backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo ""
