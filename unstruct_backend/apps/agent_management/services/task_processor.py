from typing import Dict
import json
import boto3
import csv
import io
from collections import defaultdict
from django.conf import settings
from django.utils import timezone
from botocore.config import Config

from apps.core.models import Task, ASSET_FILE_TYPE
from .agent_service_factory import AgentServiceFactory


class TaskProcessor:
    def __init__(self):
        self.model = settings.AI_MODEL  # e.g., "OpenAI"
        self.preview_limit = 5  # Number of results to show in preview
        self.s3_client = boto3.client(
            's3',
            region_name='us-east-2',
            config=Config(signature_version='s3v4')
        )

    def _convert_to_csv(self, results: Dict) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Collect all values by column
        columns = defaultdict(list)
        
        # Process extractions
        if 'extractions' in results:
            for action_name, items in results['extractions'].items():
                if isinstance(items, list):
                    for item in items:
                        value = item['data'].get(action_name, '')
                        columns[action_name].append(value)
        
        # Process generations if they exist
        if 'generations' in results:
            for action_name, items in results['generations'].items():
                if isinstance(items, list):
                    for item in items:
                        value = item['data'].get(action_name, '')
                        columns[action_name].append(value)
        
        # Write headers (column names)
        headers = list(columns.keys())
        if not headers:  # If no data, return empty CSV with a message
            writer.writerow(['message'])
            writer.writerow(['No results available'])
            return output.getvalue()
            
        writer.writerow(headers)
        
        # Find the maximum length of any column
        max_length = max((len(values) for values in columns.values()), default=0)
        
        # Write values row by row
        for i in range(max_length):
            row = [columns[header][i] if i < len(columns[header]) else '' for header in headers]
            writer.writerow(row)
        
        return output.getvalue()

    def process(self, task: Task) -> Dict[str, any]:
        # Get the file type of the first asset in the task
        file_type = task.assets.first().file_type if task.assets.exists() else None
        
        # Select appropriate API key based on file type
        api_key = settings.GEMINI_API_KEY if file_type == ASSET_FILE_TYPE.PDF else settings.OPENAI_API_KEY
        
        # Get appropriate agent service based on model and file type
        agent_service = AgentServiceFactory.get_agent_service(
            model=self.model, 
            api_key=api_key,
            file_type=file_type
        )
        
        if not agent_service:
            raise ValueError(f"AI model '{self.model}' is not supported.")

        # Get full results
        full_results = agent_service.process_task(task)

        # Create preview results
        preview_results = {}
        if 'extractions' in full_results:
            preview_results['extractions'] = {
                field: results[:self.preview_limit] if isinstance(results, list) else results
                for field, results in full_results['extractions'].items()
            }
        if 'generations' in full_results:
            preview_results['generations'] = {
                field: results[:self.preview_limit] if isinstance(results, list) else results
                for field, results in full_results['generations'].items()
            }

        # Store full results in both CSV and JSON formats
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        base_key = f"task_results/{task.id}/results_{timestamp}"
        
        # Store JSON version
        json_key = f"{base_key}.json"
        self.s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=json_key,
            Body=json.dumps(full_results),
            ContentType='application/json'
        )
        
        # Convert and store CSV version
        csv_key = f"{base_key}.csv"
        csv_content = self._convert_to_csv(full_results)
        self.s3_client.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=csv_key,
            Body=csv_content,
            ContentType='text/csv'
        )

        # Generate a pre-signed URL for the CSV file
        presigned_url = self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': csv_key
            },
            ExpiresIn=604800  # URL expires in 7 days (7 * 24 * 60 * 60 seconds)
        )

        # Update task with results URL and properly serialized preview results
        task.result_file_url = presigned_url
        task.process_results = json.dumps(preview_results)  # Properly serialize as JSON
        task.save()

        return {
            'preview': preview_results,
            'results_url': presigned_url
        }
