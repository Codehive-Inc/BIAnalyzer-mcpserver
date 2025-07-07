from openai import AzureOpenAI
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required environment variables
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_API_BASE = os.getenv("AZURE_API_BASE")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION", "2023-05-15")

# Check for required environment variables
if not all([AZURE_API_KEY, AZURE_API_BASE, AZURE_DEPLOYMENT]):
    missing = []
    if not AZURE_API_KEY:
        missing.append("AZURE_API_KEY")
    if not AZURE_API_BASE:
        missing.append("AZURE_API_BASE")
    if not AZURE_DEPLOYMENT:
        missing.append("AZURE_DEPLOYMENT")
    print(f"Error: Missing required environment variables: {', '.join(missing)}")
    print("Please set these variables in your .env file or environment.")
    sys.exit(1)

# Initialize Azure OpenAI client
try:
    client = AzureOpenAI(
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
        azure_endpoint=AZURE_API_BASE
    )
except Exception as e:
    print(f"Error initializing Azure OpenAI client: {e}")
    sys.exit(1)


def choose_db_from_prompt(prompt: str) -> str:
    """Classify a prompt to determine which database to use (postgres or neo4j)
    
    Args:
        prompt: The user prompt to classify
        
    Returns:
        str: Either 'postgres' or 'neo4j'
        
    Raises:
        Exception: If the API call fails
    """
    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT,
            messages=[
                {"role": "system", "content": "You are a classifier. Respond only with 'postgres' or 'neo4j'."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content.strip().lower()
        
        # Validate response is either postgres or neo4j
        if result not in ["postgres", "neo4j"]:
            print(f"Warning: Unexpected classification result: {result}. Defaulting to postgres.")
            return "postgres"
            
        return result
    except Exception as e:
        print(f"Error classifying prompt: {e}")
        # Default to postgres in case of error
        return "postgres"
