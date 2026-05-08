"""Bootstrap the local SQLite database from a release asset."""

import gzip
import logging
import os
import shutil
import sqlite3
import tempfile
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

logger = logging.getLogger(__name__)


def sqlite_path_from_url(database_url: str) -> Path | None:
    """Return the filesystem path for a SQLite DATABASE_URL."""
    if database_url.startswith("sqlite:///"):
        return Path(database_url.removeprefix("sqlite:///"))
    if database_url.startswith("sqlite://"):
        return Path(database_url.removeprefix("sqlite://"))
    return None


def bootstrap_database_from_release() -> bool:
    """Download the configured release database into the local SQLite path.

    Returns:
        True when a database was downloaded and installed, otherwise False.

    Raises:
        RuntimeError: If bootstrapping is required and the download or validation fails.
    """
    download_url = os.getenv("DB_DOWNLOAD_URL")
    if not download_url:
        return False
    if urlparse(download_url).scheme != "https":
        raise RuntimeError("DB_DOWNLOAD_URL must use https")

    database_url = os.getenv("DATABASE_URL", "sqlite:///./data/hadiscover.db")
    destination = sqlite_path_from_url(database_url)
    if destination is None:
        raise RuntimeError("DB_DOWNLOAD_URL requires a SQLite DATABASE_URL")

    required = os.getenv("DB_BOOTSTRAP_REQUIRED", "false").lower() == "true"
    timeout = float(os.getenv("DB_DOWNLOAD_TIMEOUT", "15"))
    max_attempts = int(os.getenv("DB_DOWNLOAD_RETRIES", "3"))
    backoff_seconds = float(os.getenv("DB_DOWNLOAD_BACKOFF", "2"))

    destination.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading pre-built database from %s", download_url)

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=destination.parent, suffix=".db.tmp", delete=False
            ) as tmp_file:
                tmp_path = Path(tmp_file.name)
                with urlopen(download_url, timeout=timeout) as response:  # nosec B310
                    with gzip.GzipFile(fileobj=response) as gzip_file:
                        shutil.copyfileobj(gzip_file, tmp_file)

            _validate_sqlite_database(tmp_path)
            tmp_path.replace(destination)
            logger.info("Pre-built database installed at %s", destination)
            return True
        except Exception as exc:
            last_error = exc
            logger.warning(
                "Database download failed (attempt %s/%s): %s",
                attempt,
                max_attempts,
                exc,
            )
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
            if attempt < max_attempts:
                time.sleep(backoff_seconds)

    message = f"Failed to download pre-built database: {last_error}"
    if required:
        raise RuntimeError(message) from last_error

    logger.warning("%s. Continuing with existing or empty database.", message)
    return False


def _validate_sqlite_database(path: Path) -> None:
    """Validate that the downloaded file is a readable SQLite database."""
    with sqlite3.connect(path) as connection:
        result = connection.execute("PRAGMA integrity_check").fetchone()

    if result is None or result[0] != "ok":
        raise RuntimeError("Downloaded database failed SQLite integrity check")
