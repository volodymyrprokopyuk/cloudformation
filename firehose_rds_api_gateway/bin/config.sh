readonly SETOPTS=-eux

set $SETOPTS

# Common configuration
readonly ROOT_DIR=$(pwd)
readonly BIN_DIR=$ROOT_DIR/bin
readonly CF_DIR=$ROOT_DIR/cloudformation
readonly DB_DIR=$ROOT_DIR/database
readonly DB_MIGRATION_DIR=$DB_DIR/migration
readonly LAMBDA_LIB_DIR=$ROOT_DIR/lambda/lib
readonly LAMBDA_TRANSFORM_DIR=$ROOT_DIR/lambda/function/transform
readonly LAMBDA_EXPOSE_DIR=$ROOT_DIR/lambda/function/expose
readonly DIRECT_IMPORT_DIR=$ROOT_DIR/direct_import
readonly FIREHOSE_IMPORT_DIR=$ROOT_DIR/firehose_import
readonly PYVENV=pyvenv
readonly TEST_DIR=$ROOT_DIR/test
readonly LAMBDA_TEST_DATA_DIR=/tmp
readonly DOC_DIR=$ROOT_DIR/doc

# Application and environment configuration
readonly APPLICATION=fenix-infringement
readonly ENVIRONMENT=DEV
readonly OWNER=volodymyr.prokopyuk@nagra.com
readonly API_VERSION=v1

# infirngement-ingest service configuration
readonly S3_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX=firehose-delivery
readonly SMART_PROTECTION_ACCOUNT_ID=243515312936
readonly SMART_PROTECTION_EXTERNAL_ID=a88f11d8-ac8a-61b7-98cf-93744baa8014

# infringement-transform service configuration
readonly LAMBDA_LOG_LEVEL=INFO
readonly S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME=$APPLICATION-transform-lambda-package
readonly LAMBDA_PUT_PRODUCT_IN_DB_VERSION=$(cat $LAMBDA_TRANSFORM_DIR/PutProductInDbLambda/version)
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION=$(cat $LAMBDA_TRANSFORM_DIR/PutInfringementInDbLambda/version)
readonly SNS_INFRINGEMENT_IMPORT_ALARM_NOTIFICATION_EMAIL=volodymyr.prokopyuk@nagra.com

# infringement-expose service configuration
readonly S3_EXPOSE_LAMBDA_PACKAGE_BUCKET_NAME=$APPLICATION-expose-lambda-package
readonly LAMBDA_GET_PARTNER_FROM_DB_VERSION=$(cat $LAMBDA_EXPOSE_DIR/GetPartnerFromDbLambda/version)
readonly LAMBDA_GET_PRODUCT_FROM_DB_VERSION=$(cat $LAMBDA_EXPOSE_DIR/GetProductFromDbLambda/version)
readonly LAMBDA_GET_PIRATE_SOURCE_FROM_DB_VERSION=$(cat $LAMBDA_EXPOSE_DIR/GetPirateSourceFromDbLambda/version)
readonly LAMBDA_GET_INFRINGEMENT_FROM_DB_VERSION=$(cat $LAMBDA_EXPOSE_DIR/GetInfringementFromDbLambda/version)
readonly LAMBDA_POST_INFRINGEMENT_IN_DB_VERSION=$(cat $LAMBDA_EXPOSE_DIR/PostInfringementInDbLambda/version)

# infringement-store service configuration
readonly DB_HOST=localhost
readonly DB_LOCAL_PORT=5432
readonly DB_TUNNEL_PORT=15432
readonly DB_NAME=infringement
readonly DB_SUPER_USER=super
readonly DB_SUPER_PASSWORD='Password1!'
readonly DB_INGEST_USER=ingest
readonly DB_INGEST_PASSWORD='Password1!'
readonly DB_EXPOSE_USER=expose
readonly DB_EXPOSE_PASSWORD='Password1!'
readonly DB_CONNECT_TIMEOUT=30
readonly BASTION_USER=ec2-user
