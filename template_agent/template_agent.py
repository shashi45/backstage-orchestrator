import requests

class TemplateAgent:
    def __init__(self, backstage_url: str):
        self.backstage_url = backstage_url.rstrip("/")

    def get_template_info(self, template_name: str):
        url = f"{self.backstage_url}/api/catalog/entities?filter=kind=Template"
        resp = requests.get(url)
        resp.raise_for_status()

        templates = resp.json()
        for t in templates:
            if t["metadata"]["name"].lower() == template_name.lower():
                return {
                    "template_name": t["metadata"]["name"],
                    "description": t["metadata"].get("description", "No description."),
                    "owner": t["spec"].get("owner", "Unknown"),
                    "status": "Available"
                }
        return {"error": f"Template {template_name} not found"}
