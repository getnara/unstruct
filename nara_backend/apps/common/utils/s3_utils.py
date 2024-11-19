import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from urllib.parse import urlparse
from typing import Dict, List, Generator, Optional
import os

class S3Service:
    """Service class to handle AWS S3 operations"""
    
    def __init__(self, credentials: Optional[Dict] = None):
        """
        Initialize S3 service with optional credentials
        Args:
            credentials: Optional dict with aws_access_key_id, aws_secret_access_key, and aws_session_token
        """
        self.credentials = credentials
        self.s3_client = None
        
    def authenticate(self):
        """Authenticate with AWS using provided credentials or environment variables"""
        try:
            if self.credentials:
                kwargs = {}
                if self.credentials.get('aws_access_key_id'):
                    kwargs['aws_access_key_id'] = self.credentials.get('aws_access_key_id')
                if self.credentials.get('aws_secret_access_key'):
                    kwargs['aws_secret_access_key'] = self.credentials.get('aws_secret_access_key')
                if self.credentials.get('aws_session_token'):
                    kwargs['aws_session_token'] = self.credentials.get('aws_session_token')
                if self.credentials.get('region_name'):
                    kwargs['region_name'] = self.credentials.get('region_name')
                    
                self.s3_client = boto3.client('s3', **kwargs)
            else:
                # Use default credentials from environment or IAM role
                self.s3_client = boto3.client('s3')
        except Exception as e:
            raise Exception(f"Error authenticating with AWS: {str(e)}")
    
    def get_files_from_bucket(self, bucket: str, prefix: str = None, recursive: bool = True) -> Generator[Dict, None, None]:
        """
        List contents of an S3 bucket
        Args:
            bucket: Name of the S3 bucket
            prefix: Prefix to filter objects (like folder path)
            recursive: Whether to recursively list contents of folders
        """
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            # Build the prefix
            if prefix:
                prefix = prefix.rstrip('/') + '/' if not prefix.endswith('/') else prefix
            
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix or ''):
                for obj in page.get('Contents', []):
                    key = obj['Key']
                    
                    # Skip empty "folder" objects (objects ending with / and size 0)
                    if key.endswith('/') and obj['Size'] == 0:
                        continue
                        
                    # Skip files in subfolders if not recursive
                    if not recursive:
                        key_without_prefix = key[len(prefix or ''):]
                        if '/' in key_without_prefix:
                            continue
                    
                    # Skip the prefix itself if it's returned as an object
                    if prefix and key == prefix:
                        continue
                        
                    yield {
                        'id': key,  # Use the object key as ID
                        'name': os.path.basename(key),
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'bucket': bucket
                    }
                    
        except Exception as e:
            raise Exception(f"Error listing bucket contents: {str(e)}")
    
    def get_file_by_key(self, bucket: str, key: str, download_path: str = None) -> Dict:
        """
        Get a single file from S3 by its key
        Args:
            bucket: Name of the S3 bucket
            key: Object key in the bucket
            download_path: Optional path to download the file
        """
        try:
            file_info = {
                'id': key,
                'name': os.path.basename(key),
                'bucket': bucket
            }
            
            # Download the file if path provided
            if download_path:
                os.makedirs(os.path.dirname(download_path), exist_ok=True)
                try:
                    self.s3_client.download_file(bucket, key, download_path)
                    file_info['local_path'] = download_path
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        raise Exception(f"File not found: {key}")
                    elif e.response['Error']['Code'] == '403':
                        raise Exception(f"Access denied to file: {key}. Please check your credentials and permissions.")
                    else:
                        raise
                
            return file_info
            
        except Exception as e:
            raise Exception(f"Error getting file: {str(e)}")

def download_from_s3(s3_url, local_path):
    try:
        s3 = boto3.client('s3')
        bucket_name, key = parse_s3_url(s3_url)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(bucket_name, key, local_path)
    except NoCredentialsError:
        raise Exception("AWS credentials not available")
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise Exception(f"File not found: {s3_url}")
        elif e.response['Error']['Code'] == '403':
            raise Exception(f"Access denied to file: {s3_url}. Please check your credentials and permissions.")
        else:
            raise Exception(f"Error downloading file: {str(e)}")
    except Exception as e:
        raise Exception(f"Error downloading file: {str(e)}")

def parse_s3_url(s3_url):
    # Parse the URL
    parsed_url = urlparse(s3_url)
    
    # Extract the bucket name from the hostname
    bucket_name = parsed_url.netloc.split('.')[0]
    
    # The key is the path without the leading '/'
    key = parsed_url.path.lstrip('/')
    
    return bucket_name, key
