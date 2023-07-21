import os
import boto3

# Boto is a bit flaky and magical with respect to configurqtion and the botocore Config
# object does not actually have the parameters we need, so we get these explicitly from
# the environment and pass to the client.
# see: https://botocore.amazonaws.com/v1/documentation/api/latest/reference/config.html

region_name = os.environ.get("AWS_REGION_NAME", "us-east-1")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "") # can be blank for localstack
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "") # can be blank for localstack

cognito_client = boto3.client('cognito-idp',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
    endpoint_url="https://localhost:4566",
    verify=False # don't check ssl for localstack
)

