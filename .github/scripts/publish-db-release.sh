#!/usr/bin/env bash
# Publishes the pre-built database and static search data as GitHub release assets.
#
# Creates two releases:
#   1. A rolling "db-latest" release (always points to the newest data)
#   2. A dated "db-YYYY-MM-DD" release (immutable daily snapshot)
#
# Stable download URLs (always the latest):
#   https://github.com/<owner>/<repo>/releases/download/db-latest/hadiscover.db.gz
#   https://github.com/<owner>/<repo>/releases/download/db-latest/search-index.json
#
# Required environment variables:
#   GITHUB_TOKEN      - Token with contents:write permission
#   GITHUB_REPOSITORY - owner/repo (auto-set in Actions)

set -euo pipefail

DB_FILE="backend/data/hadiscover.db.gz"
SEARCH_INDEX_FILE="frontend/public/data/search-index.json"
LATEST_TAG="db-latest"
DATED_TAG="db-$(date -u +%Y-%m-%d)"

if [ ! -f "${DB_FILE}" ]; then
	echo "Error: Database file '${DB_FILE}' not found."
	exit 1
fi

if [ ! -f "${SEARCH_INDEX_FILE}" ]; then
	echo "Error: Search index file '${SEARCH_INDEX_FILE}' not found."
	exit 1
fi

RELEASE_BODY="Static search data and archived SQLite database updated by GitHub Actions.

## Usage

The production website serves search data from GitHub Pages and does not require a backend API container.

Static search data asset:

https://github.com/${GITHUB_REPOSITORY}/releases/download/${LATEST_TAG}/search-index.json

Archived SQLite database:

https://github.com/${GITHUB_REPOSITORY}/releases/download/${LATEST_TAG}/hadiscover.db.gz"

# --- Rolling latest release ---
if gh release view "${LATEST_TAG}" &>/dev/null; then
	echo "Updating existing '${LATEST_TAG}' release assets..."
	gh release upload "${LATEST_TAG}" "${DB_FILE}" "${SEARCH_INDEX_FILE}" --clobber
else
	echo "Creating '${LATEST_TAG}' release..."
	gh release create "${LATEST_TAG}" \
		--title "Latest Search Data" \
		--notes "${RELEASE_BODY}" \
		--prerelease \
		"${DB_FILE}" \
		"${SEARCH_INDEX_FILE}"
fi
echo "✓ Published to '${LATEST_TAG}'"

# --- Dated snapshot release ---
if gh release view "${DATED_TAG}" &>/dev/null; then
	echo "Updating existing '${DATED_TAG}' release assets..."
	gh release upload "${DATED_TAG}" "${DB_FILE}" "${SEARCH_INDEX_FILE}" --clobber
else
	echo "Creating '${DATED_TAG}' release..."
	gh release create "${DATED_TAG}" \
		--title "Search Data ${DATED_TAG#db-}" \
		--notes "${RELEASE_BODY}" \
		--prerelease \
		"${DB_FILE}" \
		"${SEARCH_INDEX_FILE}"
fi
echo "✓ Published to '${DATED_TAG}'"
