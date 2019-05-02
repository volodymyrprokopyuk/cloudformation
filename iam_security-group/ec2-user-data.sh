#!/usr/bin/env bash

set -eu

DISTIBUTION_DIR=/opt/ec2-metadata-to-s3

sudo su

# Install Python 3
yum install python3 -y

# Install EC2 metadata to S3 script
mkdir -p $DISTIBUTION_DIR

cat > $DISTIBUTION_DIR/main.py << EOF
{{MAIN.PY}}
EOF

cat > $DISTIBUTION_DIR/requirements.txt << EOF
{{REQUIREMENTS.TXT}}
EOF

cd $DISTIBUTION_DIR
python3 -m venv pyvenv
source pyvenv/bin/activate
pip3 install -r requirements.txt

# Execute EC2 metadata to S3 script
python3 main.py
