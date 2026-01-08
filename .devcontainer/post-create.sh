#!/bin/bash
set -e

echo "🚀 Setting up hadiscover development environment..."

# Setup bash aliases symlink
echo "🔗 Setting up bash aliases..."
ln -sf /workspaces/hadiscover/.devcontainer/.bash_aliases ~/.bash_aliases
echo "✅ Bash aliases configured!"

# Install pre-commit hooks
echo "📦 Installing pre-commit..."
pip install pre-commit
pre-commit install

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
python3 -m venv venv

# Activate and install dependencies
# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete!"

# Setup frontend
echo "⚛️  Setting up Next.js frontend..."
cd ../frontend
npm install

# Create .env.local for devcontainer
if [ -n "$CODESPACE_NAME" ]; then
	# GitHub Codespaces
	CODESPACE_URL="https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
	echo "📝 Creating .env.local with Codespace URL..."
	echo "NEXT_PUBLIC_API_URL=${CODESPACE_URL}/api/v1" >.env.local
	echo "✅ .env.local created with Codespace URL: ${CODESPACE_URL}/api/v1"
else
	# Local devcontainer or other environment
	echo "📝 Creating .env.local for local development..."
	echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" >.env.local
	echo "✅ .env.local created with local URL"
fi

echo "✅ Frontend setup complete!"

# Return to workspace root
cd ..

echo ""
echo "✨ Development environment ready!"
echo ""
echo "📝 Quick commands:"
echo "  Backend tests:  cd backend && source venv/bin/activate && pytest tests/ -v"
echo "  Backend dev:    cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "  Frontend dev:   cd frontend && npm run dev (auto-starts on container start)"
echo "  Frontend build: cd frontend && npm run build"
echo "  Both services:  ./start.sh"
echo "  Stop services:  ./stop.sh"
echo ""
