import json
import logging
from typing import Any, Dict, List, Union
import mimetypes
import PIL.Image
from io import BytesIO

from google.generativeai import GenerativeModel
import google.generativeai as genai
from langchain_core.messages import HumanMessage

from apps.core.models import Action, Asset, Task, ASSET_FILE_TYPE
from apps.core.models.action import ACTION_TYPE
from .base_agent_service import BaseAgentService
from .vector_store import VectorStore
import os

logger = logging.getLogger(__name__)

# Define templates similar to OpenAI but adapted for Gemini's style
DOCUMENT_SYSTEM_TEMPLATE = """You are an assistant that extracts specific fields from documents. 
Extract information accurately and provide confidence scores and references."""

DOCUMENT_HUMAN_TEMPLATE = """
Extract the following information from the given document:

Field: {field_name}
Description: {description}

Provide:
1. The extracted value
2. A confidence score (0-1)
3. Reference location in document

Respond in JSON format:
{{
    "{field_name}": "<extracted value>",
    "{field_name}_confidence": <confidence score>,
    "{field_name}_reference": "<reference>"
}}
"""

# Similar templates for other content types...

class GeminiExtractionHandler:
    """Base class for handling different asset types in Gemini."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> str:
        raise NotImplementedError


class GeminiDocumentHandler(GeminiExtractionHandler):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = dict()

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> Dict:
        try:
            if asset.id in self.cache:
                pdf_file = self.cache[asset.id]
            else:
                doc_path = asset.get_document_from_asset()
                pdf_file = genai.upload_file(doc_path)
                self.cache[asset.id] = pdf_file
            
            prompt = f"{DOCUMENT_SYSTEM_TEMPLATE}\n\n{DOCUMENT_HUMAN_TEMPLATE.format(field_name=field_name, description=description)}"
            
            return {
                "parts": [prompt, pdf_file]  # Gemini accepts a list of parts including text and files
            }
        except Exception as e:
            self.logger.exception(f"Error constructing document prompt: {str(e)}")
            raise

class GeminiImageHandler(GeminiExtractionHandler):
    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> Dict:
        try:
            images = asset.get_images_from_asset()
            prompt = f"{DOCUMENT_SYSTEM_TEMPLATE}\n\n{DOCUMENT_HUMAN_TEMPLATE.format(field_name=field_name, description=description)}"
            
            # Convert base64 images to PIL Images
            image_parts = []
            for image_data in images:
                # Convert base64 to bytes
                image_bytes = BytesIO(image_data)
                # Open as PIL Image
                pil_image = PIL.Image.open(image_bytes)
                image_parts.append(pil_image)
            
            # Combine prompt and images as parts
            parts = [prompt] + image_parts
            
            return {
                "parts": parts  # Gemini accepts text prompt and PIL images
            }
        except Exception as e:
            self.logger.exception(f"Error constructing image prompt: {str(e)}")
            raise

class GeminiAgentService(BaseAgentService):
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("Gemini API key is not set in the environment variables.")
            raise ValueError("Gemini API key is not set in the environment variables.")
        
        genai.configure(api_key=api_key)
        self.text_model = GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'))  # Model name should come from environment, with a default
        self.vision_model = GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-1.5-flash'))  # Model name should come from environment, with a default

        # Initialize handlers
        self.handlers = {
            ASSET_FILE_TYPE.PDF: GeminiDocumentHandler(),
            ASSET_FILE_TYPE.JPEG: GeminiImageHandler(),
            ASSET_FILE_TYPE.JPG: GeminiImageHandler(),
            ASSET_FILE_TYPE.PNG: GeminiImageHandler(),
            # Add more handlers as needed
        }

    def process_task(self, task: Task) -> Dict[str, Any]:
        structured_output = {}
        try:
            extraction_actions = task.actions.filter(action_type=ACTION_TYPE.EXTRACTION)
            generation_actions = task.actions.filter(action_type=ACTION_TYPE.GENERATION)

            if extraction_actions.exists():
                structured_output["extractions"] = self.extract_fields(task, extraction_actions)

            if generation_actions.exists():
                structured_output["generations"] = self.generate_contents(task, generation_actions)

        except Exception as e:
            logger.error(f"Error processing task {task.id}: {e}")
            structured_output["error"] = str(e)

        return structured_output

    def extract_fields(self, task: Task, actions: List[Action]) -> Dict[str, Any]:
        results = {}
        try:
            for action in actions:
                field_name = action.output_column_name
                description = action.description
                action_results = []
                
                for asset in task.assets.all():
                    handler = self.handlers.get(asset.file_type)
                    if not handler:
                        logger.warning(f"No handler found for asset type: {asset.file_type}")
                        continue

                    prompt_data = handler.construct_prompt(field_name, description, asset)
                    
                    # Generate content with parts and enable streaming
                    response = self.vision_model.generate_content(
                        prompt_data.get("parts", []),
                        stream=True
                    )
                    
                    # Always handle as streaming response
                    response_text = ""
                    for chunk in response:
                        response_text += chunk.text
                    
                    parsed_response = self.parse_response(response_text)
                    
                    action_results.append({
                        "asset": asset.name,
                        "data": parsed_response,
                        "source": asset.url,
                    })
                
                results[field_name] = action_results
                
        except Exception as e:
            logger.error(f"Error extracting fields: {e}")
            results["error"] = str(e)

        return results

    def generate_contents(self, task: Task, actions: List[Action]) -> Dict[str, str]:
        content_results = {}
        try:
            for action in actions:
                prompt = action.description
                response = self.text_model.generate_content(prompt)
                content_results[action.output_column_name] = response.text
        except Exception as e:
            logger.error(f"Error generating contents: {e}")
            content_results["error"] = str(e)

        return content_results

    def parse_response(self, response: str) -> Dict[str, Any]:
        try:
            # Clean up the response text to ensure it's valid JSON
            cleaned_response = response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:-3]
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:-3]
                
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing response: {e}")
            return {"error": "Invalid JSON response"} 