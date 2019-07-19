readonly SETOPTS=-eux

set $SETOPTS

# Application and environment configuration
readonly APPLICATION=infringement
readonly ENVIRONMENT=DEV
readonly PYVENV=pyvenv

# infirngement-ingest service configuration
readonly S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX=firehose-infringement-delivery

# infringement-transform service configuration
readonly S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME=infringement-transform-lambda-package
readonly LAMBDA_LOG_LEVEL=DEBUG
readonly LAMBDA_FUNCTION_DIR=$(pwd)/lambda/function
readonly LAMBDA_LIB_DIR=$(pwd)/lambda/lib
readonly LAMBDA_PUT_PRODUCT_IN_DB_VERSION=$(cat $LAMBDA_FUNCTION_DIR/PutProductInDbLambda/version)
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION=$(cat $LAMBDA_FUNCTION_DIR/PutInfringementInDbLambda/version)
readonly SNS_INFRINGEMENT_IMPORT_ALARM_NOTIFICATION_EMAIL=volodymyr.prokopyuk@nagra.com

# infringement-store service configuration
readonly BASTION_USER=ec2-user
readonly DB_PORT=5432
readonly DB_LOCAL_PORT=15432
readonly DB_NAME=infringement
readonly DB_SUPER_USER=super
readonly DB_SUPER_PASSWORD='Password1!'
readonly DB_INGEST_USER=ingest
readonly DB_INGEST_PASSWORD='Password1!'
