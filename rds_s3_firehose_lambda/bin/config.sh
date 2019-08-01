readonly SETOPTS=-eux

set $SETOPTS

# Common configuration
readonly ROOT_DIR=$(pwd)
readonly BIN_DIR=$(pwd)/bin
readonly CF_DIR=$(pwd)/cloudformation
readonly DB_DIR=$(pwd)/database
readonly LAMBDA_LIB_DIR=$(pwd)/lambda/lib
readonly LAMBDA_FUNCTION_DIR=$(pwd)/lambda/function
readonly CLIENT_DIR=$(pwd)/client
readonly PYVENV=pyvenv
readonly TEST_DIR=$(pwd)/test

# Application and environment configuration
readonly APPLICATION=fenix-infringement
readonly ENVIRONMENT=DEV

# infirngement-ingest service configuration
readonly S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX=firehose-infringement-delivery

# infringement-transform service configuration
readonly S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME=infringement-transform-lambda-package
readonly LAMBDA_LOG_LEVEL=INFO
readonly LAMBDA_PUT_PRODUCT_IN_DB_VERSION=$(cat $LAMBDA_FUNCTION_DIR/PutProductInDbLambda/version)
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION=$(cat $LAMBDA_FUNCTION_DIR/PutInfringementInDbLambda/version)
readonly SNS_INFRINGEMENT_IMPORT_ALARM_NOTIFICATION_EMAIL=volodymyr.prokopyuk@nagra.com

# infringement-store service configuration
readonly DB_HOST=localhost
readonly DB_LOCAL_PORT=5432
readonly DB_TUNNEL_PORT=15432
readonly DB_NAME=infringement
readonly DB_SUPER_USER=super
readonly DB_SUPER_PASSWORD='Password1!'
readonly DB_INGEST_USER=ingest
readonly DB_INGEST_PASSWORD='Password1!'
readonly DB_CONNECT_TIMEOUT=30
readonly BASTION_USER=ec2-user
