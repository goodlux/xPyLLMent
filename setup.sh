#!/bin/bash

# xPyLLMent Setup Script
# ASI-ARCH Research System - Autonomous AI Architecture Discovery

echo "🚀 Setting up xPyLLMent - ASI-ARCH Research System"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
echo "📋 Python version: $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
echo "🛠️  Installing xPyLLMent in development mode..."
pip install -e .

# Install development dependencies
echo "🔨 Installing development dependencies..."
pip install -e ".[dev]"

# Create initial configuration
echo "📝 Creating initial configuration..."
if [ ! -f "config.yaml" ]; then
    python -c "
import xpyllment
try:
    xpyllment.create_default_config('config.yaml')
    print('✅ Default configuration created')
except Exception as e:
    print(f'⚠️  Could not create config: {e}')
    print('   Run: xpyllment init')
"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Set up your API keys:"
echo "   export ANTHROPIC_API_KEY='your-key'"
echo "   export OPENAI_API_KEY='your-key'"
echo ""
echo "2. Initialize your research project:"
echo "   xpyllment init"
echo ""
echo "3. Start autonomous research:"
echo "   xpyllment start --generations 5 --experiments 3"
echo ""
echo "4. Monitor progress:"
echo "   xpyllment status"
echo ""
echo "🧠 Ready to revolutionize AI architecture discovery!"
