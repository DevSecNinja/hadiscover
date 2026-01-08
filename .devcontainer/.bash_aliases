#!/bin/bash

# hadiscover development aliases

# Backend shortcuts
alias be='cd /workspaces/hadiscover/backend && source venv/bin/activate'
alias betest='cd /workspaces/hadiscover/backend && source venv/bin/activate && pytest tests/ -v'
alias berun='cd /workspaces/hadiscover/backend && source venv/bin/activate && python -m uvicorn app.main:app --reload'
alias beindex='cd /workspaces/hadiscover/backend && source venv/bin/activate && python -m app.cli index-now'

# Frontend shortcuts
alias fe='cd /workspaces/hadiscover/frontend'
alias fedev='cd /workspaces/hadiscover/frontend && npm run dev'
alias febuild='cd /workspaces/hadiscover/frontend && npm run build'

# Project shortcuts
alias ws='cd /workspaces/hadiscover'
alias start='cd /workspaces/hadiscover && ./start.sh'
alias stop='cd /workspaces/hadiscover && ./stop.sh'

# Testing shortcuts
alias precommit='cd /workspaces/hadiscover && pre-commit run --all-files'
alias alltest='cd /workspaces/hadiscover/backend && source venv/bin/activate && pytest tests/ -v && cd ../frontend && npm run build'

# Logs
alias logs-frontend='tail -f /tmp/frontend-dev.log'

echo "✨ hadiscover aliases loaded!"
echo "💡 Try: be (backend), fe (frontend), betest (run tests), start (start both)"
