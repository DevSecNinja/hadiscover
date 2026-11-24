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
# (PAGES_URL/coverage.json); if that can't be read, it warns and writes
# nothing.

set -euo pipefail

out_file="${1:?usage: write-coverage-badge.sh <out-file> [line-coverage-percent]}"
percent="${2:-}"

if [[ -z "${percent}" ]]; then
    : "${PAGES_URL:?PAGES_URL is needed to keep the live badge}"
    if curl -fsS --max-time 20 "${PAGES_URL%/}/coverage.json" -o "${out_file}"; then
        echo "Kept the live coverage badge: $(cat "${out_file}")"
    else
        rm -f "${out_file}"
        echo "::warning title=Coverage badge::No coverage.json on ${PAGES_URL}; the badge stays empty until a release deploys one."
    fi
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
echo "Wrote ${out_file}: $(cat "${out_file}")"
