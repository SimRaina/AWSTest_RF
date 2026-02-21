*** Settings ***
Library    mock_aws_library.py

*** Variables ***
${BUCKET}      compare-bucket
${FILE1}       file1.txt
${FILE2}       file2.txt
${LAMBDA}      compare-files

*** Test Cases ***
Compare Two Files Using Lambda
    Start Mock AWS

    Create S3 Bucket    ${BUCKET}

    Put File To S3    ${BUCKET}    ${FILE1}    HELLO WORLD
    Put File To S3    ${BUCKET}    ${FILE2}    HELLO WORLD

    # create IAM role
    ${role}=    Create Lambda Execution Role

    # deploy lambda with role
    Deploy Lambda    ${LAMBDA}    ${role}

    ${payload}=    Create Dictionary
    ...    bucket=${BUCKET}
    ...    file1=${FILE1}
    ...    file2=${FILE2}

    ${result}=    Invoke Lambda    ${LAMBDA}    ${payload}

    Should Be True    ${result['are_equal']}

    Stop Mock AWS