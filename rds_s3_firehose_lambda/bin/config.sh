# Application and environment configuration
readonly APPLICATION=infringement
readonly ENVIRONMENT=DEV

# infirngement-intest configuration
readonly S3_FIREHOSE_INFRINGEMENT_DELIVERY_BUCKET_SUFFIX=firehose-infringement-delivery

# infringement-transform configuration
readonly S3_TRANSFORM_LAMBDA_PACKAGE_BUCKET_NAME=infringement-transform-lambda-package
readonly LAMBDA_LOG_LEVEL=DEBUG
readonly LAMBDA_DIR=$(pwd)/lambda/function
readonly LAMBDA_PUT_PRODUCT_IN_DB_VERSION=$(cat $LAMBDA_DIR/PutProductInDbLambda/version)
readonly LAMBDA_PUT_INFRINGEMENT_IN_DB_VERSION=$(cat $LAMBDA_DIR/PutInfringementInDbLambda/version)

# infringement-store configuration
readonly DB_PORT=5432
readonly DB_NAME=infringement
readonly DB_USER=vld
readonly DB_PASSWORD='Password1!'
