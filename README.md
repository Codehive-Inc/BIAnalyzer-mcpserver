# **Classifier MCP Server**

## Steps to run:
### 1. Spin up neo4j and postgres docker containers:  
      docker run -d --name pgdb -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=mcp_db -p 5432:5432 postgres:15  
      docker run -d --name neo4jdb -e NEO4J_AUTH=neo4j/test12345 -p 7474:7474 -p 7687:7687 neo4j:5    

### 2. Install Requirements:
      pip install -r requirements.txt 

### 3. Run the mcp server:  
     cd mcp_server  
     uvicorn main:app --reload --port 8000  
  
### 4. Run the mcp client:  
     cd mcp_client  
     python client.py  
   
### 5. Execution 
     Type prompt in client. Based on this openai will decide whether to access neo4j db or postgres db
