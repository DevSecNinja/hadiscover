# hadiscover

[![Release](https://github.com/DevSecNinja/hadiscover/actions/workflows/release.yml/badge.svg)](https://github.com/DevSecNinja/hadiscover/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/DevSecNinja/hadiscover/graph/badge.svg?token=4V189H55CG)](https://codecov.io/gh/DevSecNinja/hadiscover)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)](https://github.com/DevSecNinja?tab=packages&repo_name=hadiscover)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-green.svg?logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)](https://nextjs.org/)

A search engine for discovering Home Assistant automations shared on GitHub.

[Try it now at hadiscover.com](https://hadiscover.com/)

[![Screenshot of hadiscover.com web page in dark mode](frontend/assets/screenshot-dark.png)](https://hadiscover.com/)

## What is it?

hadiscover is a search engine for discovering Home Assistant automations shared on GitHub. It indexes `automations.yaml` files from repositories that opt in by adding the `hadiscover` topic, making it easy to find real-world automation examples and explore new integration possibilities.

## Why use it?

- **Discover integrations**: Find new domains and services to use in your automations (e.g., media_player, climate, notify)
- **Filter by triggers**: Browse automations by trigger type (state, time, webhook, zone, etc.)
- **Find examples**: See how others implement automations for specific use cases
- **Opt-in only**: Privacy-focused—your repos are only indexed if you add the `hadiscover` topic

## Features

- **Multi-filter search**: Filter by repositories, trigger types, action domains (integrations), and specific service calls
- **Full-text search**: Search across automation names, descriptions, triggers, actions, and repositories
- **Integration discovery**: Browse by action domains to find automations using specific integrations
- **Direct GitHub links**: Jump to exact line numbers in source files

## Adding Your Repository

To have your automations indexed:

1. Ensure your repository has an `automations.yaml` file
2. Add the `hadiscover` topic to your GitHub repository:
   - Go to your repository on GitHub
   - Click the ⚙️ icon next to "About"
   - Add `hadiscover` to the topics list
   - Save changes
3. Wait for the next hourly indexing (or trigger manually in development mode)

---

## Development

### Prerequisites

- Python 3.12+, pip, venv
- Node.js 24+, npm
- Optional: GitHub Personal Access Token (for 5k/hr rate limit vs 60/hr)

### Quick Setup

```bash
git clone https://github.com/DevSecNinja/hadiscover.git
cd hadiscover

# Automated setup (installs backend and frontend dependencies)
./setup.sh

# Start both backend and frontend
./start.sh
```

Access the app:

- **Frontend**: <http://localhost:8080>
- **Backend API**: <http://localhost:8000>
- **API Docs**: <http://localhost:8000/docs>

Stop services:

```bash
./stop.sh
```

### Manual Setup

If you prefer manual setup or the scripts don't work:

**Backend:**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Frontend (new terminal):**

```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
# Pre-built images from GHCR
docker-compose -f docker-compose.prod.yml up -d

# Or build locally
docker-compose up -d
```

### Testing

Run backend tests:

```bash
cd backend && source venv/bin/activate && pytest tests/ -v
```

CI automatically tests Docker containers, API endpoints, and integration on every PR.

### API Documentation

OpenAPI/Swagger docs available at <http://localhost:8000/docs> once running.

**Key Endpoints:**

- `GET /api/v1/search?q={query}` - Search automations (with filters for repo, blueprint, trigger)
- `GET /api/v1/statistics` - Get totals and last indexed time
- `POST /api/v1/index` - Trigger indexing (dev mode only, rate limited)
- `GET /api/v1/health` - Health check

## More Information

- **Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
- **Contributing**: PRs welcome! Open an issue for bugs or feature requests.
- **License**: MIT License
- **Stack**: FastAPI (Python), Next.js (TypeScript), SQLite
- **Inspired by**: [kubesearch.dev](https://kubesearch.dev)

---

⭐ Star the repo if you find it useful | 🐛 Report bugs via GitHub Issues | 📢 Share with the Home Assistant community
