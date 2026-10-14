# Terraform and AWS provider versions, plus the provider configuration.
# (As in the course's session-19 labs, there is no separate provider.tf.)
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  # Credentials are NOT configured here. Terraform uses the standard AWS chain:
  # `aws configure` / `aws sso login` profile, or AWS_* environment variables.
  default_tags {
    tags = merge(
      {
        Project   = var.project_name
        ManagedBy = "Terraform"
        Purpose   = "devops-capstone"
      },
      var.extra_tags,
    )
  }
}
