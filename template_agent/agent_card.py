from a2a.types import AgentCard, AgentCapabilities, AgentSkill

AGENT_CARD = AgentCard(
    agent_name="template_agent",
    skills=[
        AgentSkill(name="template_params", description="Provide template parameters"),
        AgentSkill(name="template_create", description="Create template component"),
    ],
    capabilities=[AgentCapabilities.ORCHESTRATION],
    description="Template agent for Backstage templates",
    version="0.1.0",
)
