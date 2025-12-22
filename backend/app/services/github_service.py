"""GitHub API integration service for discovering repositories with ha-discover topic."""
import os
import logging
from typing import List, Dict, Optional
import httpx

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""
    
    BASE_URL = "https://api.github.com"
    SEARCH_TOPIC = "ha-discover"
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub service with optional authentication token."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def search_repositories(self, per_page: int = 100) -> List[Dict]:
        """
        Search for repositories with the ha-discover topic.
        
        Args:
            per_page: Number of results per page (max 100)
            
        Returns:
            List of repository metadata dictionaries
        """
        repositories = []
        page = 1
        
        async with httpx.AsyncClient() as client:
            while True:
                try:
                    url = f"{self.BASE_URL}/search/repositories"
                    params = {
                        "q": f"topic:{self.SEARCH_TOPIC}",
                        "per_page": per_page,
                        "page": page
                    }
                    
                    response = await client.get(url, headers=self.headers, params=params, timeout=30.0)
                    response.raise_for_status()
                    
                    data = response.json()
                    items = data.get("items", [])
                    
                    if not items:
                        break
                    
                    for repo in items:
                        repositories.append({
                            "name": repo["name"],
                            "owner": repo["owner"]["login"],
                            "description": repo.get("description", ""),
                            "url": repo["html_url"],
                            "default_branch": repo.get("default_branch", "main"),
                        })
                    
                    # Check if there are more pages
                    if len(items) < per_page:
                        break
                    
                    page += 1
                    
                except httpx.HTTPError as e:
                    logger.error(f"Error searching repositories: {e}")
                    break
        
        logger.info(f"Found {len(repositories)} repositories with topic '{self.SEARCH_TOPIC}'")
        return repositories
    
    async def get_file_content(self, owner: str, repo: str, path: str, branch: str = "main") -> Optional[str]:
        """
        Fetch the content of a file from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path in repository
            branch: Branch name (default: main)
            
        Returns:
            File content as string, or None if file not found
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
                params = {"ref": branch}
                
                response = await client.get(url, headers=self.headers, params=params, timeout=30.0)
                
                if response.status_code == 404:
                    logger.debug(f"File not found: {owner}/{repo}/{path}")
                    return None
                
                response.raise_for_status()
                data = response.json()
                
                # GitHub returns base64 encoded content
                import base64
                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
                
        except httpx.HTTPError as e:
            logger.error(f"Error fetching file {owner}/{repo}/{path}: {e}")
            return None
    
    async def find_automation_files(self, owner: str, repo: str, branch: str = "main") -> List[str]:
        """
        Find Home Assistant automation files in a repository.
        
        Currently looks for common automation file names. This is a best-effort approach.
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            List of file paths that might contain automations
        """
        # Common automation file locations
        potential_paths = [
            "automations.yaml",
            "automations.yml",
            "config/automations.yaml",
            "config/automations.yml",
            "home-assistant/automations.yaml",
            "home-assistant/automations.yml",
        ]
        
        found_files = []
        
        async with httpx.AsyncClient() as client:
            for path in potential_paths:
                try:
                    url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"
                    params = {"ref": branch}
                    
                    response = await client.get(url, headers=self.headers, params=params, timeout=30.0)
                    
                    if response.status_code == 200:
                        found_files.append(path)
                        logger.info(f"Found automation file: {owner}/{repo}/{path}")
                        
                except httpx.HTTPError:
                    continue
        
        return found_files
