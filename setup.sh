#!/bin/bash

# Setup script for AI RAG Chatbot

echo "🚀 Setting up AI RAG Chatbot..."

# Check Python version
echo "📌 Checking Python version..."
python3 --version

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/pdfs
mkdir -p vectorstore

# Copy .env.example to .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual API keys"
fi

# Check if client_secret.json exists
if [ ! -f client_secret.json ]; then
    echo "⚠️  client_secret.json not found!"
    echo "   Please download it from Google Cloud Console and place it in the root directory"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Add your client_secret.json from Google Cloud Console"
echo "3. Place PDF files in data/pdfs/"
echo "4. Run 'python ingest.py' to process PDFs"
echo "5. Start Redis: 'redis-server'"
echo "6. Start the app: 'uvicorn app15_book:app --reload'"
echo ""
echo "Happy coding! 🎉"
