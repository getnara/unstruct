import json
import os
import logging
from typing import Any, Dict, List

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from apps.core.models import Action, Asset, Task
from apps.core.models.action import ACTION_TYPE

from .base_agent_service import BaseAgentService

logger = logging.getLogger(__name__)

# Define the system and human message templates
system_template = "You are an assistant that extracts specific fields from documents."
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

human_template = """
Extract the following information from the given document:

Field: {field_name}
Description: {description}

For each extracted field, also provide:
1. A confidence score between 0 and 1, where 1 is highest confidence.
2. A reference to where in the document the information was found (e.g., "Page 3, Paragraph 2").

Document: {document}

Respond in the following JSON format:
{{
    "{field_name}": "<extracted value>",
    "{field_name}_confidence": <confidence score>,
    "{field_name}_reference": "<reference>"
}}
"""
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

# Create the chat prompt template
chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

class OpenAIAgentService(BaseAgentService):
    def __init__(self, api_key: str):
        if not api_key:
            print("OpenAI API key is not set in the environment variables.")
            raise ValueError("OpenAI API key is not set in the environment variables.")
        self.llm = ChatOpenAI(openai_api_key=api_key, temperature=0)

    def process_task(self, task: Task) -> Dict[str, any]:
        structured_output = {}
        try:
            extraction_actions = task.actions.filter(action_type=ACTION_TYPE.EXTRACTION)
            generation_actions = task.actions.filter(action_type=ACTION_TYPE.GENERATION)

            if extraction_actions.exists():
                structured_output["extractions"] = self.extract_fields(task, extraction_actions)

            if generation_actions.exists():
                structured_output["generations"] = self.generate_contents(task, generation_actions)

        except Exception as e:
            print(f"Error processing task {task.id}: {e}")
            structured_output["error"] = str(e)

        return structured_output

    def extract_fields(self, task: Task, actions: List[Action]) -> Dict[str, any]:
        results = {}
        try:
            for action in actions:
                field_name = action.output_column_name
                description = action.description
                action_results = []
                for asset in task.assets.all():
                    prompt = self.construct_extraction_prompt(field_name, description, asset)
                    print(prompt)
                    response = self.llm.invoke(prompt)  # Use invoke instead of __call__
                    print(response)
                    parsed_response = self.parse_response(response.content)  # Access the content attribute
                    action_results.append(
                        {
                            "asset": asset.name,
                            "data": parsed_response,
                            "source": asset.url,
                        }
                    )
                results[field_name] = action_results
        except Exception as e:
            print(f"Error extracting fields for task {task.id}: {e}")
            results["error"] = str(e)

        return results

    def generate_contents(self, task: Task, actions: List[Action]) -> Dict[str, str]:
        content_results = {}
        try:
            for action in actions:
                prompt = action.description
                response = self.llm.invoke(prompt)  # Use invoke instead of __call__
                print(response)
                content_results[action.output_column_name] = response.content  # Access the content attribute
        except Exception as e:
            print(f"Error generating contents for task {task.id}: {e}")
            content_results["error"] = str(e)

        return content_results

    def construct_extraction_prompt(self, field_name: str, description: str, asset: Asset) -> str:
        document = asset.get_document_from_asset()
        if not field_name or not description or not document:
            raise ValueError("Field name, description, or document content is empty.")
        try:
            # Use the chat prompt template to format the prompt
            prompt = chat_prompt.format_prompt(
                field_name=field_name,
                description=description,
                document=document
            )
            print("Prompt template:", prompt)
            return prompt.to_string()  # Convert PromptValue to string
        except Exception as e:
            print(f"Error constructing extraction prompt: {e}")
            raise  # Re-raise the exception instead of returning an empty string

    def parse_response(self, response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing response: {e}")
            return {"error": "Invalid JSON response"}

def sanitize_document_content(document: str) -> str:
    # Remove any unwanted characters or formatting
    return document.replace("\n", " ").strip()
