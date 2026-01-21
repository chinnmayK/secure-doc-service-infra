variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name for tagging"
  type        = string
  default     = "secure-doc-service"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}
