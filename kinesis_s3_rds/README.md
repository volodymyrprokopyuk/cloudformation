# VPC, Subnet, SecurityGroups, EC2

```bash
# Validate the CloudFormation template before creating a Stack
./bin/validate.sh
# Create a CloudFormation Stack
./bin/deploy.sh
# Create database schema
./bin/create_schema.sh
# Delete the CloudFormation Stack
aws cloudformation delete-stack --stack-name vlad-stack
```
