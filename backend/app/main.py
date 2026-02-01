"""Main FastAPI application for hadiscover."""

import logging
import os
from contextlib import asynccontextmanager

from app.api.routes import router
from app.models import init_db
from app.services.scheduler import SchedulerService
from app.version import __version__
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Get root_path from environment variable
# This allows the app to work correctly behind reverse proxies or when deployed
# to cloud platforms with different base paths (e.g., Azure Container Apps)
root_path = os.getenv("ROOT_PATH", "")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response."""
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    init_db()
    logging.info("Database initialized")

    # Start the scheduler for hourly indexing
    scheduler_service = SchedulerService()
    scheduler_service.start()
    logging.info("Scheduler initialized - hourly indexing enabled")

    yield

    # Shutdown
    scheduler_service.shutdown()
    logging.info("Scheduler shut down")


# Create FastAPI app
app = FastAPI(
    title="hadiscover API",
    description="Search engine for Home Assistant automations from GitHub",
    version=__version__,
    root_path=root_path,
    lifespan=lifespan,
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://hadiscover.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Determine the API route prefix based on root_path configuration
# If root_path is already set to /api/v1, don't add it again to routes
# This allows the app to work correctly when deployed behind reverse proxies
api_prefix = "" if root_path else "/api/v1"

# Include API routes
app.include_router(router, prefix=api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "hadiscover API", "version": __version__, "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)  # nosec B104
