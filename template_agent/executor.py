from a2a.executor import BaseExecutor

class TemplateAgentExecutor(BaseExecutor):
    async def execute(self, request):
        template_name = request.get("template_name", "")
        if template_name == "lambda":
            return {
                "params": ["component_name", "runtime", "handler", "timeout"]
            }
        return {"params": []}
