# Architecture Documentation

This document provides a comprehensive overview of the hadiscover system architecture, including data flow, design decisions, and implementation details.

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Data Flow](#data-flow)
4. [Component Details](#component-details)
5. [Database Schema](#database-schema)
6. [API Design](#api-design)
7. [Design Decisions](#design-decisions)

## System Overview

hadiscover is a full-stack web application consisting of:

- **Backend**: Python FastAPI service for data indexing and search
- **Frontend**: Next.js React application for user interface
- **Database**: SQLite for data persistence
- **External API**: GitHub REST API for repository discovery

The system follows a traditional three-tier architecture with clear separation between presentation (frontend), application logic (backend API), and data storage (database).

## High-Level Architecture

``` text
┌─────────────────────────────────────────────────────────────┐
│                          User Browser                       │
│                     (Next.js Frontend)                      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Search     │  │   Indexing   │  │    GitHub    │       │
│  │   Service    │  │   Service    │  │   Service    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ SQLite Database │
                    └─────────────────┘

                    ┌─────────────────┐
                    │   GitHub API    │
                    └─────────────────┘
```

## Data Flow

### Indexing Flow

1. **Trigger**: User clicks "Trigger Re-Index" or scheduled job runs
2. **Repository Discovery**:
   - Backend calls GitHub API to search for repositories with `hadiscover` topic
   - Returns list of repository metadata (owner, name, URL, default branch)
3. **File Discovery**:
   - For each repository, search for automation files in common locations
   - Attempts: `automations.yaml`, `automations.yml`, `config/automations.yaml`, etc.
4. **Content Fetching**:
   - Fetch raw content of automation files from GitHub
   - Handle 404 errors gracefully if files don't exist
5. **Parsing**:
   - Parse YAML content using PyYAML
   - Extract automation metadata (alias, description, triggers)
   - Handle malformed YAML gracefully
6. **Storage**:
   - Store repository information in `repositories` table
   - Store individual automations in `automations` table
   - Link automations to their source repository via foreign key
7. **Completion**:
   - Log indexing statistics
   - Continue on failure (best-effort indexing)

### Search Flow

1. **User Input**: User enters search query in frontend
2. **API Request**: Frontend sends GET request to `/api/v1/search?q={query}`
3. **Search Processing**:
   - Backend performs case-insensitive search across multiple fields
   - Fields searched: automation alias, description, trigger types, repository name/description
   - Uses SQL LIKE with wildcards for flexible matching
4. **Result Assembly**:
   - Join automations with their repositories
   - Format results with nested repository information
   - Limit results based on query parameter (default 50, max 100)
5. **Response**: Return JSON array of matching automations
6. **Frontend Display**: Render results with links to GitHub sources

## Component Details

### Backend Services

#### 1. GitHub Service (`app/services/github_service.py`)

**Responsibilities:**

- Interact with GitHub REST API
- Search for repositories by topic
- Fetch file contents from repositories
- Discover automation files using common path patterns

**Key Methods:**

- `search_repositories()`: Find repos with hadiscover topic
- `get_file_content()`: Fetch raw file content
- `find_automation_files()`: Locate automation files in repo

**Design Notes:**

- Uses async/await for concurrent API calls
- Handles rate limiting and errors gracefully
- Optional GitHub token for higher rate limits
- Base64 decodes file content from GitHub API

#### 2. Parser Service (`app/services/parser.py`)

**Responsibilities:**

- Parse Home Assistant YAML automation files
- Extract metadata from automations
- Handle various YAML structures
- Track line numbers for precise GitHub linking

**Key Methods:**

- `parse_automation_file()`: Parse complete YAML file with line number tracking
- `_parse_single_automation()`: Extract metadata from one automation
- `_extract_trigger_types()`: Identify trigger platforms (supports both old `platform` and new `trigger` keys)
- `_extract_blueprint_info()`: Extract blueprint path and input configuration
- `_extract_action_calls()`: Recursively extract service calls from actions (supports both old `service` and new `action` keys)

**Design Notes:**

- Best-effort parsing (doesn't require perfect YAML)
- Handles list-of-automations and single-automation formats
- Extracts trigger types, blueprints, and action calls for filtering and discovery
- Tracks start and end line numbers using YAML node marks
- Supports both old and new Home Assistant YAML formats
- Recursively processes nested action structures (if/then/else, choose, repeat)
- Automatically deduplicates trigger types and action calls
- Logs warnings for malformed content but continues

#### 3. Indexing Service (`app/services/indexer.py`)

**Responsibilities:**

- Orchestrate the indexing process
- Coordinate GitHub, Parser, and Database operations
- Manage transactions and error handling

**Key Methods:**

- `index_repositories()`: Index all discovered repositories
- `_index_repository()`: Index a single repository

**Design Notes:**

- Updates existing repositories (upsert pattern)
- Removes old automations before re-indexing
- Commits per-repository for isolation
- Returns statistics on success/failure

#### 4. Search Service (`app/services/search_service.py`)

**Responsibilities:**

- Query database for automations
- Format search results
- Provide statistics and facets

**Key Methods:**

- `search_automations()`: Full-text search with filtering by repository, blueprint, and trigger
- `get_statistics()`: Count repositories and automations, retrieve last indexed time and star count
- `get_facets()`: Generate aggregated counts for repositories, blueprints, and triggers

**Design Notes:**

- Case-insensitive searching
- Searches across multiple fields simultaneously
- Returns random automations if no query or filters provided
- Includes repository information in results
- Supports faceted search for filtering
- Includes line numbers for precise GitHub linking

#### 5. Scheduler Service (`app/services/scheduler.py`)

**Responsibilities:**

- Manage scheduled background tasks
- Run automated hourly indexing
- Coordinate with IndexingService

**Key Methods:**

- `start()`: Initialize scheduler with hourly cron job
- `run_indexing_task()`: Execute indexing in background
- `shutdown()`: Gracefully stop scheduler

**Design Notes:**

- Uses APScheduler with AsyncIO scheduler
- Runs indexing at the top of every hour (minute 0)
- Single instance protection (max_instances=1)
- Separate database session for background tasks
- Starts automatically on application startup via lifespan handler

### Frontend Components

#### Main Page (`frontend/app/page.tsx`)

**Responsibilities:**

- Render search interface
- Display results
- Manage application state
- Call backend API

**Key Features:**

- Real-time search with debouncing would be ideal (not implemented in MVP)
- Statistics display
- Manual indexing trigger
- Responsive design with Tailwind CSS
- Dark mode support

**Design Notes:**

- Client-side rendering with React hooks
- Environment variable for API URL configuration
- Error handling with user-friendly messages
- External links open in new tabs

## Database Schema

### Tables

#### `repositories`

Stores information about indexed GitHub repositories.

```sql
CREATE TABLE repositories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    description TEXT NULL,
    url VARCHAR(512) NOT NULL UNIQUE,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### `automations`

Stores individual Home Assistant automations.

```sql
CREATE TABLE automations (
    id INTEGER PRIMARY KEY,
    alias VARCHAR(512) NULL,
    description TEXT NULL,
    trigger_types TEXT NULL,  -- Comma-separated list
    blueprint_path VARCHAR(512) NULL,  -- Path to blueprint if using one
    action_calls TEXT NULL,  -- Comma-separated list of service calls
    source_file_path VARCHAR(512) NOT NULL,
    github_url VARCHAR(1024) NOT NULL,
    start_line INTEGER NULL,  -- Starting line number in source file
    end_line INTEGER NULL,  -- Ending line number in source file
    repository_id INTEGER NOT NULL,
    indexed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repository_id) REFERENCES repositories(id)
);
```

#### `indexing_metadata`

Tracks metadata about indexing operations.

```sql
CREATE TABLE indexing_metadata (
    id INTEGER PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Common keys**:

- `last_completed_at`: ISO timestamp of last successful indexing
- `repo_star_count`: Total star count across all indexed repositories

### Indexes

- `repositories.url`: Unique index for repository identification
- `automations.alias`: Index for faster name searches
- `automations.blueprint_path`: Index for blueprint filtering
- `automations.repository_id`: Foreign key index for joins
- `indexing_metadata.key`: Unique index for metadata keys

### Relationships

- One repository has many automations (1:N)
- Cascading delete: removing a repository removes its automations

## API Design

### RESTful Principles

The API follows REST conventions:

- Resources are nouns (e.g., `/search`, `/statistics`)
- HTTP methods indicate action (GET for read, POST for create/trigger)
- Stateless requests
- JSON response format

### Endpoints

#### `GET /api/v1/search`

**Query Parameters:**

- `q` (string, optional): Search query
- `limit` (integer, optional, default=50, max=100): Results per page
- `repo` (string, optional): Filter by repository (format: "owner/name")
- `blueprint` (string, optional): Filter by blueprint path
- `trigger` (string, optional): Filter by trigger type

**Response:**

```json
{
  "query": "string",
  "results": [
    {
      "id": 1,
      "alias": "string",
      "description": "string",
      "trigger_types": ["string"],
      "blueprint_path": "string",
      "action_calls": ["string"],
      "source_file_path": "string",
      "github_url": "string",
      "start_line": 1,
      "end_line": 10,
      "repository": {...},
      "indexed_at": "2024-01-01T00:00:00"
    }
  ],
  "count": 0,
  "facets": {
    "repositories": [{"owner": "string", "name": "string", "count": 0}],
    "blueprints": [{"path": "string", "count": 0}],
    "triggers": [{"type": "string", "count": 0}]
  }
}
```

#### `GET /api/v1/statistics`

**Response:**

```json
{
  "total_repositories": 0,
  "total_automations": 0,
  "last_indexed_at": "2024-01-01T00:00:00",
  "repo_star_count": 0
}
```

#### `POST /api/v1/index`

**Availability:** Development mode only (controlled by `ENVIRONMENT=development`)

**Rate Limiting:** Once every 10 minutes

**Success Response (200):**

```json
{
  "message": "Indexing started in background. Refresh your browser to see the changes once complete.",
  "started": true
}
```

**Rate Limit Response (429):**

```json
{
  "detail": "Indexing rate limit exceeded. Please wait 9m 45s before triggering again."
}
```

**Production Response (403):**

```json
{
  "detail": "This endpoint is not available in production. Indexing runs on a daily schedule."
}
```

#### `GET /api/v1/health`

**Response:**

```json
{
  "status": "healthy"
}
```

### CORS Configuration

Backend allows requests from:

- `http://localhost:3000` (Next.js default dev port)
- `http://localhost:8080` (production frontend port)
- `https://hadiscover.com`
- `https://www.hadiscover.com`
- `https://api.hadiscover.com`

This enables local development with separate backend/frontend servers.

## Design Decisions

### 1. SQLite Database

**Decision:** Use SQLite instead of PostgreSQL or MySQL

**Rationale:**

- MVP doesn't require high concurrency
- Zero configuration required
- File-based, easy to backup
- Sufficient performance for expected data volume
- Can migrate to PostgreSQL later if needed

### 2. Best-Effort Parsing

**Decision:** Parse YAML with fault tolerance

**Rationale:**

- Home Assistant configurations vary widely
- Users may have custom structures
- Partial data is better than no data
- Graceful degradation improves user experience

### 3. Opt-In via GitHub Topic

**Decision:** Only index repositories with explicit topic

**Rationale:**

- Respects user privacy
- Clear consent mechanism
- Easy for users to opt in/out
- Reduces noise from unrelated repositories

### 4. Background Indexing and Scheduling

**Decision:** Run indexing as both scheduled background task and on-demand (development only)

**Rationale:**

- Hourly scheduled indexing ensures fresh data automatically
- Manual trigger available in development for testing
- Indexing can take minutes for many repositories
- Prevents API timeout issues
- Better user experience (immediate response)
- Allows concurrent indexing and searching
- APScheduler provides reliable cron-like scheduling
- Single instance protection prevents overlapping indexing runs

### 5. Direct GitHub Links

**Decision:** Store and display GitHub URLs for each automation

**Rationale:**

- Users can view full context
- Encourages community engagement
- Attribution to original authors
- No copyright concerns (linking, not copying)

### 6. No Authentication

**Decision:** No user authentication in MVP

**Rationale:**

- MVP scope is read-only public data
- Reduces complexity
- Can add authentication later if needed
- GitHub data is already public

### 7. Server-Side Rendering vs Client-Side

**Decision:** Use client-side rendering (CSR) with Next.js

**Rationale:**

- Simpler deployment model
- MVP doesn't need SEO optimization
- Faster development iteration
- Can migrate to SSR later if beneficial

### 8. Monorepo Structure

**Decision:** Separate `backend/` and `frontend/` directories

**Rationale:**

- Clear separation of concerns
- Independent deployment possible
- Different tech stacks don't interfere
- Standard pattern for full-stack apps

### 9. Rate Limiting on Indexing

**Decision:** Limit re-indexing to once every 10 minutes

**Rationale:**

- Prevents API abuse and excessive GitHub API calls
- Reduces server load
- GitHub API has rate limits that need to be respected
- 10-minute cooldown is reasonable for discovery of new repositories
- In-memory tracking sufficient for MVP (single server)
- Returns HTTP 429 with clear error message including wait time

### 10. Faceted Search

**Decision:** Provide facets for repositories, blueprints, and trigger types

**Rationale:**

- Enables users to discover patterns in automations
- Helps users filter large result sets
- Shows popularity of blueprints and trigger types
- Improves user experience by making search more interactive
- Facets update dynamically based on current search and filters

### 11. Line Number Tracking

**Decision:** Store start and end line numbers for each automation

**Rationale:**

- Enables precise GitHub links directly to automation in file
- Better user experience (no scrolling to find automation)
- Works with GitHub's line number URL format (#L10-L20)
- Uses YAML parser's built-in node marks for accuracy
- Minimal overhead during parsing

### 12. Blueprint and Action Call Extraction

**Decision:** Extract blueprint paths and service calls from automations

**Rationale:**

- Blueprints are increasingly popular in Home Assistant community
- Users want to find automations using specific blueprints
- Action calls show which integrations/services are being used
- Enables filtering by blueprint or action type
- Helps users discover integration usage patterns
- Supports both old (`service`) and new (`action`) YAML formats for future compatibility

### 13. Hourly Scheduled Indexing

**Decision:** Run automatic indexing every hour

**Rationale:**

- Ensures index stays fresh without manual intervention
- Hourly frequency balances freshness with GitHub API rate limits
- Runs at top of hour for predictable timing
- Manual trigger restricted to development to prevent production load
- Single instance protection prevents overlapping runs
- APScheduler provides robust scheduling without external dependencies

## Future Enhancements

Potential improvements beyond current implementation:

1. **Advanced Search**: Fuzzy matching, boolean operators, phrase matching
2. **Pagination**: Handle large result sets efficiently (currently limited to 100)
3. ~~**Scheduled Indexing**: Cron job for automatic re-indexing~~ ✅ **Implemented** (hourly scheduling)
4. ~~**Filters by Trigger Type**: Allow filtering by specific triggers~~ ✅ **Implemented** (faceted search)
5. ~~**Blueprint Support**: Index and search blueprint-based automations~~ ✅ **Implemented**
6. ~~**Line Number Tracking**: Link to specific lines in GitHub files~~ ✅ **Implemented**
7. **Caching**: Redis for frequently accessed data and search results
8. **Analytics**: Track popular automations and search queries
9. **User Contributions**: Allow annotations, ratings, or comments
10. **API Authentication**: Rate limiting and API keys for third-party integrations
11. **Deployment Guide**: Kubernetes configs and cloud platform guides
12. **Testing**: Frontend tests, E2E tests with Playwright
13. **Monitoring**: Application metrics, performance tracking, and alerting
14. **Search History**: Save and recall previous searches
15. **Export Features**: Export search results as JSON or YAML

## Conclusion

hadiscover uses a straightforward, maintainable architecture appropriate for an MVP. The system prioritizes simplicity, fault tolerance, and extensibility. All components are loosely coupled, making it easy to swap implementations or add features in the future.
