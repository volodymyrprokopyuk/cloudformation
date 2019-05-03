# AMI lifecycle

```bash
# Validate the CloudFormation template before creating a Stack
./bin/validate.sh
# Create a Stack and configure an EC2 instance for an AMI to be built from
aws cloudformation create-stack --stack-name vlad-stack \
    --template-body file://$(pwd)/ami.yaml \
    --parameters ParameterKey=UserData,ParameterValue=$(base64 -w0 ec2-user-data.sh)
# Stop the EC2 instance before creating an AMI
aws ec2 stop-instances --instance-ids i-0c8dc6f147043a842
# Create an AMI (with EBS snapshot) from the stopped EC2 instace
aws ec2 create-image --instance-id i-0c8dc6f147043a842 --name="NGINX" \
   --description="Amazon Linux 2 AMI 2.0 with NGINX x86_64 Minimal HVM ebs"
# Delete the Stack that has been created for AMI built
aws cloudformation delete-stack --stack-name vlad-stack
# Create a new Stack using the new AMI and commenting EC2 UserData
# as the EC2 consiguraiton will be already in the AMI
aws cloudformation create-stack --stack-name vlad-stack \
    --template-body file://$(pwd)/ami.yaml
    --parameters ParameterKey=ImageId,ParameterValue=ami-0ec810b7209043b39
# Delete the Stack that has been created for AMI test
aws cloudformation delete-stack --stack-name vlad-stack
# Deregister the AMI
aws ec2 deregister-image --image-id ami-0ec810b7209043b39
# Delete EBS snapshot used by the AMI
aws ec2 delete-snapshot --snapshot-id snap-0350c36ea137a2ec9

# EC2 filter by tag
aws ec2 describe-instances --instance-ids i-0c8dc6f147043a842
aws ec2 describe-instances --filters Name=tag:Name,Values=vlad-stack-Ec2ForAmi
# AMI filter by description
aws ec2 describe-images --image-ids ami-0eaec5838478eb0ba
aws ec2 describe-images --filters \
    Name=description,Values="Amazon Linux 2 AMI 2.0.201903* x86_64 Minimal HVM ebs"
# EBS filter by description
aws ec2 describe-snapshots --snapshot-ids snap-0350c36ea137a2ec9
aws ec2 describe-snapshots --filters \
    Name=description,Values="Created by CreateImage* for ami-0ec810b7209043b39*"
```
