from typing import Optional

from .ai_service.base_agent_service import BaseAgentService
#from .ai_service.open_ai_data_service import OpenAIAgentService
from .ai_service.open_ai_data_service import OpenAIAgentService


class AgentServiceFactory:
    @staticmethod
    def get_agent_service(model: str, api_key: str) -> Optional[BaseAgentService]:
        if model.lower() == "openai":
            return OpenAIAgentService(api_key=api_key)
        # Future models can be added here
        return None