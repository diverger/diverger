#!/bin/bash
# Quick test script for holiday color detection

echo "🎨 GitHub Holiday Color Detection Demo"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt 2>/dev/null || {
    pip install -q requests beautifulsoup4 lxml
}

echo ""
echo "🔍 Testing color detection..."
echo ""

# Run the test script
python3 test_holiday_detection.py "$@"

echo ""
echo "✅ Test complete!"
echo ""
echo "💡 Tip: Run with a username argument:"
echo "   ./demo.sh your-github-username"
