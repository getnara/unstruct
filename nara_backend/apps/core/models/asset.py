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

nest_asyncio.apply()

class ASSET_UPLOAD_SOURCE(models.TextChoices):
    UPLOAD = "UPLOAD", _("Upload")
    GDRIVE = "GOOGLE_DRIVE", _("Google Drive")
    DROPBOX = "DROPBOX", _("DropBox")
    AWS_S3 = "AWS_S3", _("Amazon S3")


class ASSET_FILE_TYPE(models.TextChoices):
    PDF = "PDF", _("Pdf")
    DOC = "DOC", _("Doc")
    TXT = "TXT", _("Text")
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

    def get_document_from_asset(self):
        # Define a local path to save the downloaded file
        local_path = f"/tmp/{self.name}"

        # Download the file from S3
        download_from_s3(self.url, local_path) 

        # Load the document using LlamaParse
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),  # Ensure this is set in your environment
            result_type="text",  # or "markdown"
            verbose=True,
            gpt4o_mode=True,
            gpt4o_api_key=os.getenv("OPENAI_API_KEY")
        )
        documents = parser.load_data(local_path)
        
        return self.concatenate_documents_fast(documents)
    
    def concatenate_documents_fast(self, documents: List) -> str:
        # Use list comprehension and join for faster concatenation
        return ''.join(doc.get_text() for doc in documents)
    
    def concatenate_documents_parallel(self, documents: List) -> str:   
        # Use multiprocessing for parallel processing
        with concurrent.futures.ProcessPoolExecutor() as executor:
            texts = list(executor.map(lambda doc: doc.get_text(), documents))
        return ''.join(texts)
    