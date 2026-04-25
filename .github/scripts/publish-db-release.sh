#!/usr/bin/env bash
# Publishes the pre-built database as GitHub release assets.
#
# Creates two releases:
#   1. A rolling "db-latest" release (always points to the newest DB)
#   2. A dated "db-YYYY-MM-DD" release (immutable daily snapshot)
#
# Stable download URL (always the latest):
#   https://github.com/<owner>/<repo>/releases/download/db-latest/hadiscover.db.gz
#
# Required environment variables:
#   GITHUB_TOKEN      - Token with contents:write permission
#   GITHUB_REPOSITORY - owner/repo (auto-set in Actions)

set -euo pipefail

DB_FILE="backend/data/hadiscover.db.gz"
LATEST_TAG="db-latest"
DATED_TAG="db-$(date -u +%Y-%m-%d)"

if [ ! -f "${DB_FILE}" ]; then
	echo "Error: Database file '${DB_FILE}' not found."
	exit 1
fi

RELEASE_BODY="Pre-built database updated by GitHub Actions.

## Usage

Set these environment variables in your backend container:

\`\`\`
DB_DOWNLOAD_URL=https://github.com/${GITHUB_REPOSITORY}/releases/download/${LATEST_TAG}/hadiscover.db.gz
DISABLE_SCHEDULER=true
\`\`\`"

# --- Rolling latest release ---
if gh release view "${LATEST_TAG}" &>/dev/null; then
	echo "Updating existing '${LATEST_TAG}' release asset..."
	gh release upload "${LATEST_TAG}" "${DB_FILE}" --clobber
else
	echo "Creating '${LATEST_TAG}' release..."
	gh release create "${LATEST_TAG}" \
		--title "Latest Database" \
		--notes "${RELEASE_BODY}" \
		--prerelease \
		"${DB_FILE}"
fi
echo "✓ Published to '${LATEST_TAG}'"

# --- Dated snapshot release ---
if gh release view "${DATED_TAG}" &>/dev/null; then
	echo "Updating existing '${DATED_TAG}' release asset..."
	gh release upload "${DATED_TAG}" "${DB_FILE}" --clobber
else
	echo "Creating '${DATED_TAG}' release..."
	gh release create "${DATED_TAG}" \
		--title "Database ${DATED_TAG#db-}" \
		--notes "${RELEASE_BODY}" \
		--prerelease \
		"${DB_FILE}"
fi
echo "✓ Published to '${DATED_TAG}'"
