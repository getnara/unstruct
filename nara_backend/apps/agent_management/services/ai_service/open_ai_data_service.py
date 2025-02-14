import json
import logging
from typing import Any, Dict, List, Union

from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException

from apps.core.models import Action, Asset, Task, ASSET_FILE_TYPE
from apps.core.models.action import ACTION_TYPE

from .base_agent_service import BaseAgentService
from .vector_store import VectorStore
import os

logger = logging.getLogger(__name__)

# Define the system and human message templates for documents
DOCUMENT_SYSTEM_TEMPLATE = "You are an assistant that extracts specific fields from documents."
DOCUMENT_HUMAN_TEMPLATE = """
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

# Define the system and human message templates for images
IMAGE_SYSTEM_TEMPLATE = "You are an assistant that extracts specific fields from images."
IMAGE_HUMAN_TEMPLATE = """
Extract the following information from the given images:

Field: {field_name}
Description: {description}

For each extracted field, also provide:
1. A confidence score between 0 and 1, where 1 is highest confidence.
2. A reference to where in the image the information was found (e.g., "Image 1").

Respond in the following JSON format only:
{{
    "{field_name}": "<extracted value>",
    "{field_name}_confidence": <confidence score>,
    "{field_name}_reference": "<reference>"
}}
"""

# Define the system and human message templates for videos
VIDEO_SYSTEM_TEMPLATE = "You are an assistant that extracts specific fields from videos, including visual frames and audio transcripts."
VIDEO_HUMAN_TEMPLATE = """
Extract the following information from the given video:

Field: {field_name}
Description: {description}

For each extracted field, also provide:
1. A confidence score between 0 and 1, where 1 is highest confidence.
2. A reference to where in the video the information was found (e.g., "Image 1").

Respond in the following JSON format:
{{
    "{field_name}": "<extracted value>",
    "{field_name}_confidence": <confidence score>,
    "{field_name}_reference": "<reference>"
}}
"""

class ExtractionHandler:
    """Base class for handling different asset types."""
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> Union[str, List[HumanMessage]]:
        raise NotImplementedError

    def sanitize_document_content(self, document: str) -> str:
        return document.replace("\n", " ").strip()

class DocumentExtractionHandler(ExtractionHandler):
    def __init__(self, chat_prompt: ChatPromptTemplate):
        super().__init__()  # Initialize base class logger
        self.chat_prompt = chat_prompt

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> str:
        try:
            doc_path = asset.get_document_from_asset()
            self.logger.info(f"Got document path: {doc_path}")
            
            vector_store = VectorStore(str(asset.id))
            vector_store.index_document(doc_path=doc_path)
            data = vector_store.invoke(f"{field_name} {description}")
            
            self.logger.info(f"Got vector store data with {len(data.get('texts', []))} text chunks")
            
            if not field_name or not description:
                raise ValueError("Field name or description is empty")

            px = self.chat_prompt.format_prompt(
                field_name=field_name,
                description=description,
            )

            text_content = []
            if data.get('texts'):
                text_content.append(
                    HumanMessage(content="\n".join(data['texts']))
                )

            return px.messages + text_content
        except Exception as e:
            self.logger.exception(f"Error constructing document prompt: {str(e)}")
            raise

class ImageExtractionHandler(ExtractionHandler):
    def __init__(self, chat_prompt: ChatPromptTemplate):
        super().__init__()
        self.chat_prompt = chat_prompt

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> List[HumanMessage]:
        try:
            images = asset.get_images_from_asset()
            self.logger.info(f"Got {len(images)} images from asset")
            
            if not field_name or not description or not images:
                raise ValueError("Field name, description, or image data is empty")

            px = self.chat_prompt.format_prompt(
                field_name=field_name,
                description=description,
            )
            
            human_messages = [
                HumanMessage(
                    content=[{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                    } for img in images]
                )
            ]
            return px.messages + human_messages
        except Exception as e:
            self.logger.exception(f"Error constructing image prompt: {str(e)}")
            raise

class VideoExtractionHandler(ExtractionHandler):
    def __init__(self, chat_prompt: ChatPromptTemplate):
        super().__init__()
        self.chat_prompt = chat_prompt

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> List[HumanMessage]:
        try:
            video_path = asset.get_video()
            self.logger.info(f"Got video path: {video_path}")
            
            vector_store = VectorStore(str(asset.id))
            vector_store.index_video(video_path=video_path)
            data = vector_store.invoke(f"{field_name} {description}")
            
            frames = data.get('images', [])
            self.logger.info(f"Got {len(frames)} frames from video")
            
            if not field_name or not description:
                raise ValueError("Field name or description is empty")

            px = self.chat_prompt.format_prompt(
                field_name=field_name,
                description=description,
            )
            
            human_messages = [
                HumanMessage(
                    content=[{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                    } for img in frames]
                )
            ]

            transcript_message = []
            if data.get('texts'):
                transcript_message.append(
                    HumanMessage(content="\n".join(data['texts']))
                )
            
            return px.messages + transcript_message + human_messages
        except Exception as e:
            self.logger.exception(f"Error constructing video prompt: {str(e)}")
            raise

class AudioExtractionHandler(ExtractionHandler):
    def __init__(self, chat_prompt: ChatPromptTemplate):
        self.chat_prompt = chat_prompt

    def construct_prompt(self, field_name: str, description: str, asset: Asset) -> List[HumanMessage]:
        audio_path = asset.get_audio()  # Assume this method retrieves the audio file path
        vector_store = VectorStore(str(asset.id))
        vector_store.index_audio(audio_path=audio_path)
        data = vector_store.invoke(f"{field_name} {description}")
        
        if not field_name or not description:
            raise ValueError("Field name, description, or audio data is empty.")
        try:
            px = self.chat_prompt.format_prompt(
                field_name=field_name,
                description=description,
            )
            
            # Add transcripts to the prompt
            transcript_message = []
            if data['texts']:
                transcript_message.append(
                    HumanMessage(
                        content="\n".join(data['texts'])
                    )
                )
            
            return px.messages + transcript_message
        except Exception as e:
            logger.error(f"Error constructing extraction prompt for audio: {e}")
            raise

class OpenAIAgentService(BaseAgentService):
    def __init__(self, api_key: str):
        if not api_key:
            logger.error("OpenAI API key is not set in the environment variables.")
            raise ValueError("OpenAI API key is not set in the environment variables.")
        self.llm = ChatOpenAI(openai_api_key=api_key, temperature=0, model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

        # Initialize prompt templates
        self.document_chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(DOCUMENT_SYSTEM_TEMPLATE),
            HumanMessagePromptTemplate.from_template(DOCUMENT_HUMAN_TEMPLATE)
        ])

        self.image_chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(IMAGE_SYSTEM_TEMPLATE),
            HumanMessagePromptTemplate.from_template(IMAGE_HUMAN_TEMPLATE)
        ])

        self.video_chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(VIDEO_SYSTEM_TEMPLATE),
            HumanMessagePromptTemplate.from_template(VIDEO_HUMAN_TEMPLATE)
        ])

        # Initialize handlers
        self.handlers = {
            ASSET_FILE_TYPE.PDF: DocumentExtractionHandler(self.video_chat_prompt),
            ASSET_FILE_TYPE.JPEG: ImageExtractionHandler(self.image_chat_prompt),
            ASSET_FILE_TYPE.JPG: ImageExtractionHandler(self.image_chat_prompt),
            ASSET_FILE_TYPE.PNG: ImageExtractionHandler(self.image_chat_prompt),
            ASSET_FILE_TYPE.MP4: VideoExtractionHandler(self.video_chat_prompt),
            ASSET_FILE_TYPE.MP3: AudioExtractionHandler(self.video_chat_prompt),  # Add MP3 handler

            # Add more handlers for different asset types as needed
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
                    asset_type = asset.file_type # Assume Asset has a 'type' attribute
                    
                    handler = self.handlers.get(asset_type)
                    print(asset_type, handler)
                    if not handler:
                        logger.warning(f"No handler found for asset type: {asset_type}")
                        continue

                    prompt = handler.construct_prompt(field_name, description, asset)
                    
                    if isinstance(prompt, str):
                        response = self.llm.invoke(prompt)  # Use invoke for string prompts
                    elif isinstance(prompt, list):
                        response = self.llm.invoke(prompt)  # Use invoke_messages for message lists
                    else:
                        logger.error(f"Unsupported prompt type for asset type: {asset_type}")
                        continue

                    # Clean response content if necessary
                    if isinstance(response.content, str):
                        response_content = response.content
                        if 'json' in response_content:
                            response_content = response_content.replace('json', '')
                        response_content = response_content.replace('```', '')
                    else:
                        response_content = str(response.content)

                    parsed_response = self.parse_response(response_content)
                    action_results.append(
                        {
                            "asset": asset.name,
                            "data": parsed_response,
                            "source": asset.url,
                        }
                    )
                results[field_name] = action_results
        except Exception as e:
            logger.error(f"Error extracting fields for task {task.id}: {e}")
            results["error"] = str(e)

        return results

    def generate_contents(self, task: Task, actions: List[Action]) -> Dict[str, str]:
        content_results = {}
        try:
            for action in actions:
                prompt = action.description
                response = self.llm.invoke(prompt)  # Assuming generate content doesn't depend on asset type
                logger.debug(f"Generation response: {response}")
                content_results[action.output_column_name] = response.content
        except Exception as e:
            logger.error(f"Error generating contents for task {task.id}: {e}")
            content_results["error"] = str(e)

        return content_results

    def parse_response(self, response: str) -> Dict[str, Any]:
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing response: {e}")
            return {"error": "Invalid JSON response"}

# Utility function (if still needed)
def sanitize_document_content(document: str) -> str:
    # Remove any unwanted characters or formatting
    return document.replace("\n", " ").strip()
