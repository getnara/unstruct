from langchain.output_parsers import StructuredOutputParser
from llama_index.core.output_parsers import LangchainOutputParser
from llama_index.llms.openai import OpenAI

from apps.core.models import Task

from .base_agent_service import BaseAgentService


class OpenAIDataService(BaseAgentService):
    def get_llm_model_agent(self, task: Task):
        response_schemas = self.load_structured_response_schema(task)
        lc_output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        output_parser = LangchainOutputParser(lc_output_parser)

        # Attach output parser to LLM
        llm = OpenAI(output_parser=output_parser)
        return llm
