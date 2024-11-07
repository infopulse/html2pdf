import os
import boto3
from urllib.parse import urljoin
from pathlib import Path


def upload_files_to_s3(folder_path: str,
                       bucket_name: str,
                       s3_base_url: str) -> list[str]:
    s3 = boto3.client('s3')
    file_urls = []

    for file in Path(folder_path).iterdir():
        if file.is_file():
            s3_key = file.name
            try:
                s3.upload_file(str(file), bucket_name, s3_key)
                file_url = urljoin(s3_base_url, s3_key)
                file_urls.append(file_url)
            except Exception as e:
                print(f"Error uploading file {file}: {e}")
    return file_urls
