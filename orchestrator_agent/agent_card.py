from a2a.types import AgentCard, AgentCapabilities, AgentSkill

AGENT_CARD = AgentCard(
    agent_name="orchestrator_agent",
    skills=[AgentSkill(name="orchestrator", description="Orchestrator skill")],
    capabilities=[AgentCapabilities.CONVERSATIONAL, AgentCapabilities.ORCHESTRATION],
    description="Orchestrator agent for Backstage templates",
    version="0.1.0",
)
