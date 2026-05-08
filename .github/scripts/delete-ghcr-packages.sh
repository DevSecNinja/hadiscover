#!/usr/bin/env bash
# Deletes the legacy hadiscover GHCR packages.

set -euo pipefail

OWNER="${GITHUB_REPOSITORY_OWNER:?GITHUB_REPOSITORY_OWNER is required}"
TOKEN="${GITHUB_TOKEN:?GITHUB_TOKEN is required}"
API_VERSION="2022-11-28"

delete_package() {
	local package_name="$1"
	local encoded_name="$2"
	local url="https://api.github.com/users/${OWNER}/packages/container/${encoded_name}"
	local status

	status=$(curl -sS -o /tmp/ghcr-package.json -w "%{http_code}" \
		-H "Accept: application/vnd.github+json" \
		-H "Authorization: Bearer ${TOKEN}" \
		-H "X-GitHub-Api-Version: ${API_VERSION}" \
		"${url}")

	case "${status}" in
	200)
		echo "Deleting GHCR package ${package_name}..."
		;;
	404)
		echo "GHCR package ${package_name} is already absent."
		return 0
		;;
	*)
		echo "Error: could not inspect package ${package_name}; status ${status}."
		cat /tmp/ghcr-package.json
		return 1
		;;
	esac

	status=$(curl -sS -o /tmp/ghcr-delete.json -w "%{http_code}" \
		-X DELETE \
		-H "Accept: application/vnd.github+json" \
		-H "Authorization: Bearer ${TOKEN}" \
		-H "X-GitHub-Api-Version: ${API_VERSION}" \
		"${url}")

	case "${status}" in
	204 | 404)
		echo "Deleted GHCR package ${package_name}."
		;;
	*)
		echo "Error: could not delete package ${package_name}; status ${status}."
		cat /tmp/ghcr-delete.json
		return 1
		;;
	esac
}

delete_package "hadiscover/backend" "hadiscover%2Fbackend"
delete_package "hadiscover/frontend" "hadiscover%2Ffrontend"
