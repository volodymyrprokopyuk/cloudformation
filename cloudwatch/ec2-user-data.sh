#!/usr/bin/env bash

set -eu

CLOUDWATCH_AGENT_URL=https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
CLOUDWATCH_AGENT_PACKAGE=${CLOUDWATCH_AGENT_URL##*/}
CLOUDWATCH_AGENT_PATH=/opt/aws/amazon-cloudwatch-agent
CLOUDWATCH_AGENT_CONFIG_PATH=$CLOUDWATCH_AGENT_PATH/etc/amazon-cloudwatch-agent.json
CLOUDWATCH_AGENT_CONFIG_FILE=${CLOUDWATCH_AGENT_CONFIG_PATH##*/}

APP_REPO=https://github.com/volodymyrprokopyuk/cloudformation.git
APP_ROOT=/opt
APP_DIR=$APP_ROOT/cloudformation/cloudwatch
APP_LOG_PATH=$APP_DIR/cloudwatch-logging.log

sudo su

# Install Python 3
yum update -y
yum install -y python3 git

# Install unified CloudWatch agent
curl -O $CLOUDWATCH_AGENT_URL
rpm -U ./$CLOUDWATCH_AGENT_PACKAGE
cp $APP_DIR/$CLOUDWATCH_AGENT_CONFIG_FILE $CLOUDWATCH_AGENT_CONFIG_PATH
$CLOUDWATCH_AGENT_PATH/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 \
    -c file:$CLOUDWATCH_AGENT_CONFIG_PATH -s

# Install CloudWatch logging application
mkdir -p $APP_ROOT
cd $APP_ROOT
git clone $APP_REPO

cd $APP_DIR
python3 -m venv pyvenv
source pyvenv/bin/activate
pip3 install -r requirements.txt

# Execute CloudWatch logging application
python3 main.py > $APP_LOG_PATH 2>&1
