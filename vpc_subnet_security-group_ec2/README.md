# VPC, Subnet, SecurityGroups, EC2

```bash
# Validate the CloudFormation template before creating a Stack
./bin/validate.sh
# Create a CloudFormation Stack
./bin/deploy.sh
# SSH into public EC2 and from there SSH into private EC2
eval $(ssh-agent)
ssh-add ~/.ssh/id_rsa
ssh -A ec2-user@<PublicEc2Ip>
ssh ec2-user@<PrivateEc2Ip>
# Delete the CloudFormation Stack
aws cloudformation delete-stack --stack-name vlad-stack
```
