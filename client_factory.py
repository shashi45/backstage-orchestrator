from a2a.client import A2AClient

class ClientFactory:
    def __init__(self):
        self.clients = {}

    async def create(self, skill_name: str):
        if skill_name not in self.clients:
            if skill_name == "template_params":
                url = "http://127.0.0.1:8001"
            elif skill_name == "orchestrator":
                url = "http://127.0.0.1:8000"
            else:
                raise ValueError(f"Unknown skill: {skill_name}")
            self.clients[skill_name] = A2AClient(server_url=url)
        return self.clients[skill_name]
