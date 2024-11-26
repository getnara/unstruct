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


class TaskViewSet(NBaselViewSet):
    name = "task"
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()
    
    @action(detail=False, methods=["post"], url_path="process")
    def process_task(self, request):
        try:
            task_id = request.data.get("task_id")
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        processor = TaskProcessor()
        try:
            task.status = "RUNNING"
            task.save()
            
            structured_output = processor.process(task)
            
            # Store the process results
            task.process_results = structured_output
            task.status = "FINISHED"
            task.save()
            
            return Response(structured_output, status=status.HTTP_200_OK)
        except Exception as e:
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
