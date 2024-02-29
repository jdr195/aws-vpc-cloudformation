# aws-vpc--troposphere
Uses [Troposphere](https://troposphere.readthedocs.io/en/latest/) to reimplement the cloudformation template at [https://docs.aws.amazon.com/codebuild/latest/userguide/cloudformation-vpc-template.html](https://docs.aws.amazon.com/codebuild/latest/userguide/cloudformation-vpc-template.html)

It creates an AWS VPC with an Internet Gateway, 2 public subnets, 2 private subnets, 2 NAT Gateways, and the supporting Routes and Associations.

### Example Usage
```
pip install -r requirements.txt
python vpc.py
aws cloudformation deploy --stack-name vpc-troposphere --region us-east-1 --template template.yml
```
