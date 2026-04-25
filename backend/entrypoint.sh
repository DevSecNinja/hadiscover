#!/bin/bash
set -e

# Entrypoint script for hadiscover backend container
# Supports running as a web server or as a one-time indexing job

# Optionally download a pre-built database on startup.
# Set DB_DOWNLOAD_URL to the URL of a gzip-compressed SQLite
# database file. The database is re-downloaded on every container
# start so that restarts pick up the latest version automatically.
# Example:
#   DB_DOWNLOAD_URL=https://github.com/DevSecNinja/hadiscover/\
#     releases/download/db-latest/hadiscover.db.gz
if [ -n "${DB_DOWNLOAD_URL:-}" ]; then
	echo "Downloading pre-built database from ${DB_DOWNLOAD_URL}..."
	mkdir -p /app/data
	if python3 -c "
import urllib.request, gzip, shutil, sys
url = sys.argv[1]
try:
    with urllib.request.urlopen(url) as response, \
         gzip.open(response) as gz_file, \
         open('/app/data/hadiscover.db', 'wb') as f:
        shutil.copyfileobj(gz_file, f)
except Exception as e:
    print('Error downloading database:', e, file=sys.stderr)
    sys.exit(1)
" "${DB_DOWNLOAD_URL}"; then
		echo "✓ Pre-built database downloaded successfully"
	else
		echo "Warning: Failed to download pre-built database. Continuing with existing or empty database."
		rm -f /app/data/hadiscover.db
	fi
fi

if [ "$1" = "index-now" ]; then
	echo "Running indexing job..."
	exec python -m app.cli index-now
else
	echo "Starting web server..."
	exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
