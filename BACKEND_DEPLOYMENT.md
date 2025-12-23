# Backend Deployment Guide

This guide explains how to deploy the HA Discover backend API to various hosting platforms. The backend is a Python FastAPI application that requires a persistent runtime environment (not GitHub Pages).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start Options](#quick-start-options)
3. [Railway Deployment](#railway-deployment-recommended)
4. [Render Deployment](#render-deployment)
5. [Heroku Deployment](#heroku-deployment)
6. [Vercel Deployment](#vercel-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Configuring the Frontend](#configuring-the-frontend)

## Prerequisites

- A GitHub account
- Backend code in the `backend/` directory
- Optional: GitHub Personal Access Token (for higher API rate limits)

## Quick Start Options

For free, zero-config deployment, we recommend:

- **Railway** - Free tier, auto-deploys from GitHub
- **Render** - Free tier, simple configuration
- **Vercel** - Serverless, free tier available

## Railway Deployment (Recommended)

Railway offers a generous free tier and automatic deployments from GitHub.

### Steps

1. **Sign up at [Railway](https://railway.app/)**
   - Use your GitHub account for authentication

2. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose the `DevSecNinja/ha-discover` repository

3. **Configure the service**
   - Railway will auto-detect the `railway.toml` configuration
   - Set the root directory to `backend`
   - Add environment variables (optional):
     - `GITHUB_TOKEN`: Your GitHub Personal Access Token (for higher rate limits)

4. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a URL like: `https://ha-discover-api-production.up.railway.app`

5. **Configure custom domain (optional)**
   - Go to Settings → Networking
   - Add a custom domain if desired

### Configuration File

The repository includes `backend/railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

## Render Deployment

Render provides a free tier with persistent instances.

### Steps

1. **Sign up at [Render](https://render.com/)**

2. **Create a new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service**
   - **Name**: `ha-discover-api`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Set environment variables**
   - `PYTHON_VERSION`: `3.12.0`
   - `GITHUB_TOKEN`: (optional) Your GitHub token

5. **Create Web Service**
   - Render will deploy and give you a URL like: `https://ha-discover-api.onrender.com`

### Configuration File

The repository includes `backend/render.yaml` for automated setup:

```yaml
services:
  - type: web
    name: ha-discover-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
    healthCheckPath: /api/v1/health
```

You can use the "Deploy to Render" button by adding this to your README:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Heroku Deployment

Heroku is a well-established platform with a free tier.

### Steps

1. **Install the Heroku CLI**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Or download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**
   ```bash
   cd backend
   heroku create ha-discover-api
   ```

4. **Set environment variables**
   ```bash
   heroku config:set GITHUB_TOKEN=your_token_here
   ```

5. **Deploy**
   ```bash
   git subtree push --prefix backend heroku main
   # Or if deploying from the backend directory:
   git push heroku main
   ```

6. **Your API will be available at**: `https://ha-discover-api.herokuapp.com`

### Configuration Files

The repository includes:
- `backend/Procfile`: Process configuration
- `backend/runtime.txt`: Python version specification

## Vercel Deployment

Vercel supports Python serverless functions.

### Steps

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy from backend directory**
   ```bash
   cd backend
   vercel
   ```

3. **Follow the prompts**
   - Link to your Vercel account
   - Configure the project

4. **Your API will be available at**: `https://ha-discover-api.vercel.app`

**Note**: Vercel's serverless model may have cold start delays. For a persistent API, Railway or Render are recommended.

## Docker Deployment

For self-hosting or cloud deployment (AWS, GCP, Azure), use Docker.

### Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run

```bash
# Build image
docker build -t ha-discover-api backend/

# Run container
docker run -p 8000:8000 -e GITHUB_TOKEN=your_token ha-discover-api
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
    volumes:
      - ./backend/data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Configuring the Frontend

After deploying your backend, you need to configure the frontend to use the correct API URL.

### Option 1: GitHub Actions Workflow (Recommended)

1. **Get your backend URL** from your deployment (e.g., `https://ha-discover-api.onrender.com`)

2. **Update `.github/workflows/deploy.yml`**:
   ```yaml
   - name: Build with Next.js
     working-directory: ./frontend
     run: npm run build
     env:
       NEXT_PUBLIC_API_URL: https://your-backend-url.com/api/v1
   ```

3. **Push to trigger deployment**:
   ```bash
   git add .github/workflows/deploy.yml
   git commit -m "Configure backend API URL"
   git push
   ```

### Option 2: GitHub Secrets (More Secure)

1. **Go to your repository Settings → Secrets and variables → Actions**

2. **Add a new secret**:
   - **Name**: `API_URL`
   - **Value**: `https://your-backend-url.com/api/v1`

3. **Update `.github/workflows/deploy.yml`**:
   ```yaml
   - name: Build with Next.js
     working-directory: ./frontend
     run: npm run build
     env:
       NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
   ```

4. **Push changes and the workflow will use the secret**

### Option 3: Environment Variable (Development)

For local development:

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=https://your-backend-url.com/api/v1" > .env.local
npm run dev
```

## Verifying the Deployment

1. **Check backend health**:
   ```bash
   curl https://your-backend-url.com/api/v1/health
   ```

   Should return:
   ```json
   {"status": "ok"}
   ```

2. **Test API documentation**:
   - Visit: `https://your-backend-url.com/docs`
   - You should see the interactive Swagger UI

3. **Trigger frontend rebuild**:
   - After configuring the API URL, push to `main` branch
   - GitHub Actions will rebuild and deploy the frontend

4. **Access your site**:
   - Visit: `https://devsecninja.github.io/ha-discover/`
   - The frontend should now connect to your backend

## CORS Configuration

The backend is pre-configured to accept requests from:
- `http://localhost:3000` (local development)
- `http://127.0.0.1:3000` (local development)
- `https://devsecninja.github.io` (production frontend)

If you fork this repository or deploy to a different domain, update the CORS origins in `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://your-custom-domain.com"  # Add your domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Monitoring and Logs

- **Railway**: Check logs in the Railway dashboard
- **Render**: View logs in the Render dashboard under "Logs"
- **Heroku**: Use `heroku logs --tail` to view logs
- **Docker**: Use `docker logs -f container-name`

## Troubleshooting

### Backend doesn't start
- Check that Python version is 3.12+
- Verify all dependencies are installed
- Check logs for specific error messages

### Frontend can't connect to backend
- Verify the API URL is correct in the workflow
- Check CORS configuration includes your frontend domain
- Ensure backend is accessible (not behind a firewall)
- Test backend health endpoint directly

### Rate limiting issues
- Add a GitHub Personal Access Token to increase API limits
- Set `GITHUB_TOKEN` environment variable in your deployment

## Cost Considerations

All platforms offer free tiers suitable for this project:

- **Railway**: 500 hours/month free (enough for continuous operation)
- **Render**: 750 hours/month free
- **Heroku**: 1000 dyno hours/month free
- **Vercel**: Generous free tier for hobby projects

The HA Discover API is lightweight and should run comfortably within free tier limits.

## Next Steps

1. Deploy backend to your chosen platform
2. Get the backend URL
3. Configure the frontend workflow with the API URL
4. Push to trigger frontend deployment
5. Visit `https://devsecninja.github.io/ha-discover/` to use your app!

For questions or issues, please open an issue on GitHub.
