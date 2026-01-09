# hadiscover DevContainer

This devcontainer provides a complete development environment for hadiscover with:

- **Python 3.12** with backend virtual environment pre-configured
- **Node.js 24** with frontend dependencies pre-installed
- **Docker-in-Docker** for building and testing containers
- **GitHub CLI** for repository management
- **VS Code extensions** for Python, TypeScript, Biome, and more

## 🚀 Getting Started

When you open this repository in the devcontainer:

1. **Automatic setup** runs (via `post-create.sh`):
   - Installs pre-commit hooks
   - Creates Python virtual environment at `backend/venv/`
   - Installs all backend dependencies
   - Installs all frontend dependencies

2. **Frontend auto-starts** (via `post-start.sh`):
   - Next.js dev server starts automatically at <http://localhost:8080>
   - Logs available at `/tmp/frontend-dev.log`

## 📝 Quick Commands

### Convenient Aliases

The devcontainer includes helpful bash aliases:

- `be` - Go to backend directory and activate venv
- `betest` - Run all backend tests
- `berun` - Start backend dev server
- `beindex` - Run indexing CLI command
- `fe` - Go to frontend directory
- `fedev` - Start frontend dev server (manually)
- `febuild` - Build frontend for production
- `ws` - Go to workspace root
- `start` - Start both backend and frontend services
- `stop` - Stop all services
- `precommit` - Run pre-commit checks on all files
- `alltest` - Run all tests (backend + frontend build)
- `logs-frontend` - View frontend dev server logs

### Manual Commands

**Backend:**

```bash
cd backend && source venv/bin/activate
pytest tests/ -v                           # Run tests
python -m uvicorn app.main:app --reload   # Dev server
python -m app.cli index-now                # Index automations
```

**Frontend:**

```bash
cd frontend
npm run dev    # Dev server (already running by default)
npm run build  # Production build
```

**Both:**

```bash
./start.sh  # Start backend + frontend
./stop.sh   # Stop all services
```

## 🔧 Development Workflow

1. **Frontend is already running** at <http://localhost:8080> when you open the devcontainer
2. Start backend if needed: `berun` (or `cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload`)
3. Make changes to code
4. Run tests: `betest` (backend) or `cd frontend && npm run build` (frontend)
5. Before committing: `precommit` to run formatters and linters

## 🧪 Testing

- **Backend tests**: `betest` (runs all 40+ pytest tests)
- **Frontend build**: `cd frontend && npm run build` (verifies TypeScript compiles)
- **Pre-commit checks**: `precommit` (runs Black, isort, Biome, etc.)
- **Docker tests**: Build containers and run CI-style tests

## 🌐 Port Forwarding

The devcontainer automatically forwards:

- **8000**: Backend API (<http://localhost:8000>)
- **8080**: Frontend dev server (<http://localhost:8080>) - auto-opens in browser

## 📦 VS Code Extensions

Pre-installed extensions include:

- **Python**: pylance, black-formatter, isort, ruff
- **Frontend**: ESLint, Prettier, Biome, Tailwind CSS IntelliSense
- **GitHub Copilot**: AI pair programming

## 🔍 Troubleshooting

**Frontend not starting:**

```bash
# Check logs
cat /tmp/frontend-dev.log

# Restart manually
cd frontend && npm run dev
```

**Backend virtual environment issues:**

```bash
# Recreate venv
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Docker permission issues:**

```bash
# Add user to docker group (if needed)
sudo usermod -aG docker $USER
```

## 🎯 Next Steps

- Check [README.md](../README.md) for project overview
- Read [ARCHITECTURE.md](../ARCHITECTURE.md) for technical details
- Review [.github/copilot-instructions.md](../.github/copilot-instructions.md) for development guidelines
