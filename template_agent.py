import asyncio
import json
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langgraph import create_react_agent


# Simulated MCP Client to call tools by name
class MCPClient:
    async def call_tool(self, tool_name: str, params: dict) -> str:
        # Simulate async MCP tool calls
        await asyncio.sleep(0.1)
        if tool_name == "get_template_yaml":
            if params.get("template_name", "").lower() == "lambda":
                return """
name: lambda
parameters:
  - name: functionName
    type: string
    description: Name of the Lambda function
  - name: runtime
    type: string
    allowedValues: [python3.9, nodejs14.x, java11]
  - name: memorySize
    type: integer
    default: 128
"""
            return "Template not found."
        elif tool_name == "fetch_template_params":
            if params.get("template_name", "").lower() == "lambda":
                return "functionName, runtime, memorySize"
            return "No parameters found."
        return "Unknown tool"


# Tool that uses MCPClient and LLM for dynamic tool discovery
class TemplateAgentTool(BaseTool):
    name = "TemplateAgentTool"
    description = "Calls MCP tools dynamically based on LLM tool discovery"

    def __init__(self, llm: ChatOpenAI):
        super().__init__()
        self.llm = llm
        self.mcp_client = MCPClient()

    async def _arun(self, user_input: str) -> str:
        # Step 1: Use LLM to decide which MCP tool to call and what input to pass
        discovery_prompt = f"""
You are an intelligent agent that decides which MCP tool to call for the input below.
Available tools:
- get_template_yaml: fetches YAML content of a template
- fetch_template_params: fetches parameter names of a template

Input:
{user_input}

Respond only with JSON in this format:
{{
  "tool_name": "<tool_name>",
  "tool_input": "<input_string>"
}}
"""
        response = await self.llm.agenerate([discovery_prompt])
        try:
            decision = json.loads(response.generations[0][0].text.strip())
            tool_name = decision.get("tool_name")
            tool_input = decision.get("tool_input")
        except Exception as e:
            return f"Error parsing LLM response: {e}\nRaw: {response.generations[0][0].text.strip()}"

        # Step 2: Call the discovered MCP tool
        result = await self.mcp_client.call_tool(tool_name, {"template_name": tool_input})
        return result

    def run(self, user_input: str) -> str:
        return asyncio.run(self._arun(user_input))


def get_template_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [TemplateAgentTool(llm=llm)]
    agent = create_react_agent(llm=llm, tools=tools)
    return agent
