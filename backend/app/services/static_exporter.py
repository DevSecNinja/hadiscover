"""Export indexed automation data for static frontend search."""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.models.database import Automation, Repository
from app.services.search_service import SearchService
from sqlalchemy.orm import Session


def export_search_index(db: Session, output_path: str | Path) -> Path:
    """Export the complete search index to a JSON file."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "statistics": SearchService.get_statistics(db),
        "automations": _get_automations(db),
    }

    with destination.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=False, separators=(",", ":"))
        output_file.write("\n")

    return destination


def _get_automations(db: Session) -> list[dict]:
    rows = (
        db.query(Automation, Repository)
        .join(Repository, Automation.repository_id == Repository.id)
        .order_by(Automation.indexed_at.desc(), Automation.id.desc())
        .all()
    )

    return [
        _format_automation(automation, repository) for automation, repository in rows
    ]


def _format_automation(automation: Automation, repository: Repository) -> dict:
    return {
        "id": automation.id,
        "alias": automation.alias,
        "description": automation.description,
        "trigger_types": _split_csv(automation.trigger_types),
        "blueprint_path": automation.blueprint_path,
        "action_calls": _split_csv(automation.action_calls),
        "source_file_path": automation.source_file_path,
        "github_url": automation.github_url,
        "start_line": automation.start_line,
        "end_line": automation.end_line,
        "repository": {
            "name": repository.name,
            "owner": repository.owner,
            "description": repository.description,
            "url": repository.url,
            "stars": repository.stars or 0,
        },
        "indexed_at": (
            automation.indexed_at.isoformat() if automation.indexed_at else None
        ),
    }


def _split_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]
