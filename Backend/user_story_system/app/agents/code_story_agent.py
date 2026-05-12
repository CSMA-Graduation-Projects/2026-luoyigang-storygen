from autogen_agentchat.agents import AssistantAgent
from app.config import get_model_client
from app.services.agent_config_service import get_agent_system_prompt


def create_code_story_agent():
    return AssistantAgent(
        name="code_story_agent",
        model_client=get_model_client(),
        system_message=get_agent_system_prompt("code_story"),
    )
