from abc import ABC, abstractmethod
from typing import Any, Dict

from apps.core.models import Task


class BaseAgentService(ABC):
    @abstractmethod
    def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Process the given task and return structured output.
        """
