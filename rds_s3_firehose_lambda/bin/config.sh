# readonly CF_STACK_NAME=vlad-stack
# readonly CF_DIR=$(pwd)/cloudformation
# readonly CF_TEMPLATE=$CF_DIR/rds_s3_firehose_lambda.yaml

readonly DB_PORT=5432
readonly DB_NAME=infringement
readonly DB_USER=vld
readonly DB_PASSWORD='Password1!'
# Update DB_HOST=RDS Endpoint.Address after successful ./bin/deploy_service_stack.sh
DB_HOST=idfoo99u1uca9o.c07z8n4r5v4a.eu-central-1.rds.amazonaws.com

# readonly S3_FIREHOSE_DELIVERY_STREAM_BUCKET_NAME=${CF_STACK_NAME}-firehose-delivery-stream
# Create lambda package S3 bucket outside of the CF_STACK_NAME
readonly S3_LAMBDA_PACKAGE_BUCKET_NAME=infringement-transform-lambda-package

readonly LAMBDA_ROOT_DIR=$(pwd)/lambda/function
readonly LAMBDA_PUT_PRODUCT_IN_DB_VERSION=$(cat $LAMBDA_ROOT_DIR/PutProductInDbLambda/version)
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION=$(cat $LAMBDA_ROOT_DIR/PutInfringementInDbLambda/version)
readonly LAMBDA_LOG_LEVEL=DEBUG
