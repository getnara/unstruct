from django.db import models
from django.utils.translation import gettext_lazy as _
from llama_parse import LlamaParse
from llama_index.readers.smart_pdf_loader import SmartPDFLoader
import nest_asyncio
import os
from apps.common.utils.s3_utils import download_from_s3

from apps.common.models import NBaseWithOwnerModel

from .project import Project

nest_asyncio.apply()

LLMSHERPA_API_URL = "https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"

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

        #Load the document using LlamaParse
        parser = LlamaParse(
            api_key=os.getenv("LLAMA_CLOUD_API_KEY"),  # Ensure this is set in your environment
            result_type="markdown",  # or "markdown"
            verbose=True,
            gpt4o_mode=True,
            gpt4o_api_key=os.getenv("OPENAI_API_KEY")
        )
        # pdf_loader = SmartPDFLoader(llmsherpa_api_url=LLMSHERPA_API_URL)
        # documents = pdf_loader.load_data(local_path)

        documents = parser.load_data(local_path)
        
        # Concatenate text from all document parts
        full_text = ""
        for doc in documents:
            full_text += doc.get_text()  # or doc.text, depending on the correct method/attribute
        
        return full_text