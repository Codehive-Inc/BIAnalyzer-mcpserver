#!/bin/bash

echo "🚀 Setting up MCP Server Development Environment"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Start databases
echo "📦 Starting databases with Docker..."
docker compose -f docker-compose-db.yml up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.sample .env
    echo "⚠️  Please edit .env file with your Azure OpenAI credentials before running the server"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Azure OpenAI credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the server: cd mcp_server && uvicorn main:app --reload --port 8000"
echo ""
echo "Databases are running on:"
echo "- PostgreSQL: localhost:5432"
echo "- Neo4j: localhost:7475 (HTTP) / localhost:7688 (Bolt)" 