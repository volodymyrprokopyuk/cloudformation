# VPC, Subnet, SecurityGroups, EC2

```bash
# Validate the CloudFormation template and Python source code before creating a stack
./bin/validate.sh
# Create [-c] or update a CloudFormation Stack
./bin/deploy_rds_s3_firehose.sh [-c]
# Create database schema in RDS or in localhost [-l]
# Update DB_HOST=RDS Endpoint.Address in ./bin/config.sh
./bin/create_db_schema.sh [-l]
# Create and upload Lambda packages to S3 Lambda package bucket (check version)
./bin/upload_lambda.sh

# Upload product.txt and infringement.txt to Kinesis Firehose delivery stream
./bin/upload_data.sh
# Delete the CloudFormation Stack
aws s3 rm s3://vlad-stack-firehose-delivery-stream --recursive
aws s3 rm s3://vlad-stack-lambda-package --recursive
aws cloudformation delete-stack --stack-name vlad-stack
```
