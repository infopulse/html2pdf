import os
import boto3
import logging
from urllib.parse import urljoin
from pathlib import Path

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(handler)


def upload_files_to_s3(folder_path: str,
                       bucket_name: str,
                       s3_base_url: str) -> list[str]:
    s3 = boto3.client('s3')
    file_urls = []

    output_folder = Path(folder_path)
    log.debug(f"looking for files in {output_folder.absolute()}")

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
