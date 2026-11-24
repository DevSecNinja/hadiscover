#!/usr/bin/env bash
#
# Writes the coverage badge data for shields.io's endpoint badge
# (https://shields.io/badges/endpoint-badge) into the Pages site, so the
# README badge reads https://<site>/coverage.json.
#
# Usage: write-coverage-badge.sh <out-file> [line-coverage-percent]
#
# With a percentage (the test-report action's line-coverage output), it
# writes the badge from it. Without one, as in the daily search-index
# rebuild that runs no tests, it keeps the badge of the live site
# (PAGES_URL/coverage.json). A 404 means no badge yet: it warns and writes
# nothing. Any other failure stops the job, so a short outage can't make the
# deploy drop the live badge.

set -euo pipefail

out_file="${1:?usage: write-coverage-badge.sh <out-file> [line-coverage-percent]}"
percent="${2:-}"

if [[ -z "${percent}" ]]; then
    : "${PAGES_URL:?PAGES_URL is needed to keep the live badge}"
    url="${PAGES_URL%/}/coverage.json"
    if ! status="$(curl -sS --max-time 20 --retry 3 -o "${out_file}" -w '%{http_code}' "${url}")"; then
        # A non-zero exit can follow a 200 header (timeout, truncated body).
        status="curl error"
    fi
    case "${status}" in
    200)
        echo "Kept the live coverage badge:"
        cat "${out_file}"
        ;;
    404)
        rm -f "${out_file}"
        echo "::warning title=Coverage badge::No coverage.json on ${PAGES_URL}; the badge stays empty until a release deploys one."
        ;;
    *)
        rm -f "${out_file}"
        echo "::error title=Coverage badge::Could not read ${url} (${status}); stopping so this deploy doesn't drop the live badge."
        exit 1
        ;;
    esac
    exit 0
fi

if [[ ! "${percent}" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
    echo "::error title=Coverage badge::Not a percentage: '${percent}'"
    exit 1
fi

color="$(awk -v p="${percent}" 'BEGIN {
    if (p >= 90) print "brightgreen"
    else if (p >= 80) print "green"
    else if (p >= 70) print "yellowgreen"
    else if (p >= 60) print "yellow"
    else if (p >= 50) print "orange"
    else print "red"
}')"
printf '{"schemaVersion":1,"label":"coverage","message":"%s%%","color":"%s"}\n' "${percent}" "${color}" >"${out_file}"
echo "Wrote ${out_file}:"
cat "${out_file}"
