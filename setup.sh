#!/bin/bash

# Exit on error
set -e

# Function to display usage
usage() {
    echo "Usage: source ./setup.sh [--dev]"
    echo "  --dev    Activates the virtual environment after setup"
}

# 1. Create directory structure
mkdir -p src/processor src/utils tests
touch src/__init__.py src/processor/__init__.py src/utils/__init__.py

# 2. Virtual environment logic
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# 3. Dependency management
source venv/bin/activate
pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    touch requirements.txt
fi

# 4. Handle flags
if [[ "$1" == "--dev" ]]; then
    echo "Environment configured and activated."
else
    # If not in dev mode, deactivate so the script finishes cleanly
    deactivate
    echo "Setup complete. Run 'source venv/bin/activate' to begin."
fi