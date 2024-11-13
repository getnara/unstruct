from django.db import models
from django.utils.translation import gettext_lazy as _
from llama_parse import LlamaParse
import nest_asyncio
import os
import concurrent.futures
from typing import List, Generator

from apps.common.utils.s3_utils import download_from_s3

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
        blank=False,
        on_delete=models.CASCADE,
    )
    url = models.URLField()
    upload_source = models.CharField(
        max_length=200,
        choices=ASSET_UPLOAD_SOURCE,
    )
    file_type = models.CharField(max_length=200, choices=ASSET_FILE_TYPE, default=ASSET_FILE_TYPE.OTHER)

    def __str__(self) -> str:
        return str(self.name)
    

    def get_images_from_asset(self):
        local_path = f"/tmp/{self.name}"
        download_from_s3(self.url, local_path) 
        return [get_base64_image(local_path)]
    

    def get_frames_from_video(self):
        local_path = f"/tmp/{self.name}"
        download_from_s3(self.url, local_path) 
        try:
            return get_frames(local_path)
        except Exception as e:
            print(e)

    def get_video(self):
        local_path = f"/tmp/{self.name}"
        if not os.path.exists(local_path):
            download_from_s3(self.url, local_path) 
        return local_path
    
    def get_audio(self):
        local_path = f"/tmp/{self.name}"
        if not os.path.exists(local_path):
            download_from_s3(self.url, local_path) 
        return local_path


    def get_document_from_asset(self):
        local_path = f"/tmp/{self.name}"
        if not os.path.exists(local_path):
            download_from_s3(self.url, local_path) 
        return local_path
    
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