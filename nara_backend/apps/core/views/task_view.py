from django.db import models
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import os

from apps.common.views import NBaselViewSet
from apps.core.models import Task
from apps.core.serializers import TaskSerializer
from apps.agent_management.services.task_processor import TaskProcessor
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
import pandas as pd
from django.http import HttpResponse
from datetime import datetime
import json
from apps.common.utils.snowflake_utils import SnowflakeManager
from apps.common.mixins.organization_mixin import OrganizationMixin
from django.core.exceptions import ValidationError
from apps.core.models.asset import ASSET_FILE_TYPE

logger = logging.getLogger(__name__)

class TaskViewSet(OrganizationMixin, NBaselViewSet):
    name = "task"
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.get_organization())

    @action(detail=True, methods=["post"], url_path="process")
    def process_task(self, request, pk=None):
        try:
            task = self.get_object()
            organization = task.organization
            
            # Log organization and subscription details
            logger.info(f"Processing task for organization: {organization.id}")
            logger.info(f"Organization subscription plan: {organization.current_subscription_plan}")
            logger.info(f"Organization owner email: {organization.owner.email}")
            
            # Get all assets for this task
            assets = task.assets.all()
            if not assets:
                return Response(
                    {"error": "No assets found for this task"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log asset details
            for asset in assets:
                logger.info(f"Processing asset: {asset.id}, type: {asset.file_type}")
            
            # Process each asset with appropriate limits
            for asset in assets:
                # Get file size in GB for media files
                file_path = asset.get_file_path()
                size_in_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
                
                # Check file type and apply appropriate limits
                if asset.file_type == ASSET_FILE_TYPE.PDF:
                    # Check PDF processing limit
                    logger.info(f"Checking PDF processing limit for org {organization.id}")
                    organization.can_process_pdf()
                    organization.increment_pdf_count()
                    logger.info("PDF processing limit check passed")
                    
                elif asset.file_type == ASSET_FILE_TYPE.MP4:
                    # Check video processing limit
                    logger.info(f"Checking video processing limit for org {organization.id}, size: {size_in_gb}GB")
                    organization.can_process_video(size_in_gb)
                    organization.add_video_usage(size_in_gb)
                    logger.info("Video processing limit check passed")
                    
                elif asset.file_type == ASSET_FILE_TYPE.MP3:
                    # Check audio processing limit
                    logger.info(f"Checking audio processing limit for org {organization.id}, size: {size_in_gb}GB")
                    organization.can_process_audio(size_in_gb)
                    organization.add_audio_usage(size_in_gb)
                    logger.info("Audio processing limit check passed")
            
            # Process the task
            task.status = "RUNNING"
            task.save()
            
            processor = TaskProcessor()
            structured_output = processor.process(task)
            
            # Store the process results
            task.process_results = structured_output
            task.status = "FINISHED"
            task.save()
            
            return Response(structured_output, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            if task:
                task.status = "FAILED"
                task.save()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            if task:
                task.status = "FAILED"
                task.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"], url_path="exporttoexcel")
    def export_to_excel(self, request, pk=None):
        try:
            task = self.get_object()
            
            if not task.process_results:
                return Response(
                    {"error": "No results available for this task."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Parse the JSON string if it's a string
            results_data = (
                json.loads(task.process_results)
                if isinstance(task.process_results, str)
                else task.process_results
            )
            
            # Ensure results_data is a list
            if not isinstance(results_data, list):
                results_data = [results_data]
            
            # Flatten the JSON data
            flattened_data = []
            for result in results_data:
                if 'extractions' in result:
                    for extraction_type, extractions in result['extractions'].items():
                        if isinstance(extractions, list):
                            for item in extractions:
                                row = {
                                    'TASK_ID': str(task.id),
                                    'EXTRACTION_TYPE': extraction_type,
                                    'ASSET': item.get('asset', ''),
                                    'SOURCE': item.get('source', '')
                                }
                                # Add all fields from the nested 'data' dictionary
                                if 'data' in item:
                                    # Convert data keys to uppercase
                                    data_dict = {k.upper(): v for k, v in item['data'].items()}
                                    row.update(data_dict)
                                flattened_data.append(row)
            
            # Convert flattened data to DataFrame
            df = pd.DataFrame(flattened_data)
            
            # Create Excel response
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"task_results_{task.id}_{timestamp}.xlsx"
            
            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            
            # Write DataFrame to Excel
            df.to_excel(response, index=False, engine="openpyxl")
            
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Failed to export results: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"], url_path="exporttosnowflake")
    def export_to_snowflake(self, request, pk=None):
        try:
            task = self.get_object()
            
            # Validate Snowflake credentials in request
            required_fields = ['account', 'user', 'password', 'warehouse', 'database', 'schema', 'role']
            snowflake_config = {}
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {"error": f"Missing required Snowflake credential: {field}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                snowflake_config[field] = request.data[field]
            
            if not task.process_results:
                return Response(
                    {"error": "No results available for this task."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Parse the JSON string if it's a string
            results_data = (
                json.loads(task.process_results)
                if isinstance(task.process_results, str)
                else task.process_results
            )
            
            # Ensure results_data is a list
            if not isinstance(results_data, list):
                results_data = [results_data]
            
            # Flatten the JSON data
            flattened_data = []
            for result in results_data:
                if 'extractions' in result:
                    for extraction_type, extractions in result['extractions'].items():
                        if isinstance(extractions, list):
                            for item in extractions:
                                row = {
                                    'TASK_ID': str(task.id),
                                    'EXTRACTION_TYPE': extraction_type,
                                    'ASSET': item.get('asset', ''),
                                    'SOURCE': item.get('source', '')
                                }
                                # Add all fields from the nested 'data' dictionary
                                if 'data' in item:
                                    # Convert data keys to uppercase
                                    data_dict = {k.upper(): v for k, v in item['data'].items()}
                                    row.update(data_dict)
                                flattened_data.append(row)
            
            # Convert flattened data to DataFrame
            df = pd.DataFrame(flattened_data)
            
            # Upload to Snowflake
            snowflake = SnowflakeManager(snowflake_config)
            table_name = request.data.get('table_name', 'TASK_RESULTS')
            result = snowflake.upload_dataframe(df, table_name)
            
            return Response(
                {
                    "message": "Data successfully uploaded to Snowflake",
                    "table_name": table_name,
                    **result
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": f"Failed to export to Snowflake: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
