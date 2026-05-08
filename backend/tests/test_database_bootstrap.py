"""Tests for bootstrapping SQLite from release assets."""

import gzip
import io
import sqlite3

import pytest
from app.services import database_bootstrap


class MockResponse(io.BytesIO):
    """BytesIO response with context manager support."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def make_gzipped_sqlite() -> bytes:
    """Create a gzip-compressed SQLite database for tests."""
    source = sqlite3.connect(":memory:")
    source.execute("CREATE TABLE repositories (id INTEGER PRIMARY KEY)")
    source.commit()

    backup = sqlite3.connect("file:backup?mode=memory&cache=shared", uri=True)
    source.backup(backup)

    dump = io.BytesIO()
    for line in backup.iterdump():
        dump.write(f"{line}\n".encode())

    database = sqlite3.connect(":memory:")
    database.executescript(dump.getvalue().decode())
    serialized = database.serialize()

    source.close()
    backup.close()
    database.close()
    return gzip.compress(serialized)


def test_sqlite_path_from_url():
    """Test SQLite DATABASE_URL path parsing."""
    assert str(database_bootstrap.sqlite_path_from_url("sqlite:///./data/test.db")) == (
        "data/test.db"
    )
    assert str(database_bootstrap.sqlite_path_from_url("sqlite:////tmp/test.db")) == (
        "/tmp/test.db"
    )
    assert database_bootstrap.sqlite_path_from_url("postgresql://example") is None


def test_bootstrap_database_from_release(monkeypatch, tmp_path):
    """Test downloading, decompressing, and installing a release database."""
    database_path = tmp_path / "hadiscover.db"
    payload = make_gzipped_sqlite()

    def mock_urlopen(url, timeout):
        assert url == "https://example.com/hadiscover.db.gz"
        assert timeout == 15
        return MockResponse(payload)

    monkeypatch.setenv("DB_DOWNLOAD_URL", "https://example.com/hadiscover.db.gz")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setattr(database_bootstrap, "urlopen", mock_urlopen)

    assert database_bootstrap.bootstrap_database_from_release() is True
    assert database_path.exists()

    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()

    assert ("repositories",) in tables


def test_bootstrap_skips_without_download_url(monkeypatch):
    """Test that bootstrapping is disabled unless DB_DOWNLOAD_URL is set."""
    monkeypatch.delenv("DB_DOWNLOAD_URL", raising=False)

    assert database_bootstrap.bootstrap_database_from_release() is False


def test_bootstrap_rejects_non_https_url(monkeypatch):
    """Test that database release URLs must use HTTPS."""
    monkeypatch.setenv("DB_DOWNLOAD_URL", "http://example.com/hadiscover.db.gz")

    with pytest.raises(RuntimeError, match="must use https"):
        database_bootstrap.bootstrap_database_from_release()


def test_bootstrap_required_raises_on_failure(monkeypatch, tmp_path):
    """Test required bootstrap mode fails startup when download fails."""
    database_path = tmp_path / "hadiscover.db"

    def mock_urlopen(url, timeout):
        raise OSError("network unavailable")

    monkeypatch.setenv("DB_DOWNLOAD_URL", "https://example.com/hadiscover.db.gz")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("DB_BOOTSTRAP_REQUIRED", "true")
    monkeypatch.setenv("DB_DOWNLOAD_RETRIES", "1")
    monkeypatch.setattr(database_bootstrap, "urlopen", mock_urlopen)

    with pytest.raises(RuntimeError, match="Failed to download"):
        database_bootstrap.bootstrap_database_from_release()

    assert not database_path.exists()
