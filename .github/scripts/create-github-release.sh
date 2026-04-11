#!/usr/bin/env bash
# Creates a GitHub Release using the gh CLI, combining a custom body with
# auto-generated release notes.
#
# Required environment variables:
#   VERSION_TAG         - Git tag name (e.g. v1.2.3)
#   VERSION             - Human-readable version string (e.g. 1.2.3)
#   IS_PRERELEASE       - "true" or "false"
#   REGISTRY            - Container registry hostname (e.g. ghcr.io)
#   BACKEND_IMAGE_NAME  - Backend image name (e.g. owner/repo/backend)
#   FRONTEND_IMAGE_NAME - Frontend image name (e.g. owner/repo/frontend)
#   GITHUB_TOKEN        - Token with contents:write permission (auto-set in Actions)
#   GITHUB_REPOSITORY   - owner/repo (auto-set in Actions)

set -euo pipefail

# Fetch auto-generated release notes from GitHub API
GENERATED_NOTES=$(gh api \
	--method POST \
	"/repos/${GITHUB_REPOSITORY}/releases/generate-notes" \
	-f "tag_name=${VERSION_TAG}" \
	--jq '.body')

# Write the full release notes to a temp file
RELEASE_NOTES_FILE=$(mktemp)
trap 'rm -f "${RELEASE_NOTES_FILE}"' EXIT

cat >"${RELEASE_NOTES_FILE}" <<EOF
## Release ${VERSION}

### Docker Images

**Backend:**
\`\`\`bash
docker pull ${REGISTRY}/${BACKEND_IMAGE_NAME}:${VERSION}
\`\`\`

**Frontend:**
\`\`\`bash
docker pull ${REGISTRY}/${FRONTEND_IMAGE_NAME}:${VERSION}
\`\`\`

### Using Docker Compose

Update your \`docker-compose.yml\` to use the released images:

\`\`\`yaml
services:
  backend:
    image: ${REGISTRY}/${BACKEND_IMAGE_NAME}:${VERSION}
  frontend:
    image: ${REGISTRY}/${FRONTEND_IMAGE_NAME}:${VERSION}
\`\`\`

${GENERATED_NOTES}
EOF

# Build gh CLI argument list
GH_ARGS=(
	"${VERSION_TAG}"
	--title "${VERSION}"
	--notes-file "${RELEASE_NOTES_FILE}"
)

if [[ "${IS_PRERELEASE}" == "true" ]]; then
	GH_ARGS+=(--prerelease)
fi

gh release create "${GH_ARGS[@]}"
