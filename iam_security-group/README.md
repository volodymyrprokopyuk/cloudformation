# IAM Users, User Groups, Roles and Security Groups

```bash
# Validate the CloudFormation template before creating a Stack
./bin/validate.sh
# Create a Stack
./bin/deploy.sh
# Get automatically generated by AWS IAM Role access credentials
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/<RoleName>
# Get EC2 instance UserData
curl http://169.254.169.254/latest/user-data
# Get EC2 instance UserData log
cat /var/log/cloud-init-output.log
# Delete first the S3 Bucket objects to be able to delete the S3 Bucket itself as part of the Stack deletion
aws s3 rm s3://vlad-stack-ec2-metadata/ec2 --recursive
# Delete the Stack
aws cloudformation delete-stack --stack-name vlad-stack
```