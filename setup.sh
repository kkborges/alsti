#!/bin/bash

# Setup script for Gemini Code Generator

echo "🚀 Gemini Code Generator - Setup"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "❌ Python 3 not found. Please install Python 3.8+"; exit 1; }
echo "✓ Python 3 found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists. Skipping..."
else
    echo "Creating .env file..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and set your GEMINI_API_KEY"
    echo "   Get your API key at: https://makersuite.google.com/app/apikey"
fi
echo ""

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and set your GEMINI_API_KEY"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run an example: python -m src.main generate examples/simple_calculator.json"
echo ""
