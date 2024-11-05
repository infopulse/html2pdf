import json
from recorder2 import main
from s3_connect import upload_files_to_s3

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps(
                    {
                        "status": "error",
                        "message": "Invalid JSON",
                        "links": []
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
                    "links": []
                }
            )
        }

    try:
        username = body['username']
        password = body['password']
        links = body['links']
        s3_bucket_url = body['s3_bucket_url']
        s3_bucket_access_key = body['s3_bucket_access_key']
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {
                    "status": "error",
                    "message": "Missing required field",
                    "links": []
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
                    "message": "Hello from Lambda!",
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

