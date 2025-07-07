# Configuration Guide

## Setup Options

### Option 1: Databases in Docker + FastAPI Locally (Development)
- **File**: `docker-compose-db.yml`
- **Use case**: Local development
- **Database access**: `localhost:5432` (PostgreSQL), `localhost:7688` (Neo4j)

### Option 2: Everything in Docker (Production-like)
- **File**: `docker-compose.yml`
- **Use case**: Production or testing full stack
- **Database access**: Internal container communication

## Environment Variables

### Azure OpenAI (Required for both options)
```
AZURE_API_KEY=your_azure_openai_api_key_here
AZURE_API_BASE=https://your-resource-name.openai.azure.com/
AZURE_ENGINE=your-deployment-name
```

### Database Configuration

#### For Local Development (docker-compose-db.yml)
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mcp_db
POSTGRES_USER=mcp_user
POSTGRES_PASSWORD=secret

NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=test12345
```

#### For Full Docker Stack (docker-compose.yml)
The MCP server container uses these internal values:
```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mcp_db
POSTGRES_USER=mcp_user
POSTGRES_PASSWORD=secret

NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=test12345
```

## Port Mappings

### Local Development
- PostgreSQL: `localhost:5432`
- Neo4j HTTP: `localhost:7475`
- Neo4j Bolt: `localhost:7688`
- FastAPI: `localhost:8000`

### Full Docker Stack
- PostgreSQL: `localhost:5432`
- Neo4j HTTP: `localhost:7475`
- Neo4j Bolt: `localhost:7688`
- FastAPI: `localhost:8000`

## Database Credentials

Both setups use the same database credentials:
- **PostgreSQL**: `mcp_user` / `secret`
- **Neo4j**: `neo4j` / `test12345` 