"""API routes for HA Discover."""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models import get_db
from app.services.search_service import SearchService
from app.services.indexer import IndexingService

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for API
class RepositoryResponse(BaseModel):
    """Repository information in API response."""
    name: str
    owner: str
    description: Optional[str]
    url: str


class AutomationResponse(BaseModel):
    """Automation search result."""
    id: int
    alias: Optional[str]
    description: Optional[str]
    trigger_types: List[str]
    source_file_path: str
    github_url: str
    repository: RepositoryResponse
    indexed_at: Optional[str]


class SearchResponse(BaseModel):
    """Search API response."""
    query: str
    results: List[AutomationResponse]
    count: int


class StatisticsResponse(BaseModel):
    """Statistics API response."""
    total_repositories: int
    total_automations: int


class IndexResponse(BaseModel):
    """Indexing operation response."""
    message: str
    started: bool


class IndexStatusResponse(BaseModel):
    """Indexing status response."""
    repositories_found: int
    repositories_indexed: int
    automations_indexed: int
    errors: int


@router.get("/search", response_model=SearchResponse)
async def search_automations(
    q: str = "",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Search for Home Assistant automations.
    
    Args:
        q: Search query string (searches across automation name, description, triggers, and repository)
        limit: Maximum number of results (default: 50, max: 100)
        db: Database session
        
    Returns:
        Search results with matching automations
    """
    if limit > 100:
        limit = 100
    
    results = SearchService.search_automations(db, q, limit)
    
    return {
        "query": q,
        "results": results,
        "count": len(results)
    }


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(db: Session = Depends(get_db)):
    """
    Get statistics about indexed repositories and automations.
    
    Args:
        db: Database session
        
    Returns:
        Statistics about indexed data
    """
    stats = SearchService.get_statistics(db)
    return stats


@router.post("/index", response_model=IndexResponse)
async def trigger_indexing(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger indexing of repositories with ha-discover topic.
    
    This endpoint starts indexing in the background.
    
    Args:
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Confirmation that indexing has started
    """
    async def run_indexing():
        """Background task to run indexing."""
        indexer = IndexingService()
        # Create a new session for background task
        from app.models import SessionLocal
        bg_db = SessionLocal()
        try:
            await indexer.index_repositories(bg_db)
        finally:
            bg_db.close()
    
    background_tasks.add_task(run_indexing)
    
    return {
        "message": "Indexing started in background",
        "started": True
    }


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Simple health status
    """
    return {"status": "healthy"}
