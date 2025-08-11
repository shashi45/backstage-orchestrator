from a2a.executor import BaseExecutor

class OrchestratorExecutor(BaseExecutor):
    async def execute(self, request):
        # Echo input for now
        input_text = request.get("input", "")
        return {"response": f"Orchestrator received: {input_text}"}
