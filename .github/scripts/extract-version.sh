#!/bin/bash
# Extract version from git reference or workflow input
# Usage: extract-version.sh <event_name> <input_version_or_pr_number> <git_ref>

set -e

EVENT_NAME="${1}"
INPUT_VERSION="${2}" # Can be: PR number for pull_request, version for workflow_dispatch, or empty
GIT_REF="${3}"

if [ "$EVENT_NAME" = "pull_request" ]; then
    # For PRs, use format: pr.<number>.<short-sha>
    if [ -z "$INPUT_VERSION" ]; then
        echo "Error: PR number required for pull_request event"
        exit 1
    fi
    SHORT_SHA=$(git rev-parse --short HEAD)
    VERSION="pr.${INPUT_VERSION}.${SHORT_SHA}"
    VERSION_TAG="pr-${INPUT_VERSION}"
elif [ "$EVENT_NAME" = "workflow_dispatch" ]; then
    VERSION="${INPUT_VERSION}"
    VERSION_TAG="v${VERSION}"
elif [ -n "$GIT_REF" ]; then
    # Extract version from tag (e.g., v1.0.0 -> 1.0.0)
    VERSION=${GIT_REF#refs/tags/v}
    VERSION_TAG=${GIT_REF#refs/tags/}
else
    echo "Error: Invalid arguments for event $EVENT_NAME"
    exit 1
fi

echo "version=${VERSION}"
echo "version_tag=${VERSION_TAG}"
