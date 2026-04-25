"""Tests for DISABLE_SCHEDULER environment variable configuration."""

import importlib
import os
import sys
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def test_scheduler_disabled():
    """Test that the scheduler is not started when DISABLE_SCHEDULER=true."""
    os.environ["DISABLE_SCHEDULER"] = "true"

    mock_scheduler = MagicMock()
    try:
        # Reload app.main first so it picks up the env var change
        if "app.main" in sys.modules:
            importlib.reload(sys.modules["app.main"])
        else:
            import app.main

        # Patch SchedulerService where it's used (in app.main namespace)
        with patch(
            "app.main.SchedulerService",
            return_value=mock_scheduler,
        ) as mock_cls:
            from app.main import app

            # Use context manager to trigger lifespan
            with TestClient(app) as client:
                # The app should serve requests normally
                response = client.get("/api/v1/health")
                assert response.status_code == 200
                assert response.json() == {"status": "healthy"}

                # SchedulerService should NOT have been instantiated
                mock_cls.assert_not_called()
    finally:
        if "DISABLE_SCHEDULER" in os.environ:
            del os.environ["DISABLE_SCHEDULER"]
        if "app.main" in sys.modules:
            importlib.reload(sys.modules["app.main"])


def test_scheduler_enabled_by_default():
    """Test that the scheduler is started by default."""
    # Ensure DISABLE_SCHEDULER is not set
    if "DISABLE_SCHEDULER" in os.environ:
        del os.environ["DISABLE_SCHEDULER"]

    mock_scheduler = MagicMock()
    try:
        # Reload app.main first so it picks up the env var change
        if "app.main" in sys.modules:
            importlib.reload(sys.modules["app.main"])
        else:
            import app.main

        # Patch SchedulerService where it's used (in app.main namespace)
        with patch(
            "app.main.SchedulerService",
            return_value=mock_scheduler,
        ) as mock_cls:
            from app.main import app

            # Use context manager to trigger lifespan
            with TestClient(app) as client:
                response = client.get("/api/v1/health")
                assert response.status_code == 200

                # SchedulerService SHOULD have been started
                mock_cls.assert_called_once()
                mock_scheduler.start.assert_called_once()
    finally:
        if "app.main" in sys.modules:
            importlib.reload(sys.modules["app.main"])
