#!/bin/bash
# Create a sample SQLite database from the hadiscover models for schema diagram generation

set -e

echo "Creating sample database from models..."

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Change to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment if it exists, otherwise create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create a temporary Python script to generate the database
cat > /tmp/create_db.py << 'EOF'
"""Generate sample SQLite database from SQLAlchemy models."""
from app.models.database import Base
from sqlalchemy import create_engine

# Create engine and database
engine = create_engine('sqlite:///sample_schema.db')
Base.metadata.create_all(engine)

print("Sample database created successfully at backend/sample_schema.db")
EOF

# Set PYTHONPATH and run the script
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
python /tmp/create_db.py

# Clean up
rm /tmp/create_db.py

echo "Database creation complete."
