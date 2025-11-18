#!/bin/bash
# WorldWind Python - Launch Script

echo "=========================================="
echo "WorldWind Python - VisPy 3D Globe"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python -c "import vispy" 2>/dev/null; then
    echo "Dependencies not found. Installing..."
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "Launching WorldWind Python..."
echo ""

# Run the application
python worldwind.py

# Deactivate virtual environment
deactivate
