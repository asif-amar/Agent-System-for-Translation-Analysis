#!/bin/bash

# Translation Quality Analysis System - UI Launcher
# This script launches the Streamlit web interface

set -e

echo "========================================="
echo "Translation Quality Analysis System - UI"
echo "========================================="
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Dependencies installed."
fi

# Launch Streamlit UI
echo ""
echo "Launching UI..."
echo "The interface will open in your browser at http://localhost:8501"
echo ""
echo "To stop the UI, press Ctrl+C"
echo ""

streamlit run src/ui/app.py
