from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import os
import io
from typing import List, Dict, Generator, Optional, Union

class GoogleDriveService:
    """Service class to handle Google Drive operations using either service account or OAuth tokens"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, credentials_info: Union[dict, str] = None, oauth_tokens: Optional[dict] = None):
        self.credentials = None
        self.service = None
        self.credentials_info = credentials_info
        self.oauth_tokens = oauth_tokens
        
        if not self.credentials_info and not self.oauth_tokens:
            raise ValueError("Either service account credentials or OAuth tokens are required")
    
    def authenticate(self):
        """Authenticate with Google Drive using either service account or OAuth tokens"""
        try:
            if self.oauth_tokens:
                self.credentials = Credentials(
                    token=self.oauth_tokens.get('access_token'),
                    refresh_token=self.oauth_tokens.get('refresh_token'),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=os.getenv('GOOGLE_CLIENT_ID'),
                    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                    scopes=self.SCOPES
                )
            else:
                self.credentials = service_account.Credentials.from_service_account_info(
                    self.credentials_info,
                    scopes=self.SCOPES
                )
            
            self.service = build('drive', 'v3', credentials=self.credentials)
        except Exception as e:
            raise Exception(f"Error authenticating with Google Drive: {str(e)}")
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """Get metadata for a file"""
        try:
            return self.service.files().get(fileId=file_id, fields="id, name, mimeType, parents").execute()
        except Exception as e:
            raise Exception(f"Error getting file metadata: {str(e)}")
    
    def download_file(self, file_id: str, local_path: str) -> str:
        """Download a file from Google Drive"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file.seek(0)
            with open(local_path, 'wb') as f:
                f.write(file.read())
            return local_path
        except Exception as e:
            raise Exception(f"Error downloading file: {str(e)}")
    
    def get_file_by_id(self, file_id: str, download_path: str = None) -> Dict:
        """Get file content and metadata"""
        try:
            metadata = self.get_file_metadata(file_id)
            if metadata['mimeType'] == 'application/vnd.google-apps.folder':
                raise Exception("Cannot download a folder directly. Use list_folder_contents instead.")
            
            file_info = {
                'id': metadata['id'],
                'name': metadata['name'],
                'mime_type': metadata['mimeType']
            }
            
            if download_path:
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                self.download_file(file_id, download_path)
                file_info['local_path'] = download_path
                
            return file_info
            
        except Exception as e:
            raise Exception(f"Error getting file: {str(e)}")
    
    def list_folder_contents(self, folder_id: str, recursive: bool = True) -> Generator[Dict, None, None]:
        """
        List contents of a folder. If recursive is True, also list contents of subfolders.
        Returns a generator of file metadata.
        """
        try:
            # Get all files in the folder
            query = f"'{folder_id}' in parents and trashed = false"
            page_token = None
            
            while True:
                results = self.service.files().list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, parents)",
                    pageToken=page_token
                ).execute()
                
                
                for item in results.get('files', []):
                    if item['mimeType'] == 'application/vnd.google-apps.folder' and recursive:
                        # Recursively get contents of subfolders
                        yield from self.list_folder_contents(item['id'], recursive)
                    else:
                        yield item
                
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
                    
        except Exception as e:
            raise Exception(f"Error listing folder contents: {str(e)}")
    
    def get_files_by_ids(self, file_ids: List[str]) -> Generator[Dict, None, None]:
        """Get multiple files by their IDs"""
        for file_id in file_ids:
            try:
                yield self.get_file_by_id(file_id)
            except Exception as e:
                print(f"Error processing file {file_id}: {str(e)}")
                continue
    
    def get_folder_contents(self, folder_id: str, recursive: bool = True) -> Generator[Dict, None, None]:
        """
        Download all files in a folder. If recursive is True, also download files in subfolders.
        Returns a generator of file information dictionaries.
        """
        try:
            for item in self.list_folder_contents(folder_id, recursive):
                if item['mimeType'] != 'application/vnd.google-apps.folder':
                    try:
                        yield self.get_file_by_id(item['id'])
                    except Exception as e:
                        print(f"Error downloading file {item['name']}: {str(e)}")
                        continue
        except Exception as e:
            raise Exception(f"Error processing folder contents: {str(e)}")
