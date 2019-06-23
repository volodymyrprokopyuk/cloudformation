# VPC, Subnet, SecurityGroups, EC2

```bash
# Validate the CloudFormation template and Python source code before creating a stack
./bin/validate.sh
# Manually create vlad-stack-lambda-package S3 bucket to upload Lambda packages
aws s3 mb s3://vlad-stack-lambda-package
# Check version of each lambda to upload
# Create and upload Lambda packages to S3 Lambda package S3 bucket
./bin/upload_lambda.sh
# Create [-c] or update a CloudFormation stack
./bin/deploy_stack.sh [-c]
# Update DB_HOST=RDS Endpoint.Address in ./bin/config.sh
# Create database schema in RDS or in localhost [-l]
./bin/create_db_schema.sh [-l]
# Update Kinesis Firehose delivery stream S3 bucket NotificaitonConfiguration
./bin/update_firehose_s3_bucket_notification_configuration.sh
# Upload product.txt and infringement.txt to Kinesis Firehose delivery stream
./bin/upload_data.sh

# Delete the CloudFormation Stack
aws s3 rm s3://vlad-stack-firehose-delivery-stream --recursive
aws cloudformation delete-stack --stack-name vlad-stack
# Optionally delete lambda packages and remove Lambda package S3 bucket
aws s3 rm s3://vlad-stack-lambda-package --recursive
aws s3 rb s3://vlad-stack-lambda-package
```
