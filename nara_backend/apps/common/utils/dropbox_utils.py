from dropbox import Dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import FileMetadata, FolderMetadata
import os
from typing import Dict, Generator, Optional

class DropboxService:
    """Service class to handle Dropbox operations"""
    
    def __init__(self, access_token: str = None):
        """
        Initialize Dropbox service with access token
        Args:
            access_token: Dropbox access token
        """
        self.access_token = access_token
        self.client = None
        
    def authenticate(self):
        """Authenticate with Dropbox using access token"""
        try:
            if not self.access_token:
                raise ValueError("Dropbox access token is required")
                
            # Print token format for debugging
            print(f"Token type: {type(self.access_token)}")
            print(f"Token length: {len(str(self.access_token))}")
            
            # Handle token if it's in JSON format
            if isinstance(self.access_token, dict):
                token = self.access_token.get('access_token')
            else:
                token = self.access_token
                
            if not token:
                raise ValueError("Invalid token format")
                
            self.client = Dropbox(token)
            # Test the connection
            self.client.users_get_current_account()
        except AuthError as e:
            raise Exception(f"Error authenticating with Dropbox: Invalid access token. Details: {str(e)}")
        except Exception as e:
            raise Exception(f"Error authenticating with Dropbox: {str(e)}")
    
    def get_file_by_id(self, file_path: str, download_path: str = None) -> Dict:
        """
        Get a single file from Dropbox by its path
        Args:
            file_path: Path to the file in Dropbox
            download_path: Optional path to download the file
        """
        try:
            metadata = self.client.files_get_metadata(file_path)
            
            if isinstance(metadata, FolderMetadata):
                raise Exception("Cannot download a folder directly. Use list_folder_contents instead.")
            
            file_info = {
                'id': metadata.path_display,
                'name': metadata.name,
                'size': metadata.size,
                'mime_type': self._get_mime_type(metadata.name),
                'last_modified': metadata.client_modified
            }
            
            if download_path:
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                with open(download_path, 'wb') as f:
                    metadata, response = self.client.files_download(file_path)
                    f.write(response.content)
                file_info['local_path'] = download_path
                
            return file_info
            
        except ApiError as e:
            if e.error.is_path():
                raise Exception(f"File not found: {file_path}")
            raise Exception(f"Error getting file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error getting file: {str(e)}")
    
    def list_folder_contents(self, folder_path: str = "", recursive: bool = True) -> Generator[Dict, None, None]:
        """
        List contents of a Dropbox folder
        Args:
            folder_path: Path to the folder in Dropbox
            recursive: Whether to recursively list contents of subfolders
        """
        try:
            result = self.client.files_list_folder(
                folder_path,
                recursive=recursive
            )
            
            while True:
                for entry in result.entries:
                    # Skip folders if we're just interested in files
                    if isinstance(entry, FolderMetadata):
                        continue
                        
                    yield {
                        'id': entry.path_display,
                        'name': entry.name,
                        'size': entry.size,
                        'mime_type': self._get_mime_type(entry.name),
                        'last_modified': entry.client_modified
                    }
                
                # Check if there are more files to load
                if not result.has_more:
                    break
                    
                result = self.client.files_list_folder_continue(result.cursor)
                
        except ApiError as e:
            if e.error.is_path():
                raise Exception(f"Folder not found: {folder_path}")
            raise Exception(f"Error listing folder contents: {str(e)}")
        except Exception as e:
            raise Exception(f"Error listing folder contents: {str(e)}")
            
    def _get_mime_type(self, filename: str) -> str:
        """Get mime type based on file extension"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
