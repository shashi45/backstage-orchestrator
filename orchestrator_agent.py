import asyncio
from langchain.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langgraph import create_react_agent, Workflow
from template_agent import get_template_agent


# Tool wrapper to call TemplateAgent from orchestrator
class TemplateAgentCallerTool(BaseTool):
    name = "TemplateAgentCallerTool"
    description = "Calls TemplateAgent to fetch template data"

    async def _arun(self, query: str) -> str:
        template_agent = get_template_agent()
        return await template_agent.arun(query)

    def run(self, query: str) -> str:
        return asyncio.run(self._arun(query))


def get_orchestrator_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [TemplateAgentCallerTool()]
    agent = create_react_agent(llm=llm, tools=tools)
    return agent


def build_orchestrator_workflow(agent):
    workflow = Workflow(name="orchestrator_workflow")

    @workflow.step()
    async def extract_template_name(context):
        user_input = context["user_input"]
        prompt = f"Extract the template name from this user input: '{user_input}'. Reply with only the template name."
        template_name = await agent.arun(prompt)
        context["template_name"] = template_name.strip().lower()

    @workflow.step()
    async def fetch_template_yaml(context):
        if not context.get("template_name"):
            context["error"] = "Template name not found."
            return
        prompt = f"Please fetch template YAML for template '{context['template_name']}'"
        yaml_content = await agent.arun(prompt)
        context["template_yaml"] = yaml_content

    @workflow.step()
    async def fetch_parameters(context):
        if not context.get("template_name"):
            context["error"] = "Template name missing; cannot fetch parameters."
            return
        prompt = f"Please fetch parameters list for template '{context['template_name']}'"
        params = await agent.arun(prompt)
        context["parameters"] = params

    @workflow.step()
    async def present_parameters(context):
        if context.get("error"):
            context["response"] = f"Error: {context['error']}"
            return

        response = (
            f"You requested template '{context['template_name']}'.\n\n"
            f"Template YAML:\n{context['template_yaml']}\n\n"
            f"Parameters you need to provide: {context['parameters']}\n"
        )
        context["response"] = response

    @workflow.step()
    async def prompt_for_missing_params(context):
        required = [p.strip() for p in context["parameters"].split(",")]
        provided = context.get("provided_params", {})

        missing = [p for p in required if p not in provided]
        if not missing:
            context["all_params_collected"] = True
            return

        param_to_ask = missing[0]
        # For demo, use input(); in real system, replace with async user prompt interface
        answer = input(f"Please provide value for parameter '{param_to_ask}': ")
        provided[param_to_ask] = answer
        context["provided_params"] = provided
        context["all_params_collected"] = False

    workflow.set_sequence(
        [
            extract_template_name,
            fetch_template_yaml,
            fetch_parameters,
            present_parameters,
            # Run this step repeatedly until all params are collected
            prompt_for_missing_params,
        ]
    )

    return workflow
