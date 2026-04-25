"""Tests for DISABLE_SCHEDULER environment variable configuration."""

from unittest.mock import MagicMock, patch

import app.main
from fastapi.testclient import TestClient


def test_scheduler_disabled(monkeypatch):
    """Test that the scheduler is not started when DISABLE_SCHEDULER=true."""
    monkeypatch.setenv("DISABLE_SCHEDULER", "true")

    mock_scheduler = MagicMock()

    # Patch SchedulerService where it's used (in app.main namespace)
    with patch(
        "app.main.SchedulerService",
        return_value=mock_scheduler,
    ) as mock_cls:
        # Use context manager to trigger lifespan
        with TestClient(app.main.app) as client:
            # The app should serve requests normally
            response = client.get("/api/v1/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}

            # SchedulerService should NOT have been instantiated
            mock_cls.assert_not_called()


def test_scheduler_enabled_by_default(monkeypatch):
    """Test that the scheduler is started by default."""
    monkeypatch.delenv("DISABLE_SCHEDULER", raising=False)

    mock_scheduler = MagicMock()

    # Patch SchedulerService where it's used (in app.main namespace)
    with patch(
        "app.main.SchedulerService",
        return_value=mock_scheduler,
    ) as mock_cls:
        # Use context manager to trigger lifespan
        with TestClient(app.main.app) as client:
            response = client.get("/api/v1/health")
            assert response.status_code == 200

            # SchedulerService SHOULD have been started
            mock_cls.assert_called_once()
            mock_scheduler.start.assert_called_once()
