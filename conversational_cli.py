import asyncio
from a2a.client import A2AClient

async def main():
    orchestrator_client = A2AClient(server_url="http://127.0.0.1:8000")
    prompt = input("User> ")
    response = await orchestrator_client.send({"input": prompt})
    print("Orchestrator>", response)

if __name__ == "__main__":
    asyncio.run(main())
