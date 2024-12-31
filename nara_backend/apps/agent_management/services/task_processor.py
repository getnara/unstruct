from typing import Dict
import json
import boto3
import csv
import io
from collections import defaultdict
from django.conf import settings
from django.utils import timezone
from botocore.config import Config

from apps.core.models import Task
from .agent_service_factory import AgentServiceFactory


class TaskProcessor:
    def __init__(self):
        self.model = settings.AI_MODEL  # e.g., "OpenAI"
        self.api_key = settings.OPENAI_API_KEY
        self.preview_limit = 5  # Number of results to show in preview
        self.s3_client = boto3.client(
            's3',
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
        writer.writerow(headers)
        
        # Find the maximum length of any column
        max_length = max(len(values) for values in columns.values())
        
        # Write values row by row
        for i in range(max_length):
            row = [columns[header][i] if i < len(columns[header]) else '' for header in headers]
            writer.writerow(row)
        
        return output.getvalue()

    def process(self, task: Task) -> Dict[str, any]:
        agent_service = AgentServiceFactory.get_agent_service(self.model, self.api_key)
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
            ExpiresIn=3600  # URL expires in 1 hour
        )

        # Update task with results URL
        task.result_file_url = presigned_url
        task.process_results = preview_results
        task.save()

        return {
            'preview': preview_results,
            'results_url': presigned_url
        }
