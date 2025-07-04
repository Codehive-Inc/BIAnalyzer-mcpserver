import requests

BASE_URL = "http://localhost:8000/process"

def run():
    print("🔗 MCP Client connected to server")

    while True:
        prompt = input("📝 Enter prompt (or 'exit'): ").strip()
        if prompt.lower() == "exit":
            break

        response = requests.post(BASE_URL, json={"prompt": prompt})

        try:
            print("✅ Response:", response.json())
        except Exception:
            print("❌ Server returned non-JSON response:", response.text)

if __name__ == "__main__":
    run()
