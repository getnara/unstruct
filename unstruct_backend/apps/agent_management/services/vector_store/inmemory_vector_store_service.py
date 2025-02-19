from typing import Any, Dict, List


class InMemoryVectorStore(BaseVectorStore):
    def __init__(self):
        self.documents = []

    def add_documents(self, documents: List[Dict[str, Any]]):
        self.documents.extend(documents)

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.documents

    def search(self, query: str, k: int = 1) -> List[Dict[str, Any]]:
        # Implement a simple search function (for demonstration purposes)
        return sorted(self.documents, key=lambda x: x["page_content"].count(query), reverse=True)[:k]
