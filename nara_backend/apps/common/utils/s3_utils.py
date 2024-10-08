import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from urllib.parse import urlparse

def download_from_s3(s3_url, local_path):
    s3 = boto3.client('s3')
    bucket_name, key = parse_s3_url(s3_url)
    print(f"Attempting to download from bucket: {bucket_name}, key: {key}")
    try:
        s3.download_file(bucket_name, key, local_path)
    except NoCredentialsError:
        print("Credentials not available")
    except ClientError as e:
        print(f"Client error: {e}")

def parse_s3_url(s3_url):
    print(s3_url)
    # Parse the URL
    parsed_url = urlparse(s3_url)
    
    # Extract the bucket name from the hostname
    bucket_name = parsed_url.netloc.split('.')[0]
    
    # The key is the path without the leading '/'
    key = parsed_url.path.lstrip('/')
    
    print(bucket_name, key)
    return bucket_name, key
