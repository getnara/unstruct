from django.core.files.storage import default_storage
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import os
import logging
import traceback
from django.conf import settings

from apps.common.views import NBaselViewSet
from apps.core.models import Asset, Project
from apps.core.models.asset import ASSET_UPLOAD_SOURCE
from apps.core.serializers import AssetSerializer
from apps.core.models.asset import ASSET_FILE_TYPE
from apps.agent_management.services.ai_service.vector_store import VectorStore
from apps.common.utils.gdrive_utils import GoogleDriveService
from apps.common.utils.s3_utils import S3Service
from apps.common.utils.dropbox_utils import DropboxService
from apps.common.mixins.organization_mixin import OrganizationMixin


class AssetViewSet(OrganizationMixin, NBaselViewSet):
    name = "asset"
    serializer_class = AssetSerializer
    queryset = Asset.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.get_organization())

    @action(detail=False, methods=["post"])
    def create_assets_for_project(self, request):
        files = request.FILES.getlist("files")
        project_id = request.data.get("project_id")

        if not files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        assets = []
        for file in files:
            asset = Asset(
                name=file.name,
                description=f"Uploaded file: {file.name}",
                project=project,
                upload_source=ASSET_UPLOAD_SOURCE.UPLOAD,
                file_type=self.get_file_type(file.name),
            )
            asset.save()

            # Save the file using Django's default file storage
            file_path = default_storage.save(f"assets/{asset.id}/{file.name}", file)
            asset.url = default_storage.url(file_path)
            asset.save()

        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def assets(self, request):
        """Create assets from various sources"""
        upload_source = request.data.get("upload_source")
        if not upload_source:
            return Response(
                {"error": "upload_source is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle regular file uploads
        if upload_source == ASSET_UPLOAD_SOURCE.UPLOAD:
            return self.create_assets_for_project(request)
        
        # Handle Google Drive uploads
        if upload_source == ASSET_UPLOAD_SOURCE.GDRIVE:
            return self.create_assets_from_gdrive(request)
            
        # Handle S3 uploads
        if upload_source == ASSET_UPLOAD_SOURCE.AWS_S3:
            return self.create_assets_from_s3(request)
            
        # Handle Dropbox uploads
        if upload_source == ASSET_UPLOAD_SOURCE.DROPBOX:
            return self.create_assets_from_dropbox(request)
            
        return Response(
            {"error": f"Unsupported upload source: {upload_source}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    def create_assets_from_gdrive(self, request):
        """Create assets from Google Drive files or folders"""
        project_id = request.data.get("project_id")
        file_ids = request.data.get("file_ids", [])  # List of file IDs
        folder_id = request.data.get("folder_id")    # Optional folder ID
        recursive = request.data.get("recursive", True)  # For folder processing
        service_account_info = request.data.get("service_account_info")

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not file_ids and not folder_id:
            return Response(
                {"error": "Either file_ids or folder_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not service_account_info:
            return Response(
                {"error": "Service account credentials are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Initialize Google Drive service with service account
            gdrive_service = GoogleDriveService(service_account_info=service_account_info)
            gdrive_service.authenticate()

            assets = []

            # Process individual files if provided
            if file_ids:
                for file_info in gdrive_service.get_files_by_ids(file_ids):
                    asset = self._create_asset_from_gdrive_file(
                        project=project,
                        gdrive_file_id=file_info['id'],
                        file_info=file_info,
                        service_account_info=service_account_info
                    )
                    assets.append(asset)

            # Process folder if provided
            if folder_id:
                for file_info in gdrive_service.list_folder_contents(folder_id, recursive=recursive):
                    asset = self._create_asset_from_gdrive_file(
                        project=project,
                        gdrive_file_id=file_info['id'],
                        file_info=file_info,
                        service_account_info=service_account_info
                    )
                    assets.append(asset)

            serializer = self.get_serializer(assets, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_asset_from_gdrive_file(self, project, gdrive_file_id, file_info, service_account_info):
        """Helper method to create an asset from a Google Drive file"""
        asset = Asset(
            name=file_info['name'],
            description=f"Google Drive file: {file_info['name']}",
            project=project,
            upload_source=ASSET_UPLOAD_SOURCE.GDRIVE,
            file_type=self.get_file_type(file_info['name']),
            gdrive_file_id=gdrive_file_id,
            gdrive_credentials=service_account_info,
        )
        asset.save()

        return asset

    def create_assets_from_s3(self, request):
        """Create assets from S3 bucket"""
        project_id = request.data.get("project_id")
        bucket = request.data.get("bucket")
        keys = request.data.get("keys", [])  # List of S3 keys
        prefix = request.data.get("prefix")  # Optional prefix/folder path
        recursive = request.data.get("recursive", True)
        aws_credentials = request.data.get("aws_credentials")

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not bucket:
            return Response({"error": "S3 bucket is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not keys and not prefix:
            return Response(
                {"error": "Either keys or prefix is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Initialize S3 service
            s3_service = S3Service(aws_credentials)
            s3_service.authenticate()

            assets = []

            # Process individual files if provided
            if keys:
                for key in keys:
                    file_info = s3_service.get_file_by_key(bucket, key)
                    asset = self._create_asset_from_s3_file(
                        project=project,
                        bucket=bucket,
                        key=key,
                        file_info=file_info,
                        aws_credentials=aws_credentials
                    )
                    assets.append(asset)

            # Process prefix/folder if provided
            if prefix:
                for file_info in s3_service.get_files_from_bucket(bucket, prefix, recursive):
                    asset = self._create_asset_from_s3_file(
                        project=project,
                        bucket=bucket,
                        key=file_info['id'],
                        file_info=file_info,
                        aws_credentials=aws_credentials
                    )
                    assets.append(asset)

            serializer = self.get_serializer(assets, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_asset_from_s3_file(self, project, bucket, key, file_info, aws_credentials):
        """Helper method to create an asset from an S3 file"""
        asset = Asset(
            name=file_info['name'],
            description=f"S3 file: {file_info['name']}",
            project=project,
            upload_source=ASSET_UPLOAD_SOURCE.AWS_S3,
            file_type=self.get_file_type(file_info['name']),
            s3_bucket=bucket,
            s3_key=key,
            s3_credentials=aws_credentials
        )
        asset.save()
        return asset

    def create_assets_from_dropbox(self, request):
        """Create assets from Dropbox files or folders"""
        project_id = request.data.get("project_id")
        paths = request.data.get("paths", [])  # List of file paths
        folder_path = request.data.get("folder_path")  # Optional folder path
        recursive = request.data.get("recursive", True)
        access_token = request.data.get("access_token")

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not paths and not folder_path:
            return Response(
                {"error": "Either paths or folder_path is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not access_token:
            return Response(
                {"error": "Dropbox access token is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Initialize Dropbox service
            dropbox_service = DropboxService(access_token)
            print(access_token)
            dropbox_service.authenticate()

            assets = []

            # Process individual files if provided
            if paths:
                for path in paths:
                    file_info = dropbox_service.get_file_by_id(path)
                    asset = self._create_asset_from_dropbox_file(
                        project=project,
                        file_path=path,
                        file_info=file_info,
                        access_token=access_token
                    )
                    assets.append(asset)

            # Process folder if provided
            if folder_path:
                for file_info in dropbox_service.list_folder_contents(folder_path, recursive):
                    asset = self._create_asset_from_dropbox_file(
                        project=project,
                        file_path=file_info['id'],
                        file_info=file_info,
                        access_token=access_token
                    )
                    assets.append(asset)

            serializer = self.get_serializer(assets, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_asset_from_dropbox_file(self, project, file_path, file_info, access_token):
        """Helper method to create an asset from a Dropbox file"""
        asset = Asset(
            name=file_info['name'],
            description=f"Dropbox file: {file_info['name']}",
            project=project,
            upload_source=ASSET_UPLOAD_SOURCE.DROPBOX,
            file_type=self.get_file_type(file_info['name']),
            dropbox_path=file_path,
            dropbox_access_token=access_token
        )
        asset.save()
        return asset

    def get_file_type(self, filename):
        extension = filename.split(".")[-1].lower()
        if extension == "pdf":
            return ASSET_FILE_TYPE.PDF
        elif extension in ["doc", "docx"]:
            return ASSET_FILE_TYPE.DOC
        elif extension == "txt":
            return ASSET_FILE_TYPE.TXT
        elif extension == 'mp4':
            return ASSET_FILE_TYPE.MP4
        elif extension == 'jpeg':
            return ASSET_FILE_TYPE.JPEG
        elif extension == 'jpg':
            return ASSET_FILE_TYPE.JPG
        elif extension == 'png':
            return ASSET_FILE_TYPE.PNG
        elif extension == 'mp3':
            return ASSET_FILE_TYPE.MP3
        else:
            return ASSET_FILE_TYPE.OTHER

    def handle_file_upload(self, request):
        file_key = request.data.get('file_key')
        project_id = request.data.get('project')

        if not file_key:
            return Response({"error": "file_key is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not project_id:
            return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create asset with S3 URL using bucket from settings
        asset = Asset(
            name=file_key.split('/')[-1],  # Get filename from key
            description=f"Uploaded file: {file_key}",
            project=project,
            upload_source=ASSET_UPLOAD_SOURCE.UPLOAD,
            file_type=self.get_file_type(file_key),
            url=f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{file_key}"
        )
        asset.save()

        serializer = self.get_serializer(asset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_file_type_from_mime(self, mime_type: str, filename: str) -> str:
        """Determine file type from MIME type and filename"""
        mime_to_type = {
            'application/pdf': ASSET_FILE_TYPE.PDF,
            'video/mp4': ASSET_FILE_TYPE.MP4,
            'application/msword': ASSET_FILE_TYPE.DOC,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ASSET_FILE_TYPE.DOC,
            'text/plain': ASSET_FILE_TYPE.TXT,
            'image/jpeg': ASSET_FILE_TYPE.JPEG,
            'image/jpg': ASSET_FILE_TYPE.JPG,
            'image/png': ASSET_FILE_TYPE.PNG,
            'audio/mpeg': ASSET_FILE_TYPE.MP3,
        }
        
        # First try MIME type
        if mime_type in mime_to_type:
            return mime_to_type[mime_type]
        
        # Then try file extension
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        ext_to_type = {
            'pdf': ASSET_FILE_TYPE.PDF,
            'mp4': ASSET_FILE_TYPE.MP4,
            'doc': ASSET_FILE_TYPE.DOC,
            'docx': ASSET_FILE_TYPE.DOC,
            'txt': ASSET_FILE_TYPE.TXT,
            'jpeg': ASSET_FILE_TYPE.JPEG,
            'jpg': ASSET_FILE_TYPE.JPG,
            'png': ASSET_FILE_TYPE.PNG,
            'mp3': ASSET_FILE_TYPE.MP3,
        }
        
        return ext_to_type.get(ext, ASSET_FILE_TYPE.OTHER)

    def handle_google_drive_file(self, request):
        """Handle Google Drive file imports"""
        try:
            data = request.data
            project_id = data.get('project')
            file_id = data.get('file_id')
            name = data.get('name')
            mime_type = data.get('mime_type')
            
            if not project_id:
                return Response({"error": "Project ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not file_id:
                return Response({"error": "File ID is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Add file type detection
            file_type = self.get_file_type_from_mime(mime_type, name)
            
            # Create the asset
            asset = Asset(
                name=name,
                project_id=project_id,
                upload_source=ASSET_UPLOAD_SOURCE.GOOGLE_DRIVE,
                source_file_id=file_id,
                metadata=data.get('metadata'),
                mime_type=mime_type,
                size=data.get('size'),
                file_type=file_type  # Set the detected file type
            )
            asset.save()
            
            serializer = self.get_serializer(asset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Error creating Google Drive asset")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def handle_dropbox_file(self, request):
        """Handle Dropbox file imports (placeholder)"""
        return Response(
            {"error": "Dropbox file handling not implemented yet"}, 
            status=status.HTTP_501_NOT_IMPLEMENTED
        )

    def handle_s3_file(self, request):
        """Handle S3 file imports (placeholder)"""
        return Response(
            {"error": "S3 file handling not implemented yet"}, 
            status=status.HTTP_501_NOT_IMPLEMENTED
        )

    def create(self, request):
        upload_source = request.data.get('upload_source')
        handler_map = {
            ASSET_UPLOAD_SOURCE.UPLOAD: self.handle_file_upload,
            ASSET_UPLOAD_SOURCE.GOOGLE_DRIVE: self.handle_google_drive_file,
            ASSET_UPLOAD_SOURCE.DROPBOX: self.handle_dropbox_file,  # Now we can include these
            ASSET_UPLOAD_SOURCE.AWS_S3: self.handle_s3_file,       # since the methods exist
        }
        
        handler = handler_map.get(upload_source)
        if not handler:
            return Response(
                {"error": f"Unsupported upload source: {upload_source}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return handler(request)

    @action(detail=True, methods=["get"])
    def debug(self, request, pk=None):
        """Debug endpoint to check asset state"""
        try:
            asset = self.get_object()
            debug_info = {
                "id": str(asset.id),
                "name": asset.name,
                "file_type": asset.file_type,
                "upload_source": asset.upload_source,
                "gdrive_file_id": asset.gdrive_file_id,
                "has_metadata": bool(asset.metadata),
                "metadata": asset.metadata,  # Add full metadata
                "has_credentials": bool(asset.gdrive_credentials),
                "url": asset.url,
                "mime_type": asset.mime_type,
                "size": asset.size,
            }
            
            # Try to get the file path
            try:
                logger.info(f"Debug: Getting file path for asset {asset.id}")
                file_path = asset.get_file_path()
                debug_info["file_path"] = file_path
                debug_info["file_exists"] = os.path.exists(file_path)
                if debug_info["file_exists"]:
                    debug_info["file_size"] = os.path.getsize(file_path)
                    debug_info["file_permissions"] = oct(os.stat(file_path).st_mode)[-3:]
                    
                    # For PDFs, try to verify
                    if asset.file_type == 'PDF':
                        try:
                            from PyPDF2 import PdfReader
                            reader = PdfReader(file_path)
                            debug_info["pdf_pages"] = len(reader.pages)
                        except Exception as e:
                            debug_info["pdf_error"] = str(e)
            
            except Exception as e:
                logger.exception("Error in debug endpoint while getting file path")
                debug_info["file_path_error"] = str(e)
                debug_info["file_path_error_type"] = type(e).__name__
            
            return Response(debug_info)
        except Exception as e:
            logger.exception("Error in debug endpoint")
            return Response({
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }, status=500)

    def destroy(self, request, *args, **kwargs):
        """Soft delete the asset"""
        try:
            instance = self.get_object()
            # Clean up any temporary files
            try:
                if instance.upload_source == ASSET_UPLOAD_SOURCE.GOOGLE_DRIVE:
                    download_dir = f"/tmp/nara/gdrive/{instance.id}"
                    if os.path.exists(download_dir):
                        import shutil
                        shutil.rmtree(download_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up downloaded files: {e}")
            
            # Perform soft delete (default behavior)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception("Error during asset deletion")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
