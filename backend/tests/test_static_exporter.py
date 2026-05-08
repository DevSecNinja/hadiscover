"""Tests for static frontend search index export."""

import json
from datetime import datetime, timezone

from app.models.database import Automation, IndexingMetadata, Repository
from app.services.static_exporter import export_search_index


def test_export_search_index_writes_frontend_contract(test_db, tmp_path):
    """Exported JSON includes statistics and API-shaped automation rows."""
    repository = Repository(
        name="home-assistant-config",
        owner="testuser",
        description="My Home Assistant configuration",
        url="https://github.com/testuser/home-assistant-config",
        stars=42,
    )
    test_db.add(repository)
    test_db.flush()

    indexed_at = datetime(2026, 5, 8, 12, 30, tzinfo=timezone.utc)
    test_db.add(
        Automation(
            alias="Motion Activated Light",
            description="Turn on light when motion is detected",
            trigger_types="state,motion",
            blueprint_path="blueprints/motion.yaml",
            action_calls="light.turn_on,notify.mobile_app",
            source_file_path="automations.yaml",
            github_url="https://github.com/testuser/home-assistant-config/blob/main/automations.yaml",
            start_line=1,
            end_line=12,
            repository_id=repository.id,
            indexed_at=indexed_at,
        )
    )
    test_db.add(IndexingMetadata(key="last_completed_at", value="2026-05-08T12:30:00Z"))
    test_db.add(IndexingMetadata(key="repo_star_count", value="42"))
    test_db.commit()

    output_path = export_search_index(test_db, tmp_path / "search-index.json")

    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert data["statistics"] == {
        "total_repositories": 1,
        "total_automations": 1,
        "last_indexed_at": "2026-05-08T12:30:00Z",
        "repo_star_count": 42,
    }
    assert data["automations"] == [
        {
            "id": 1,
            "alias": "Motion Activated Light",
            "description": "Turn on light when motion is detected",
            "trigger_types": ["state", "motion"],
            "blueprint_path": "blueprints/motion.yaml",
            "action_calls": ["light.turn_on", "notify.mobile_app"],
            "source_file_path": "automations.yaml",
            "github_url": "https://github.com/testuser/home-assistant-config/blob/main/automations.yaml",
            "start_line": 1,
            "end_line": 12,
            "repository": {
                "name": "home-assistant-config",
                "owner": "testuser",
                "description": "My Home Assistant configuration",
                "url": "https://github.com/testuser/home-assistant-config",
                "stars": 42,
            },
            "indexed_at": "2026-05-08T12:30:00",
        }
    ]
