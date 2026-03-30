import os
# force local lambda execution
os.environ["MOTO_LAMBDA_EXECUTOR"] = "local"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
import boto3
import logging
from moto import mock_aws
from robot.api.deco import keyword
from robot.api import logger
import json
import zipfile
import io

# Configure Python logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("mockaws")

_mock = None


def _log(message):
    """Log to both Robot Framework and Python logger."""
    logger.info(message)     # shows in Robot log.html
    log.info(message)        # shows in console


@keyword
def start_mock_aws():
    global _mock
    _log("Starting Moto AWS mock environment")
    _mock = mock_aws()
    _mock.start()
    _log("Moto AWS mock started successfully")


@keyword
def stop_mock_aws():
    global _mock
    if _mock:
        _log("Stopping Moto AWS mock environment")
        _mock.stop()
        _mock = None
        _log("Moto AWS mock stopped")


# ---------- S3 ----------
@keyword
def create_s3_bucket(bucket_name, region="us-east-1"):
    _log(f"Creating S3 bucket: {bucket_name}")
    s3 = boto3.client("s3", region_name=region)
    s3.create_bucket(Bucket=bucket_name)
    _log(f"S3 bucket created: {bucket_name}")


@keyword
def list_s3_buckets():
    _log("Listing S3 buckets")
    s3 = boto3.client("s3", region_name="us-east-1")
    response = s3.list_buckets()
    buckets = [b["Name"] for b in response["Buckets"]]
    _log(f"Buckets found: {buckets}")
    return buckets


@keyword
def put_file_to_s3(bucket, key, content):
    _log(f"Uploading object '{key}' to bucket '{bucket}'")
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.put_object(Bucket=bucket, Key=key, Body=content)
    _log("Upload successful")


@keyword
def list_s3_objects(bucket):
    _log(f"Listing objects in bucket: {bucket}")
    s3 = boto3.client("s3", region_name="us-east-1")
    response = s3.list_objects_v2(Bucket=bucket)
    objects = [obj["Key"] for obj in response.get("Contents", [])]
    _log(f"Objects found: {objects}")
    return objects

@keyword
def deploy_lambda(function_name, role_arn, handler_file="lambda_compare.lambda_handler"):
    """Deploy Lambda function to Moto."""
    _log(f"Deploying Lambda function: {function_name}")

    lambda_client = boto3.client("lambda", region_name="us-east-1")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as z:
        z.write("lambda_compare.py")

    zip_buffer.seek(0)

    lambda_client.create_function(
        FunctionName=function_name,
        Runtime="python3.11",
        Role=role_arn,
        Handler=handler_file,
        Code={"ZipFile": zip_buffer.read()},
        Publish=True,
    )

    _log("Lambda deployed successfully")


@keyword
def invoke_lambda(function_name, payload_dict):
    """Invoke lambda locally (no docker)."""
    _log(f"Invoking Lambda locally: {function_name}")

    import lambda_compare

    result = lambda_compare.lambda_handler(payload_dict, None)

    _log(f"Lambda response: {result}")
    return result

@keyword
def create_lambda_execution_role(role_name="lambda-role"):
    """Create IAM role that Lambda can assume."""
    _log(f"Creating IAM role for Lambda: {role_name}")

    iam = boto3.client("iam", region_name="us-east-1")

    assume_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    role = iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_policy),
    )

    arn = role["Role"]["Arn"]
    _log(f"IAM Role created: {arn}")
    return arn