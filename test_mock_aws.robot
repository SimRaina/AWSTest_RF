*** Settings ***
Library    mock_aws_library.py

*** Test Cases ***
Full AWS Mock Test
    Start Mock AWS

    # S3
    Create S3 Bucket    demo-bucket
    ${buckets}=    List S3 Buckets
    Should Contain    ${buckets}    demo-bucket

    # SQS
    ${url}=    Create Queue    demo-queue
    Send Message    ${url}    hello world
    ${msgs}=    Receive Messages    ${url}
    Should Contain    ${msgs}    hello world

    # DynamoDB
    Create Table    demo-table
    Put Item    demo-table    1    value123
    ${val}=    Get Item    demo-table    1
    Should Be Equal    ${val}    value123

    Stop Mock AWS