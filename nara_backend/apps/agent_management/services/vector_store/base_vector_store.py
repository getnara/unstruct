from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: List[Dict[str, Any]]):
        pass

    @abstractmethod
    def get_all_documents(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def search(self, query: str, k: int = 1) -> List[Dict[str, Any]]:
        pass
