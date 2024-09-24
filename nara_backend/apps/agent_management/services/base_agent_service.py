from llama_index.core import ServiceContext, VectorStoreIndex, set_global_service_context
from llama_index.core.schema import ResponseSchema

from apps.core.models.task import Task


class BaseAgentService:
    def load_documents(self, task: Task):
        """
        Reads the documents of each Asset
        using the DocumentReader class from llama_index .
        """
        all_documents = []
        for asset in task.assets.all():
            document = asset.get_document_from_asset()
            all_documents.extend(document)

        return all_documents

    def load_structured_response_schema(self, task: Task):
        response_schemas = []
        for action in task.actions.all():
            response_schemas.append(
                ResponseSchema(
                    name=action.name,
                    description=action.description,
                ),
            )
        response_schemas.append(
            ResponseSchema(
                name="Embed Location",
                description="This is the embed location of the response",
            ),
        )
        return response_schemas

    def get_llm_model_agent(self, task: Task):
        pass

    def get_structured_output(self, task: Task):
        """
        Get the structured output from the task.
        """
        if not task:
            return {}
        index = self.create_index(task)
        task_system_prompt = task.system_prompt
        llm = self.get_llm_model_agent(task)

        # obtain a structured response
        query_engine = index.as_query_engine(llm=llm)
        response = query_engine.query(
            "You need to extract the response output from all the files that are ingested in to the vector index. You also need to give me the embed and the pointer to the page where the response is located?",
            task_system_prompt,
        )
        return response

    def create_document_index(self, task: Task):
        """
        Creates a Vector index from the documents loaded from Confluence.
        """
        service_context = ServiceContext.from_defaults(chunk_size=1024)
        set_global_service_context(service_context)
        document_index = VectorStoreIndex.from_documents(self.load_documents(task))
        return document_index

    def load_query_engine(self):
        """
        Create the query engine from the index.
        """
        document_index = self.create_document_index()
        return document_index.as_query_engine()
