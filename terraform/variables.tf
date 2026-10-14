variable "aws_region" {
  description = "AWS region for the VPC and EKS cluster."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix used in resource names and the Project tag."
  type        = string
  default     = "shelflife"
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "shelflife-eks"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version. Must be in EKS STANDARD support (extended support costs $0.60/h instead of $0.10/h). Check with: aws eks describe-cluster-versions"
  type        = string
  default     = "1.36"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "One public subnet per availability zone (the rubric requires at least two)."
  type        = list(string)
  default     = ["10.42.0.0/20", "10.42.16.0/20"]

  validation {
    condition     = length(var.public_subnet_cidrs) >= 2
    error_message = "At least two public subnets are required (EKS needs subnets in two AZs)."
  }
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDRs allowed to reach the public EKS API endpoint. Narrow this to your own IP (x.x.x.x/32) for the demo."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "node_instance_types" {
  description = "EC2 instance types for the managed node group."
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_capacity_type" {
  description = "ON_DEMAND (predictable) or SPOT (cheaper, can be interrupted)."
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition     = contains(["ON_DEMAND", "SPOT"], var.node_capacity_type)
    error_message = "node_capacity_type must be ON_DEMAND or SPOT."
  }
}

variable "node_desired_size" {
  description = "Number of worker nodes to run."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum worker nodes."
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum worker nodes."
  type        = number
  default     = 3
}

variable "node_disk_size_gb" {
  description = "Root EBS volume size per worker node (GiB)."
  type        = number
  default     = 20
}

variable "budget_alert_email" {
  description = "If set, creates an AWS Budgets monthly cost budget that emails this address. Leave empty to skip."
  type        = string
  default     = ""
}

variable "budget_limit_usd" {
  description = "Monthly budget amount in USD for the optional budget alert."
  type        = number
  default     = 25
}

variable "extra_tags" {
  description = "Additional tags for every resource (e.g. Owner)."
  type        = map(string)
  default     = {}
}
