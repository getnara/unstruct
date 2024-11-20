from django.db import models
from django.utils.translation import gettext_lazy as _
from llama_parse import LlamaParse
import nest_asyncio
import os
import concurrent.futures
from typing import List, Generator

from apps.common.utils.s3_utils import download_from_s3, S3Service
from apps.common.utils.gdrive_utils import GoogleDriveService
from apps.common.utils.dropbox_utils import DropboxService  # Import DropboxService

from apps.common.models import NBaseWithOwnerModel

from .project import Project


import cv2  # We're using OpenCV to read video, to install !pip install opencv-python
import base64
import time

import os
import requests

nest_asyncio.apply()

class ASSET_UPLOAD_SOURCE(models.TextChoices):
    UPLOAD = "UPLOAD", _("Upload")
    GDRIVE = "GOOGLE_DRIVE", _("Google Drive")
    DROPBOX = "DROPBOX", _("DropBox")
    AWS_S3 = "AWS_S3", _("Amazon S3")


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
    gdrive_file_id = models.CharField(max_length=100, null=True, blank=True)
    gdrive_credentials = models.JSONField(null=True, blank=True)
    s3_bucket = models.CharField(max_length=100, null=True, blank=True)
    s3_key = models.CharField(max_length=500, null=True, blank=True)
    s3_credentials = models.JSONField(null=True, blank=True)
    dropbox_path = models.CharField(max_length=1024, null=True, blank=True)
    dropbox_access_token = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.name)
    
    def get_file_path(self):
        """Get the local path or download the file if it's from an external source"""
        local_path = f"/tmp/{self.name}"
        
        if self.upload_source == ASSET_UPLOAD_SOURCE.GDRIVE:
            return self._download_from_gdrive()
        elif self.upload_source == ASSET_UPLOAD_SOURCE.AWS_S3:
            return self._download_from_s3()
        elif self.upload_source == ASSET_UPLOAD_SOURCE.DROPBOX:
            return self._download_from_dropbox()
        else:
            if not os.path.exists(local_path):
                download_from_s3(self.url, local_path)
            return local_path

    def _download_from_gdrive(self):
        """Download file from Google Drive using stored credentials"""
        if not self.gdrive_file_id or not self.gdrive_credentials:
            raise ValueError("Google Drive file ID and credentials are required")

        try:
            gdrive_service = GoogleDriveService(self.gdrive_credentials)
            gdrive_service.authenticate()
            
            # Create a temporary directory for downloads
            download_dir = f"/tmp/nara/gdrive/{self.id}"
            os.makedirs(download_dir, exist_ok=True)
            
            file_info = gdrive_service.get_file_by_id(
                self.gdrive_file_id, 
                os.path.join(download_dir, self.name)
            )
            return file_info['local_path']
        except Exception as e:
            raise Exception(f"Error downloading from Google Drive: {str(e)}")

    def _download_from_s3(self):
        """Download file from S3 using stored credentials"""
        if not self.s3_bucket or not self.s3_key:
            raise ValueError("S3 bucket and key are required")

        try:
            s3_service = S3Service(self.s3_credentials)  # Credentials are optional
            s3_service.authenticate()
            
            # Create a temporary directory for downloads
            download_dir = f"/tmp/nara/s3/{self.id}"
            os.makedirs(download_dir, exist_ok=True)
            
            file_info = s3_service.get_file_by_key(
                self.s3_bucket,
                self.s3_key,
                os.path.join(download_dir, self.name)
            )
            return file_info['local_path']
        except Exception as e:
            raise Exception(f"Error downloading from S3: {str(e)}")

    def _download_from_dropbox(self):
        """Download file from Dropbox using stored access token"""
        if not self.dropbox_path or not self.dropbox_access_token:
            raise ValueError("Dropbox path and access token are required")

        try:
            dropbox_service = DropboxService(self.dropbox_access_token)
            dropbox_service.authenticate()
            
            # Create a temporary directory for downloads
            download_dir = f"/tmp/nara/dropbox/{self.id}"
            os.makedirs(download_dir, exist_ok=True)
            
            file_info = dropbox_service.get_file_by_id(
                self.dropbox_path,
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
        return self.get_file_path()
    
    def concatenate_documents_fast(self, documents: List) -> str:
        # Use list comprehension and join for faster concatenation
        return ''.join(doc.get_text() for doc in documents)
    
    def concatenate_documents_parallel(self, documents: List) -> str:   
        # Use multiprocessing for parallel processing
        with concurrent.futures.ProcessPoolExecutor() as executor:
            texts = list(executor.map(lambda doc: doc.get_text(), documents))
        return ''.join(texts)
    

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