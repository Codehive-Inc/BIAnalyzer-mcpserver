# **Classifier MCP Server**

## Quick Start with Docker (Recommended)

### Option 1: Databases in Docker + FastAPI Locally (Recommended for Development)
```bash
# Quick setup (recommended)
./setup.sh

# Or manual setup:
# 1. Start only the databases
docker compose -f docker-compose-db.yml up -d

# 2. Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp env.sample .env
# Edit .env with your Azure OpenAI credentials

# 4. Run FastAPI server locally
cd mcp_server
uvicorn main:app --reload --port 8000
```

### Option 2: Everything in Docker (Production-like)
```bash
# Start all services (PostgreSQL, Neo4j, and MCP Server)
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

### Using Docker Compose with client:
```bash
# Start all services including the client
docker compose --profile client up -d

# Run client interactively
docker compose run --rm mcp_client
```

## Manual Setup (Alternative)

### 1. Spin up neo4j and postgres docker containers:  
```bash
docker run -d --name pgdb -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=mcp_db -p 5432:5432 postgres:15  
docker run -d --name neo4jdb -e NEO4J_AUTH=neo4j/test12345 -p 7474:7474 -p 7687:7687 neo4j:5    
```

### 2. Install Requirements:
```bash
pip install -r requirements.txt 
```

### 3. Run the mcp server:  
```bash
cd mcp_server  
uvicorn main:app --reload --port 8000  
```

### 4. Run the mcp client:  
```bash
cd mcp_client  
python client.py  
```

## Execution 
Type prompt in client. Based on this openai will decide whether to access neo4j db or postgres db

## Environment Variables

Copy `env.sample` to `.env` and configure the following variables:

### Required:
- `AZURE_API_KEY`: Your Azure OpenAI API key
- `AZURE_API_BASE`: Your Azure OpenAI endpoint URL
- `AZURE_ENGINE`: Your Azure OpenAI deployment name

### Optional (defaults provided):
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

## Docker Services

- **PostgreSQL**: Available on port 5432
- **Neo4j**: Available on ports 7475 (HTTP) and 7688 (Bolt)
- **MCP Server**: Available on port 8000
- **Health Check**: Available at http://localhost:8000/health
