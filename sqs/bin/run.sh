#!/usr/bin/env bash

set -eu

# SQS SendMessage
python sqs/producer.py
sleep 2s
# SQS ReceiveMessage and DeleteMessage
python sqs/consumer.py
