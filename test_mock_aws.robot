*** Settings ***
Library    mock_aws_library.py

*** Test Cases ***
Full AWS Mock Test
    Start Mock AWS

    # S3
    Create S3 Bucket    demo-bucket
    ${buckets}=    List S3 Buckets
    Should Contain    ${buckets}    demo-bucket
    Stop Mock AWS