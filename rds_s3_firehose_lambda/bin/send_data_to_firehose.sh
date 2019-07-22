#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly CLIENT_DIR=$(pwd)/client
readonly CLIENT_SCRIPT=$CLIENT_DIR/main.py
readonly CLIENT_DATA=$CLIENT_DIR/data

cd $CLIENT_DIR

setup_virtual_environment $PYVENV

readonly STACK_NAME=$APPLICATION-ingest-$ENVIRONMENT

# Get Kinesis Firehose product delivery stream name
readonly PRODUCT_DELIVERY_STREAM_EXPORT_NAME=$STACK_NAME:ProductDeliveryStreamName
export PRODUCT_DELIVERY_STREAM_NAME=$(
    get_cf_export_value $PRODUCT_DELIVERY_STREAM_EXPORT_NAME
)

# Get Kinesis Firehose infringement delivery stream name
readonly INFRINGEMENT_DELIVERY_STREAM_EXPORT_NAME=$STACK_NAME:InfringementDeliveryStreamName
export INFRINGEMENT_DELIVERY_STREAM_NAME=$(
    get_cf_export_value $INFRINGEMENT_DELIVERY_STREAM_EXPORT_NAME
)

# Send product data to the corresponding Kinesis Firehose delivery stream
for data_file in $CLIENT_DATA/product*.txt; do
    python $CLIENT_SCRIPT -p $data_file
done

sleep 5

# Send infringement data to the corresponding Kinesis Firehose delivery stream
for data_file in $CLIENT_DATA/infringement*.txt; do
    python $CLIENT_SCRIPT -i $data_file
done
