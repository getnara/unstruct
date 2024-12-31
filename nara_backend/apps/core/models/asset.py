from django.db import models
from django.utils.translation import gettext_lazy as _
import nest_asyncio
import os
import concurrent.futures
from typing import List, Generator

from apps.common.utils.s3_utils import download_from_s3, S3Service
from apps.common.utils.gdrive_utils import GoogleDriveService
from apps.common.utils.dropbox_utils import DropboxService

from apps.common.models import NBaseWithOwnerModel

from .project import Project
from .constants import ASSET_UPLOAD_SOURCE

import cv2
import base64
import time

import os
import requests
from django.utils import timezone

from django.conf import settings

import logging

import boto3

# Configure logger
logger = logging.getLogger(__name__)

nest_asyncio.apply()

class ASSET_FILE_TYPE(models.TextChoices):
    PDF = "PDF", _("Pdf")
    MP4 = "MP4", _("Mp4")
    DOC = "DOC", _("Doc")
    TXT = "TXT", _("Text")
    JPEG = "JPEG", _("Jpeg")
    JPG = "JPG", _("Jpg")
    PNG = "PNG", _("Png")
    MP3 = "MP3", _("Mp3")
    OTHER = "OTHER", _("Other")


class ASSET_UPLOAD_SOURCE(models.TextChoices):
    UPLOAD = 'UPLOAD', 'Upload'
    GOOGLE_DRIVE = 'GOOGLE_DRIVE', 'Google Drive'
    DROPBOX = 'DROPBOX', 'Dropbox'
    AWS_S3 = 'AWS_S3', 'AWS S3'


class Asset(NBaseWithOwnerModel):
    """Represents a asset in the system."""

    name = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    url = models.URLField(max_length=500)
    upload_source = models.CharField(
        max_length=20,
        choices=ASSET_UPLOAD_SOURCE.choices,
        default=ASSET_UPLOAD_SOURCE.UPLOAD,
    )
    file_type = models.CharField(
        max_length=20,
        choices=ASSET_FILE_TYPE.choices,
        default=ASSET_FILE_TYPE.OTHER,
    )
    mime_type = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=20, null=True, blank=True)
    
    # Generic fields for all sources
    source_file_id = models.CharField(max_length=500, null=True, blank=True)  # ID in the source system (gdrive_id, dropbox_id etc)
    source_credentials = models.JSONField(null=True, blank=True)  # Source-specific credentials
    metadata = models.JSONField(null=True, blank=True)  # Additional metadata like OAuth tokens

    class Meta:
        # Add this to ensure we only get non-deleted assets by default
        default_manager_name = 'objects'
        base_manager_name = 'objects'

    def __str__(self) -> str:
        return str(self.name)
    
    def _find_file_in_s3(self, filename):
        """Search for a file in S3 bucket and return its key"""
        try:
            s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION)
            logger.error(f"[DEBUG] Searching for file {filename} in bucket {settings.AWS_STORAGE_BUCKET_NAME}")
            
            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=settings.AWS_STORAGE_BUCKET_NAME):
                if 'Contents' in page:
                    for obj in page['Contents']:
                        logger.error(f"[DEBUG] Found object: {obj['Key']}")
                        if filename in obj['Key']:
                            return obj['Key']
            return None
        except Exception as e:
            logger.error(f"[DEBUG] Error searching S3: {str(e)}")
            raise

    def get_file_path(self):
        """Get the local path or download the file if it's from an external source"""
        local_path = f"/tmp/nara/assets/{self.id}/{self.name}"
        
        if self.upload_source == ASSET_UPLOAD_SOURCE.GOOGLE_DRIVE:
            return self._download_from_gdrive()
        elif self.upload_source == ASSET_UPLOAD_SOURCE.AWS_S3:
            return self._download_from_s3()
        elif self.upload_source == ASSET_UPLOAD_SOURCE.DROPBOX:
            return self._download_from_dropbox()
        else:
            if not os.path.exists(local_path):
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                try:
                    # First try to get the key directly from the URL
                    url_parts = self.url.split(settings.AWS_STORAGE_BUCKET_NAME + '.s3.' + settings.AWS_S3_REGION + '.amazonaws.com/')
                    key = None
                    
                    if len(url_parts) == 2:
                        key = url_parts[1]
                        logger.info(f"Found key from URL: {key}")
                    else:
                        # If URL parsing fails, search for the file in S3
                        filename = os.path.basename(self.url)
                        logger.info(f"Looking for file: {filename}")
                        key = self._find_file_in_s3(filename)
                        if not key:
                            raise Exception(f"File {filename} not found in S3 bucket")
                        logger.info(f"Found file with key: {key}")
                    
                    # Use S3 client directly
                    s3 = boto3.client(
                        's3',
                        region_name=settings.AWS_S3_REGION,
                    )
                    
                    try:
                        s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, key, local_path)
                        logger.info(f"File downloaded successfully to {local_path}")
                    except s3.exceptions.NoSuchKey:
                        # If the direct key fails, try with the URL-decoded version
                        from urllib.parse import unquote
                        decoded_key = unquote(key)
                        s3.download_file(settings.AWS_STORAGE_BUCKET_NAME, decoded_key, local_path)
                        logger.info(f"File downloaded successfully using decoded key: {decoded_key}")
                    
                except Exception as e:
                    logger.error(f"Error downloading file from S3: {str(e)}")
                    logger.error(f"Error type: {type(e)}")
                    raise
                    
            return local_path

    def _download_from_gdrive(self):
        """Download file from Google Drive using stored credentials or OAuth tokens"""
        if not self.source_file_id:
            raise ValueError("Google Drive file ID is required")

        # Get OAuth tokens from metadata if available
        oauth_tokens = self.metadata.get('oauth') if self.metadata else None
        
        try:
            logger.info(f"Starting Google Drive download for file {self.name}")
            logger.info(f"File ID: {self.source_file_id}")
            logger.info(f"OAuth tokens present: {bool(oauth_tokens)}")
            logger.info(f"Using service credentials from settings: {bool(settings.GOOGLE_DRIVE_CREDENTIALS)}")
            
            gdrive_service = GoogleDriveService(
                credentials_info=settings.GOOGLE_DRIVE_CREDENTIALS,
                oauth_tokens=oauth_tokens
            )

            logger.info("Authenticating with Google Drive...")
            gdrive_service.authenticate()
            logger.info("Authentication successful")
            
            # Create a temporary directory for downloads
            download_dir = f"/tmp/nara/gdrive/{self.id}"
            os.makedirs(download_dir, exist_ok=True)
            logger.info(f"Created download directory: {download_dir}")
            
            local_path = os.path.join(download_dir, self.name)
            logger.info(f"Will download to: {local_path}")
            
            file_info = gdrive_service.get_file_by_id(
                self.source_file_id, 
                local_path
            )
            
            if os.path.exists(local_path):
                file_size = os.path.getsize(local_path)
                logger.info(f"File downloaded successfully. Size: {file_size} bytes")
            else:
                raise Exception(f"File not found at {local_path} after download")
            
            return file_info['local_path']
        except Exception as e:
            logger.exception(f"Error downloading from Google Drive: {str(e)}")
            raise

    def _download_from_s3(self):
        """Download file from S3 using stored credentials"""
        if not self.source_file_id:
            raise ValueError("S3 bucket and key are required")

        try:
            s3_service = S3Service(self.source_credentials)  # Credentials are optional
            s3_service.authenticate()
            
            # Create a temporary directory for downloads
            download_dir = f"/tmp/nara/s3/{self.id}"
            os.makedirs(download_dir, exist_ok=True)
            
            file_info = s3_service.get_file_by_key(
                self.source_file_id,
                os.path.join(download_dir, self.name)
            )
            return file_info['local_path']
        except Exception as e:
            raise Exception(f"Error downloading from S3: {str(e)}")

    def _download_from_dropbox(self):
        """Download file from Dropbox using stored access token"""
        if not self.source_file_id:
            raise ValueError("Dropbox path and access token are required")

        try:
            dropbox_service = DropboxService(self.source_credentials)
            dropbox_service.authenticate()
            
            # Create a temporary directory for downloads
            download_dir = f"/tmp/nara/dropbox/{self.id}"
            os.makedirs(download_dir, exist_ok=True)
            
            file_info = dropbox_service.get_file_by_id(
                self.source_file_id,
                os.path.join(download_dir, self.name)
            )
            return file_info['local_path']
        except Exception as e:
            raise Exception(f"Error downloading from Dropbox: {str(e)}")

    def get_images_from_asset(self):
        local_path = self.get_file_path()
        return [get_base64_image(local_path)]
    
    def get_frames_from_video(self):
        local_path = self.get_file_path()
        try:
            return get_frames(local_path)
        except Exception as e:
            print(e)

    def get_video(self):
        return self.get_file_path()
    
    def get_audio(self):
        return self.get_file_path()

    def get_document_from_asset(self):
        try:
            logger.info(f"Getting document for asset {self.id} from source {self.upload_source}")
            file_path = self.get_file_path()
            logger.info(f"Got file path: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Error getting document from asset: {str(e)}")
            raise
    
    def concatenate_documents_fast(self, documents: List) -> str:
        # Use list comprehension and join for faster concatenation
        return ''.join(doc.get_text() for doc in documents)
    
    def concatenate_documents_parallel(self, documents: List) -> str:   
        # Use multiprocessing for parallel processing
        with concurrent.futures.ProcessPoolExecutor() as executor:
            texts = list(executor.map(lambda doc: doc.get_text(), documents))
        return ''.join(texts)
    
    def delete(self, *args, **kwargs):
        """Override delete to optionally do hard delete"""
        hard_delete = kwargs.pop('hard_delete', False)
        if hard_delete:
            super(NBaseWithOwnerModel, self).delete(*args, **kwargs)
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

def get_frames(video_path):
    video = cv2.VideoCapture(video_path)

    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()
    print(len(base64Frames), "frames read.")
    return base64Frames

def get_base64_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image from {image_path}")

    _, buffer = cv2.imencode(".jpg", image)
    base64_image = base64.b64encode(buffer).decode("utf-8")

    print("Image read and encoded.")
    return base64_image