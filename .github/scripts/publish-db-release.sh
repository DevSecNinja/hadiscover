#!/usr/bin/env bash
# Publishes the pre-built database as a rolling GitHub release asset.
#
# The release uses a fixed tag (db-latest) so consumers can always download
# the current database from a stable URL:
#
#   https://github.com/<owner>/<repo>/releases/download/db-latest/hadiscover.db.gz
#
# Required environment variables:
#   GITHUB_TOKEN       - Token with contents:write permission (auto-set in Actions)
#   GITHUB_REPOSITORY  - owner/repo (auto-set in Actions)

set -euo pipefail

DB_FILE="backend/data/hadiscover.db.gz"
RELEASE_TAG="db-latest"
RELEASE_TITLE="Latest Database"

if [ ! -f "${DB_FILE}" ]; then
	echo "Error: Database file '${DB_FILE}' not found."
	exit 1
fi

# Create release if it doesn't exist, otherwise update the asset
if gh release view "${RELEASE_TAG}" &>/dev/null; then
	echo "Updating existing '${RELEASE_TAG}' release asset..."
	gh release upload "${RELEASE_TAG}" "${DB_FILE}" --clobber
else
	echo "Creating '${RELEASE_TAG}' release..."
	gh release create "${RELEASE_TAG}" \
		--title "${RELEASE_TITLE}" \
		--notes "Pre-built database automatically updated by GitHub Actions on every run.

## Usage

Set \`DB_DOWNLOAD_URL\` in your backend container to bootstrap without a GitHub API token:

\`\`\`
DB_DOWNLOAD_URL=https://github.com/${GITHUB_REPOSITORY}/releases/download/db-latest/hadiscover.db.gz
DISABLE_SCHEDULER=true
\`\`\`

The database is compressed with gzip. The backend will decompress it automatically on first start." \
		--prerelease \
		"${DB_FILE}"
fi

echo "✓ Database published to release '${RELEASE_TAG}'"
