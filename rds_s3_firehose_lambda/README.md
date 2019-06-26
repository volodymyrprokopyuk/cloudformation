# VPC, Subnet, SecurityGroups, EC2

```bash
# Downlaod the psycopg2 with statically linked libpg
# because AWS Lambda environment does not have libpg
git clone https://github.com/jkehler/awslambda-psycopg2.git
cp -r psycopg2-3.7 lambda/lib/psycopg2
# Validate the Python source code before uploading the lambdas to S3
./bin/validate_py_code.sh
# Check the version of each lambda to upload to S3 in the corresponding version file
# Create and upload lambda packages to the S3 lambda package bucket
./bin/upload_lambda.sh

# Validate the CloudFormation template before creating a stack
./bin/validate_cf_template.sh
# Create [-c] or update a CloudFormation stack
./bin/deploy_stack.sh [-c]
# Update DB_HOST=RDS Endpoint.Address in ./bin/config.sh
# Create the database schema in RDS or in localhost [-l]
./bin/create_db_schema.sh [-l]
# Update the Kinesis Firehose delivery streams S3 bucket NotificaitonConfiguration
./bin/update_firehose_s3_bucket_notification_configuration.sh

# Upload the product.txt and the infringement.txt
# to the corresponding Kinesis Firehose delivery streams
./bin/send_data.sh

# Delete the CloudFormation Stack
aws s3 rm s3://vlad-stack-firehose-delivery-stream --recursive
aws cloudformation delete-stack --stack-name vlad-stack
# Optionally delete the lambda packages and remove the lambda package S3 bucket
aws s3 rm s3://vlad-stack-lambda-package --recursive
aws s3 rb s3://vlad-stack-lambda-package
```
