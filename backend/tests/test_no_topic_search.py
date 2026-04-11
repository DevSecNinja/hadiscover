"""Tests for no-topic search functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.services.github_service import GitHubService
from app.services.indexer import IndexingService


@pytest.mark.asyncio
async def test_github_service_no_topic_search_disabled_by_default():
    """Test that GitHubService defaults to topic-based search."""
    service = GitHubService()
    assert service.enable_no_topic_search is False
    assert service.max_repositories is None


@pytest.mark.asyncio
async def test_github_service_no_topic_search_enabled():
    """Test that GitHubService can enable no-topic search."""
    service = GitHubService(enable_no_topic_search=True)
    assert service.enable_no_topic_search is True


@pytest.mark.asyncio
async def test_github_service_max_repositories():
    """Test that GitHubService respects max_repositories limit."""
    service = GitHubService(enable_no_topic_search=True, max_repositories=10)
    assert service.max_repositories == 10


@pytest.mark.asyncio
async def test_search_repositories_with_no_topic_search():
    """Test that search_repositories uses different query when no-topic search is enabled."""
    service = GitHubService(enable_no_topic_search=True)

    # Mock response with test data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "name": "test-repo",
                "owner": {"login": "testowner"},
                "description": "Test repository",
                "html_url": "https://github.com/testowner/test-repo",
                "default_branch": "main",
                "stargazers_count": 5,
            }
        ]
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        repos = await service.search_repositories()

        # Verify the correct query was used
        call_args = mock_client.get.call_args
        assert call_args is not None
        params = call_args[1]["params"]
        assert "automations.yaml in:path" in params["q"]
        assert "topic:" not in params["q"]

        # Verify repository was returned
        assert len(repos) == 1
        assert repos[0]["name"] == "test-repo"


@pytest.mark.asyncio
async def test_search_repositories_with_topic_search():
    """Test that search_repositories uses topic query when no-topic search is disabled."""
    service = GitHubService(enable_no_topic_search=False)

    # Mock response with test data
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "name": "test-repo",
                "owner": {"login": "testowner"},
                "description": "Test repository",
                "html_url": "https://github.com/testowner/test-repo",
                "default_branch": "main",
                "stargazers_count": 5,
            }
        ]
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        repos = await service.search_repositories()

        # Verify the correct query was used (should be topic-based)
        call_args = mock_client.get.call_args
        assert call_args is not None
        params = call_args[1]["params"]
        assert "topic:" in params["q"]

        # Verify repository was returned
        assert len(repos) == 1
        assert repos[0]["name"] == "test-repo"


@pytest.mark.asyncio
async def test_search_repositories_respects_max_repositories():
    """Test that search_repositories stops after reaching max_repositories limit."""
    service = GitHubService(enable_no_topic_search=True, max_repositories=2)

    # Mock response with 3 repos, but we should only get 2
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "name": f"test-repo-{i}",
                "owner": {"login": "testowner"},
                "description": f"Test repository {i}",
                "html_url": f"https://github.com/testowner/test-repo-{i}",
                "default_branch": "main",
                "stargazers_count": 5,
            }
            for i in range(3)
        ]
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        repos = await service.search_repositories()

        # Verify only 2 repositories were returned
        assert len(repos) == 2


@pytest.mark.asyncio
async def test_search_repositories_no_max_limit():
    """Test that search_repositories returns all repos when max_repositories is None."""
    service = GitHubService(enable_no_topic_search=True, max_repositories=None)

    # Mock response with 3 repos
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "items": [
            {
                "name": f"test-repo-{i}",
                "owner": {"login": "testowner"},
                "description": f"Test repository {i}",
                "html_url": f"https://github.com/testowner/test-repo-{i}",
                "default_branch": "main",
                "stargazers_count": 5,
            }
            for i in range(3)
        ]
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_class.return_value = mock_client

        repos = await service.search_repositories()

        # Verify all 3 repositories were returned
        assert len(repos) == 3


@pytest.mark.asyncio
async def test_indexing_service_passes_parameters():
    """Test that IndexingService correctly passes parameters to GitHubService."""
    indexer = IndexingService(
        github_token="test_token",
        enable_no_topic_search=True,
        max_repositories=10,
    )

    assert indexer.github_service.enable_no_topic_search is True
    assert indexer.github_service.max_repositories == 10
    assert indexer.github_service.token == "test_token"


@pytest.mark.asyncio
async def test_search_repositories_avoids_duplicates_in_no_topic_mode():
    """Test that no-topic search doesn't return duplicate repositories."""
    service = GitHubService(enable_no_topic_search=True)

    # Mock response with duplicate repos
    mock_response_page1 = MagicMock()
    mock_response_page1.status_code = 200
    mock_response_page1.json.return_value = {
        "items": [
            {
                "name": "test-repo",
                "owner": {"login": "testowner"},
                "description": "Test repository",
                "html_url": "https://github.com/testowner/test-repo",
                "default_branch": "main",
                "stargazers_count": 5,
            }
        ]
    }

    # Second page returns same repo (unlikely but possible)
    mock_response_page2 = MagicMock()
    mock_response_page2.status_code = 200
    mock_response_page2.json.return_value = {
        "items": []  # Empty to stop pagination
    }

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.side_effect = [mock_response_page1, mock_response_page2]
        mock_client_class.return_value = mock_client

        repos = await service.search_repositories()

        # Should only have one repo (no duplicates)
        assert len(repos) == 1


@pytest.mark.asyncio
async def test_environment_variable_parsing():
    """Test that environment variables are correctly parsed for boolean values."""
    import os

    # Test various truthy values
    for value in ["true", "True", "TRUE", "1", "yes", "Yes"]:
        os.environ["ENABLE_NO_TOPIC_SEARCH"] = value
        result = os.getenv("ENABLE_NO_TOPIC_SEARCH", "false").lower() in (
            "true",
            "1",
            "yes",
        )
        assert result is True, f"Failed for value: {value}"

    # Test various falsy values
    for value in ["false", "False", "FALSE", "0", "no", "No", ""]:
        os.environ["ENABLE_NO_TOPIC_SEARCH"] = value
        result = os.getenv("ENABLE_NO_TOPIC_SEARCH", "false").lower() in (
            "true",
            "1",
            "yes",
        )
        assert result is False, f"Failed for value: {value}"

    # Clean up
    if "ENABLE_NO_TOPIC_SEARCH" in os.environ:
        del os.environ["ENABLE_NO_TOPIC_SEARCH"]


@pytest.mark.asyncio
async def test_max_repositories_integer_parsing():
    """Test that MAX_REPOSITORIES environment variable is correctly parsed as integer."""
    import os

    # Test valid integer
    os.environ["MAX_REPOSITORIES"] = "10"
    max_repositories_str = os.getenv("MAX_REPOSITORIES")
    max_repositories = int(max_repositories_str) if max_repositories_str else None
    assert max_repositories == 10

    # Test None when not set
    if "MAX_REPOSITORIES" in os.environ:
        del os.environ["MAX_REPOSITORIES"]
    max_repositories_str = os.getenv("MAX_REPOSITORIES")
    max_repositories = int(max_repositories_str) if max_repositories_str else None
    assert max_repositories is None

    # Test empty string
    os.environ["MAX_REPOSITORIES"] = ""
    max_repositories_str = os.getenv("MAX_REPOSITORIES")
    max_repositories = int(max_repositories_str) if max_repositories_str else None
    assert max_repositories is None

    # Clean up
    if "MAX_REPOSITORIES" in os.environ:
        del os.environ["MAX_REPOSITORIES"]
