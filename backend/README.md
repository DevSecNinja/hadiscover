# hadiscover Backend

This is the backend indexing and local API tooling for hadiscover, built with FastAPI.

## 🚀 Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- **API Docs**: <http://localhost:8000/docs>
- **Health Check**: <http://localhost:8000/api/v1/health>

### Running Tests

```bash
pytest tests/ -v
```

## 🌐 Deployment

The public production site does not run a backend container. Indexing for production is handled by the repository's `Update Database` GitHub Action, which exports static frontend search data and publishes archival SQLite assets to GitHub releases.

### Running Modes

#### Web Server Mode (Default)

```bash
docker run -p 8000:8000 hadiscover-backend
```

To run with the release-hosted database:

```bash
docker run \
 -e DB_DOWNLOAD_URL=https://github.com/DevSecNinja/hadiscover/releases/download/db-latest/hadiscover.db.gz \
 -e DB_BOOTSTRAP_REQUIRED=true \
 -e DISABLE_SCHEDULER=true \
 -p 8000:8000 \
 hadiscover-backend
```

or using the entrypoint:

```bash
docker run -p 8000:8000 hadiscover-backend
```

#### Indexing Job Mode

For running as a one-time indexing job, including the GitHub Actions database build:

```bash
docker run hadiscover-backend index-now
```

This will:

1. Initialize the database
2. Run the indexing process once
3. Exit with code 0 on success or 1 on failure

This mode is used by `.github/workflows/update-db.yml` to create `hadiscover.db` before exporting static frontend search data.

#### Static Export Mode

After indexing, export browser-consumable search data:

```bash
python -m app.cli export-static ../frontend/public/data/search-index.json
```

### Quick Deploy Options

- **GitHub Actions**: Production indexing and static data export
- **Docker**: Local/development API tooling with flexible entrypoint
- **Container App Job**: Can be run with `index-now` argument

### Configuration Files

- `Dockerfile` - Docker container configuration
- `entrypoint.sh` - Entrypoint script supporting multiple run modes

## 🔧 Configuration

### Environment Variables

- `GITHUB_TOKEN` (optional): GitHub Personal Access Token for higher API rate limits when indexing
- `ENVIRONMENT` (optional): Set to `development` to enable the manual `/index` endpoint trigger. Defaults to `production` which disables the endpoint. In production, use the `index-now` command for scheduled indexing.
- `ROOT_PATH` (optional): Base path for the API when deployed behind a reverse proxy or on cloud platforms (e.g., Azure Container Apps). Leave empty for default behavior.
- `DATABASE_URL` (optional): Database connection URL. Defaults to `sqlite:///./data/hadiscover.db`
- `DB_DOWNLOAD_URL` (optional): URL of a gzip-compressed SQLite database release asset to install on startup
- `DB_BOOTSTRAP_REQUIRED` (optional): Set to `true` to fail startup if `DB_DOWNLOAD_URL` cannot be installed
- `DISABLE_SCHEDULER` (optional): Set to `true` when the database is built externally by GitHub Actions

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your GitHub token and other configuration
```

#### Deployment-Specific Configuration

**Azure Container Apps / Cloud Platforms:**

If you're deploying to Azure Container Apps or similar platforms where the application is accessed without the `/api/v1` prefix in the URL, you can set:

```bash
ROOT_PATH=/api/v1
```

This configures FastAPI to properly handle requests when the platform's routing layer strips or doesn't include the `/api/v1` prefix. Your application will then be accessible at the root URL (e.g., `https://your-app.azurecontainerapps.io/`) while maintaining the correct API path structure internally.

## 📚 API Endpoints

- `GET /api/v1/search?q={query}` - Search automations
- `GET /api/v1/statistics` - Get indexing statistics
- `POST /api/v1/index` - Trigger repository indexing (development only)
- `GET /api/v1/health` - Health check

## 🔄 Indexing

### Development Mode

In development, you can manually trigger indexing via the API:

```bash
curl -X POST http://localhost:8000/api/v1/index
```

### Production Mode

In production, the `/index` endpoint is disabled for security. The recommended flow is:

1. `.github/workflows/update-db.yml` runs `python -m app.cli index-now`
2. The workflow exports `frontend/public/data/search-index.json`
3. The workflow builds and deploys the static frontend to GitHub Pages
4. The workflow publishes `search-index.json` and `hadiscover.db.gz` to the `db-latest` GitHub release and a dated snapshot release

You can still run the container CLI manually to build a database:

```bash
# Run as a one-time job
docker run hadiscover-backend index-now

# Or exec into a running container (short form)
docker exec -it <container-id> index-now

# Or exec into a running container (long form)
docker exec -it <container-id> python -m app.cli index-now
```

Self-hosted deployments can still use Azure Container App Jobs, Kubernetes CronJobs, or any scheduled job platform instead of the GitHub Actions workflow.

## 🛠️ Project Structure

```text
backend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── cli.py            # CLI commands for batch operations
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   │   ├── database_bootstrap.py
│   │   ├── github_service.py
│   │   ├── parser.py
│   │   ├── indexer.py
│   │   └── search_service.py
│   └── api/
│       └── routes.py     # API endpoints
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── entrypoint.sh        # Container entrypoint script

```

## 🔒 CORS Configuration

The local/development API is configured to accept requests from:

- `http://localhost:8080` (local frontend)
- `http://127.0.0.1:8080` (local frontend)
- `https://hadiscover.com` (production frontend)
- `https://www.hadiscover.com` (production frontend)

If you fork the repository, update the CORS origins in `app/main.py`.

## 📖 Documentation

- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [README.md](../README.md) - Project overview

## 🐛 Troubleshooting

### Database Issues

The app uses SQLite with the database stored in `data/hadiscover.db`. If you encounter database issues:

```bash
# Remove the database and restart
rm -rf data/
python -m uvicorn app.main:app --reload
```

### GitHub API Rate Limits

Without a token, GitHub limits you to 60 requests per hour. Add a `GITHUB_TOKEN` to increase this to 5,000 requests per hour.

### CORS Errors

If the local development frontend can't connect to the API, ensure:

1. The backend is running and accessible
2. The CORS origins include your frontend URL
3. `NEXT_PUBLIC_API_URL` is set when using the local dev re-index button

## 📝 License

MIT License - see [LICENSE](../LICENSE) for details
