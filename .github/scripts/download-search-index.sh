#!/usr/bin/env bash
# Downloads the latest static search index for frontend builds.

set -euo pipefail

SEARCH_INDEX_PATH="${SEARCH_INDEX_PATH:-frontend/public/data/search-index.json}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:-DevSecNinja/hadiscover}"
SEARCH_INDEX_URL="${SEARCH_INDEX_URL:-https://github.com/${GITHUB_REPOSITORY}/releases/download/db-latest/search-index.json}"

mkdir -p "$(dirname "${SEARCH_INDEX_PATH}")"

if curl -fsSL "${SEARCH_INDEX_URL}" -o "${SEARCH_INDEX_PATH}"; then
	echo "Downloaded search index from ${SEARCH_INDEX_URL}"
	exit 0
fi

echo "Warning: could not download ${SEARCH_INDEX_URL}; writing empty search index."
cat >"${SEARCH_INDEX_PATH}" <<EOF
{"version":1,"generated_at":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","statistics":{"total_repositories":0,"total_automations":0,"last_indexed_at":null,"repo_star_count":0},"automations":[]}
EOF
