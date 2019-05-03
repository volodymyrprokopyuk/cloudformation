#!/usr/bin/env bash

set -eu

EC2_USER_DATA_TEMPLATE=ec2-user-data.sh
STACK_NAME=vlad-stack
TEMPLATE=iam_security-group.yaml

# Include the main.py and the requirements.txt into the ec2-user-data.sh
# Base64 encode the ec2-user-data.sh
EC2_USER_DATA=$(cat $EC2_USER_DATA_TEMPLATE \
    | sed -e '/{{MAIN.PY}}/{' -e 'r main.py' -e 'd' -e '}' \
    | sed -e '/{{REQUIREMENTS.TXT}}/{' -e 'r requirements.txt' -e 'd' -e '}' \
    | base64 -w0)

# Create a CloudFormation Stack with the ec2-user-data.sh
aws cloudformation create-stack --stack-name $STACK_NAME \
    --template-body file://$(pwd)/$TEMPLATE \
    --parameters ParameterKey=UserData,ParameterValue=$EC2_USER_DATA \
    --capabilities CAPABILITY_NAMED_IAM
