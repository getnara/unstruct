from django.db import models
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import os
import time

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
from apps.common.middleware.timing_middleware import ViewTimingContextManager

logger = logging.getLogger(__name__)

class TaskViewSet(OrganizationMixin, NBaselViewSet):
    name = "task"
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.get_organization())

    def list(self, request, *args, **kwargs):
        timings = []
        
        with ViewTimingContextManager("query_tasks") as timing:
            queryset = self.get_queryset()
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"query_tasks;dur={timing.duration:.2f};desc='Query Tasks'")
            else:
                timings.append("query_tasks;dur=0;desc='Query Tasks'")
        
        with ViewTimingContextManager("serialize_tasks") as timing:
            serializer = self.get_serializer(queryset, many=True)
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"serialize_tasks;dur={timing.duration:.2f};desc='Serialize Tasks'")
            else:
                timings.append("serialize_tasks;dur=0;desc='Serialize Tasks'")
        
        response = Response(serializer.data)
        response["Server-Timing"] = ", ".join(timings)
        return response

    def retrieve(self, request, *args, **kwargs):
        timings = []
        
        with ViewTimingContextManager("query_task") as timing:
            instance = self.get_object()
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"query_task;dur={timing.duration:.2f};desc='Query Task'")
            else:
                timings.append("query_task;dur=0;desc='Query Task'")
        
        with ViewTimingContextManager("serialize_task") as timing:
            serializer = self.get_serializer(instance)
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"serialize_task;dur={timing.duration:.2f};desc='Serialize Task'")
            else:
                timings.append("serialize_task;dur=0;desc='Serialize Task'")
        
        response = Response(serializer.data)
        response["Server-Timing"] = ", ".join(timings)
        return response

    @action(detail=True, methods=["post"], url_path="process")
    def process_task(self, request, pk=None):
        try:
            timings = []
            
            with ViewTimingContextManager("get_task") as timing:
                task = self.get_object()
                organization = task.organization
                if hasattr(timing, 'duration') and timing.duration is not None:
                    timings.append(f"get_task;dur={timing.duration:.2f};desc='Get Task'")
                else:
                    timings.append("get_task;dur=0;desc='Get Task'")
            
            with ViewTimingContextManager("get_assets") as timing:
                assets = task.assets.all()
                if not assets:
                    return Response(
                        {"error": "No assets found for this task"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if hasattr(timing, 'duration') and timing.duration is not None:
                    timings.append(f"get_assets;dur={timing.duration:.2f};desc='Get Assets'")
                else:
                    timings.append("get_assets;dur=0;desc='Get Assets'")
            
            with ViewTimingContextManager("process_assets") as timing:
                for asset in assets:
                    file_path = asset.get_file_path()
                    size_in_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
                    
                    if asset.file_type == ASSET_FILE_TYPE.PDF:
                        organization.can_process_pdf()
                        organization.increment_pdf_count()
                    elif asset.file_type == ASSET_FILE_TYPE.MP4:
                        organization.can_process_video(size_in_gb)
                        organization.add_video_usage(size_in_gb)
                    elif asset.file_type == ASSET_FILE_TYPE.MP3:
                        organization.can_process_audio(size_in_gb)
                        organization.add_audio_usage(size_in_gb)
                if hasattr(timing, 'duration') and timing.duration is not None:
                    timings.append(f"process_assets;dur={timing.duration:.2f};desc='Process Assets'")
                else:
                    timings.append("process_assets;dur=0;desc='Process Assets'")
            
            with ViewTimingContextManager("task_processing") as timing:
                task.status = "RUNNING"
                task.save()
                
                processor = TaskProcessor()
                structured_output = processor.process(task)
                
                task.process_results = structured_output
                task.status = "FINISHED"
                task.save()
                if hasattr(timing, 'duration') and timing.duration is not None:
                    timings.append(f"task_processing;dur={timing.duration:.2f};desc='Task Processing'")
                else:
                    timings.append("task_processing;dur=0;desc='Task Processing'")
            
            response = Response(structured_output, status=status.HTTP_200_OK)
            response["Server-Timing"] = ", ".join(timings)
            return response
            
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