#!/bin/bash

# Sales Chatbot Setup Script

echo "🚀 Setting up Sales Data Chatbot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit the .env file and add your Anthropic API key!"
    echo "   Get your API key from: https://console.anthropic.com/"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and add your ANTHROPIC_API_KEY"
echo "   2. Activate the virtual environment: source venv/bin/activate"
echo "   3. Run the app: streamlit run app.py"
echo ""
echo "🎉 Happy analyzing!"
