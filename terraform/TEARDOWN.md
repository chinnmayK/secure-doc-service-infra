# Infrastructure Teardown Guide

## Safe Destruction Order (Handled by Terraform)
- Auto Scaling Group
- EC2 instances
- Launch Templates
- Load Balancer
- Security Groups
- Route Tables
- Subnets
- VPC

## Manual Verification Required
- NAT Gateway (billing-critical)
- Elastic IP
- VPC Interface Endpoints
- DynamoDB Table (data decision)

## Destroy Command
terraform destroy

## Notes
- NAT Gateway and EIP are the highest cost resources
- VPC endpoints reduce NAT cost but must be destroyed
- Logs are instance-local and removed automatically
