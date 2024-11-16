import json
import os
from recorder2 import main
from s3_connect import upload_files_to_s3

def handler(event, context):
    print(event)

    if event.get('httpMethod') == 'POST':
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "status": "error",
                        "message": "Invalid JSON",
                    }
                )
            }
    else:
        return {
            "statusCode": 405,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": "Method Not Allowed",
                }
            )
        }

    try:
        username = body['username']
        password = body['password']
        links = body['links']
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": "Missing required fields: username, password, links",
                }
            )
        }

    s3_bucket_url = os.environ.get('S3_BUCKET_URL')
    s3_bucket_access_key = os.environ.get('S3_BUCKET_ACCESS_KEY')
    if s3_bucket_url is None or s3_bucket_access_key is None:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": "Missing S3 configuration",
                }
            )
        }

    try:
        main(username, password, links)
        urls = upload_files_to_s3('output', s3_bucket_url, s3_bucket_access_key)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "status": "success",
                    "message": "pages parsed and uploaded to S3",
                    "links": urls
                }
            )
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": str(e),
                    "links": []
                }
            )
        }

