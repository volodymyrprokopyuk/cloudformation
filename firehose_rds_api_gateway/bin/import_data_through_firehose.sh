#!/usr/bin/env bash

source ./bin/config.sh
source ./bin/util.sh

set $SETOPTS

readonly USAGE="Usage: ./bin/import_data_through_firehose.sh
    {--product <product file> | --infringement <infringement file>}"

readonly FIREHOSE_IMPORT_SCRIPT=$FIREHOSE_IMPORT_DIR/main.py

if (( $# < 2 )); then
    echo $USAGE >&2
    exit 1
fi

function read_options {
    while (( $# )); do
        case $1 in
            --product)
                PRODUCT_FILE=$2
                shift
                shift
                ;;
            --infringement)
                INFRINGEMENT_FILE=$2
                shift
                shift
                ;;
            *)
                echo "Unknown parameter $1"
                shift
                exit 1
                ;;
        esac
    done
}

cd $FIREHOSE_IMPORT_DIR
setup_virtual_environment $PYVENV

read_options "$@"

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

set +u
# Send product data to the corresponding Kinesis Firehose delivery stream
if [[ -n $PRODUCT_FILE ]]; then
    python $FIREHOSE_IMPORT_SCRIPT --product $PRODUCT_FILE
fi

# Send infringement data to the corresponding Kinesis Firehose delivery stream
if [[ -n $INFRINGEMENT_FILE ]]; then
    sleep 80
    python $FIREHOSE_IMPORT_SCRIPT --infringement $INFRINGEMENT_FILE
fi
set -u
