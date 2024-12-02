import os
import boto3
import logging
from urllib.parse import urljoin
from pathlib import Path
import shutil
import os

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log.addHandler(handler)


def upload_files_to_s3(folder_path: str,
                       bucket_name: str) -> list[str]:
    s3 = boto3.client('s3')
    file_urls = []

    output_folder = folder_path

    for file in Path(folder_path).iterdir():
        log.debug(f"[DEV]PATH LOG {file}")
        if file.is_file():
            s3_key = file.name
            try:
                print(str(file), bucket_name, s3_key)
                s3.upload_file(str(file), bucket_name, s3_key)
                url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': s3_key},
                    ExpiresIn=3600
                )
                file_urls.append(url)
            except Exception as e:
                print(f"Error uploading file {file}: {e}")
    return file_urls

def cleanup():
    folder_path = '/tmp/output'
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' has been removed.")
    else:
        print(f"Folder '{folder_path}' does not exist.")
