from typing import Dict

from django.conf import settings

from apps.core.models import Task

from .service_factory import AgentServiceFactory


class TaskProcessor:
    def __init__(self):
        self.model = settings.AI_MODEL  # e.g., "OpenAI"
        self.api_key = settings.OPENAI_API_KEY

    def process(self, task: Task) -> Dict[str, Any]:
        agent_service = AgentServiceFactory.get_agent_service(self.model, self.api_key)
        if not agent_service:
            raise ValueError(f"AI model '{self.model}' is not supported.")
        return agent_service.process_task(task)
