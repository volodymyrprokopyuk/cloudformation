#!/usr/bin/env bash

set -eu

DISTRIBUTION_ROOT=/opt
DISTRIBUTION_REPO=https://github.com/volodymyrprokopyuk/cloudformation.git
DISTRIBUTION_DIR=$DISTRIBUTION_ROOT/cloudformation/cloudwatch
LOG_FILE=cloudwatch-logging.log

sudo su

# Install Python 3
yum install python3 git -y

# Install CloudWatch logging
mkdir -p $DISTRIBUTION_ROOT
cd $DISTRIBUTION_ROOT
git clone $DISTRIBUTION_REPO

cd $DISTRIBUTION_DIR
python3 -m venv pyvenv
source pyvenv/bin/activate
pip3 install -r requirements.txt

# Execute CloudWatch logging
python3 main.py > $LOG_FILE
