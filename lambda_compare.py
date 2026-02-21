import boto3
import hashlib

s3 = boto3.client("s3")


def calculate_hash(stream):
    """Compute MD5 hash of streamed S3 object."""
    hasher = hashlib.md5()

    for chunk in iter(lambda: stream.read(4096), b""):
        hasher.update(chunk)

    return hasher.hexdigest()


def lambda_handler(event, context):
    bucket = event["bucket"]
    key1 = event["file1"]
    key2 = event["file2"]

    obj1 = s3.get_object(Bucket=bucket, Key=key1)
    obj2 = s3.get_object(Bucket=bucket, Key=key2)

    hash1 = calculate_hash(obj1["Body"])
    hash2 = calculate_hash(obj2["Body"])

    return {
        "file1": key1,
        "file2": key2,
        "hash1": hash1,
        "hash2": hash2,
        "are_equal": hash1 == hash2,
    }