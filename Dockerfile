FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mcp_server/ ./mcp_server/
COPY mcp_client/ ./mcp_client/

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Run the MCP server directly
CMD ["python", "-m", "mcp_server.mcp_server"] 