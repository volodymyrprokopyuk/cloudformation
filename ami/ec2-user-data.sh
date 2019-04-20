#!/usr/bin/env bash

set -eu

sudo su

# Install NGINX
amazon-linux-extras install nginx1.12 -y

# Configure NGINX
# NGINX configuration
cat > /etc/nginx/conf.d/default.conf << EOF
server {
    listen       80;
    listen       [::]:80;
    server_name  *.compute.amazonaws.com;

    location / {
        root /usr/share/nginx/html;
        index ami-index.html;
    }
}
EOF

# NGINX index
cat > /usr/share/nginx/html/ami-index.html << EOF
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8">
        <title>NGINX from AMI</title>
    </head>
    <body>
        <h1>NGINX from AMI</h1>
    </body>
</html>
EOF

# Enable NGINX
chkconfig nginx on

# Start NGINX
service nginx start
