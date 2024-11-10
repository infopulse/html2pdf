# AWS setup guide

1. Build the docker image
2. Create ECR and upload the docker image to it
3. Create Lambda function using the docker image
4. Set environment variables for the Lambda function:
    - S3_BUCKET_URL
    - S3_BUCKET_ACCESS_KEY
5. Create API Gateway and link it to the Lambda function

# Usage

- Send a POST request to the API Gateway with the following body:

``` json
{
    "username": "user",
    "password": "password",
    "links": [
        "https://123456",
        "https://456789"
    ]
}
```

- The lambda function will parse the web pages, save them to PDF and upload them to the S3 bucket.
- The lambda function will return the S3 bucket URL where the PDFs are stored.

``` json
 {
   "status": "success",
   "message": "pages parsed and uploaded to S3",
   "links": [
       "https://s3.amazonaws.com/bucket-name/123456.pdf",
       "https://s3.amazonaws.com/bucket-name/456789.pdf"
   ]
}
```
# Next steps
- Create another lambda function with static html to call the API Gateway and display the PDFs in a web page.
- As example use the example in the static folder