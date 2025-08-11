# test_client.py
import asyncio
import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import SendMessageRequest, MessageSendParams
from uuid import uuid4

async def main():
    send_message_payload = {
        "message": {
            "role": "user",
            "parts": [
                {"kind": "text", "text": "I want to create a lambda template"}
            ],
            "messageId": uuid4().hex,
        }
    }
    base_url = "http://127.0.0.1:9000"
    async with httpx.AsyncClient() as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        card = await resolver.get_agent_card()
        client = A2AClient(agent_card=card, httpx_client=httpx_client)
        send_req = SendMessageRequest(id=str(uuid4()), params=MessageSendParams(**send_message_payload))
        response = await client.send_message(send_req)
        print("Response:", response)

if __name__ == "__main__":
    asyncio.run(main())
