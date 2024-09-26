import json
from typing import Any, Dict, List

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from apps.core.models import ACTION_TYPE, Action, Asset, Task

from .base_agent_service import BaseAgentService


class OpenAIAgentService(BaseAgentService):
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(openai_api_key=openai_api_key, temperature=0)

    def process_task(self, task: Task) -> Dict[str, Any]:
        structured_output = {}
        extraction_actions = task.actions.filter(action_type=ACTION_TYPE.EXTRACTION)
        generation_actions = task.actions.filter(action_type=ACTION_TYPE.GENERATION)

        if extraction_actions.exists():
            structured_output["extractions"] = self.extract_fields(task, extraction_actions)

        if generation_actions.exists():
            structured_output["generations"] = self.generate_contents(task, generation_actions)

        return structured_output

    def extract_fields(self, task: Task, actions: List[Action]) -> Dict[str, Any]:
        results = {}
        for action in actions:
            field_name = action.name  # field_name from Action model
            description = action.description  # Description to aid extraction
            action_results = []
            for asset in task.assets.all():
                prompt = self.construct_extraction_prompt(field_name, description, asset)
                response = self.llm(prompt)
                parsed_response = self.parse_response(response)
                action_results.append(
                    {
                        "asset": asset.name,
                        "data": parsed_response,
                        "source": asset.url,
                    }
                )
            results[field_name] = action_results
        return results

    def generate_contents(self, task: Task, actions: List[Action]) -> Dict[str, str]:
        content_results = {}
        for action in actions:
            prompt = action.description  # Generation prompt from Action model
            response = self.llm(prompt)
            content_results[action.name] = response
        return content_results

    def construct_extraction_prompt(self, field_name: str, description: str, asset: Asset) -> str:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an assistant that extracts specific fields from documents."),
                (
                    "human",
                    f"""
                Extract the following information from the given document:

                Field: {field_name}
                Description: {description}

                For each extracted field, also provide:
                1. A confidence score between 0 and 1, where 1 is highest confidence.
                2. A reference to where in the document the information was found (e.g., "Page 3, Paragraph 2").

                Document:
                {asset.get_document_from_asset()}

                Respond in the following JSON format:
                {{
                    "{field_name}": "<extracted value>",
                    "{field_name}_confidence": <confidence score>,
                    "{field_name}_reference": "<reference>"
                }}
            """,
                ),
            ]
        )
        return prompt_template.format_prompt().to_string()

    def parse_response(self, response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response"}
