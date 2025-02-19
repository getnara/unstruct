from typing import Optional, Dict
from apps.core.models import ASSET_FILE_TYPE
from .ai_service.base_agent_service import BaseAgentService
#from .ai_service.open_ai_data_service import OpenAIAgentService
from .ai_service.open_ai_data_service import OpenAIAgentService
from .ai_service.gemini_data_service import GeminiAgentService

class AgentServiceFactory:
    _instance: Dict[str, BaseAgentService] = {}
    
    @staticmethod
    def get_agent_service(model: str, api_key: str, file_type: str = None) -> Optional[BaseAgentService]:
        # For PDF documents, always return Gemini service
        if file_type == ASSET_FILE_TYPE.PDF:
            if 'gemini' not in AgentServiceFactory._instance:
                AgentServiceFactory._instance['gemini'] = GeminiAgentService(api_key=api_key)
            return AgentServiceFactory._instance['gemini']
        
        # For all other file types, return OpenAI service
        if 'openai' not in AgentServiceFactory._instance:
            AgentServiceFactory._instance['openai'] = OpenAIAgentService(api_key=api_key)
        return AgentServiceFactory._instance['openai']