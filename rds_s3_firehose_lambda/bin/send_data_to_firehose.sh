#!/usr/bin/env bash

set -eux

source ./bin/config.sh
source ./bin/util.sh

# Get Kinesis Firehose product delivery stream name
readonly FIREHOSE_PRODUCT_DELIVERY_STREAM_EXPORT_NAME=$APPLICATION-ingest-$ENVIRONMENT:ProductDeliveryStreamName
export FIREHOSE_PRODUCT_DELIVERY_STREAM_NAME=$(
    get_cf_export_value $FIREHOSE_PRODUCT_DELIVERY_STREAM_EXPORT_NAME
)

# Get Kinesis Firehose infringement delivery stream name
readonly FIREHOSE_INFRINGEMENT_DELIVERY_STREAM_EXPORT_NAME=$APPLICATION-ingest-$ENVIRONMENT:InfringementDeliveryStreamName
export FIREHOSE_INFRINGEMENT_DELIVERY_STREAM_NAME=$(
    get_cf_export_value $FIREHOSE_INFRINGEMENT_DELIVERY_STREAM_EXPORT_NAME
)

readonly CLIENT_DIR=$(pwd)/client
readonly CLIENT_SCRIPT=$CLIENT_DIR/main.py
readonly CLIENT_DATA=$CLIENT_DIR/data

# Send product data to the corresponding Kinesis Firehose delivery stream
python $CLIENT_SCRIPT -p $CLIENT_DATA/product.txt
sleep 5
# Send infringement data to the corresponding Kinesis Firehose delivery stream
python $CLIENT_SCRIPT -i $CLIENT_DATA/infringement.txt
