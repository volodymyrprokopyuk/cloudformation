#!/usr/bin/env bash

set -eu

# SQS SendMessage
python producer.py
sleep 2s
# SQS ReceiveMessage and DeleteMessage
python consumer.py
