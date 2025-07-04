from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_API_BASE")
)

def choose_db_from_prompt(prompt: str) -> str:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_ENGINE"),
        messages=[
            {"role": "system", "content": "You are a classifier. Respond only with 'postgres' or 'neo4j'."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().lower()
