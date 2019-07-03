# VPC, Subnet, SecurityGroups, RDS, Kinesis Firehose, S3, Lambda

```bash
# Validate cloudformation/infirngement_store.yaml template
./bin/validate_cf_template.sh cloudformation/infringement_store.yaml
# Deploy (create -c or update) infirngement-store service stack
./bin/deploy_service_stack.sh infringement-store [-c]

# Create database schema in RDS or in localhost [-l]
./bin/create_db_schema.sh [-l]

# Validate cloudformation/infirngement_ingest.yaml template
./bin/validate_cf_template.sh cloudformation/infringement_ingest.yaml
# Deploy (create -c or update) infirngement-ingest service stack
./bin/deploy_service_stack.sh infringement-ingest [-c]

# Downlaod psycopg2 with statically linked libpg
# because AWS Lambda environment does not have libpg
git clone https://github.com/jkehler/awslambda-psycopg2.git
cp -r psycopg2-3.7 lambda/lib/psycopg2
# Validate Python source code before uploading lambdas packages to S3
./bin/validate_py_code.sh
# Check the version of each lambda package in the corresponding version file
# Create and upload lambda packages to S3 bucket
./bin/upload_transform_lambda_to_s3.sh

# Validate cloudformation/infirngement_transform.yaml template
./bin/validate_cf_template.sh cloudformation/infringement_transform.yaml
# Deploy (create -c or update) infirngement-transform service stack
./bin/deploy_service_stack.sh infringement-transform [-c]

# Update Kinesis Firehose infringement delivery S3 bucket to trigger transformation
# Lambdas on new S3 objects creation
./bin/update_ingest_stack.sh


# Upload the product.txt and the infringement.txt
# to the corresponding Kinesis Firehose delivery streams
./bin/send_data_to_firehose.sh


# DELETE APPLICATION SERVICE STACKS
# Delete Kinesis Firehose infirngement delivery S3 bucket content
aws s3 rm s3://$APPLICATION-ingest-$ENVIRONMENT-firehose-infringement-delivery --recursive
# Delete application service stacks
aws cloudformation delete-stack --stack-name $APPLICATION-transform-$ENVIRONMENT
aws cloudformation delete-stack --stack-name $APPLICATION-ingest-$ENVIRONMENT
aws cloudformation delete-stack --stack-name $APPLICATION-store-$ENVIRONMENT

# Optionally delete transform lambda package S3 bucket content
aws s3 rm s3://infringement-transform-lambda-package --recursive
# Optionally delete transform lambda package S3 bucket
aws s3 rb s3://infringement-transform-lambda-package
```
