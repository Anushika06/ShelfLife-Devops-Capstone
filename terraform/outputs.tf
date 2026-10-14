output "aws_region" {
  description = "Region the infrastructure was created in."
  value       = var.aws_region
}

output "vpc_id" {
  description = "ID of the VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets (one per AZ)."
  value       = aws_subnet.public[*].id
}

output "availability_zones" {
  description = "AZs used by the subnets."
  value       = local.azs
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = aws_eks_cluster.main.name
}

output "cluster_version" {
  description = "Kubernetes version of the EKS control plane."
  value       = aws_eks_cluster.main.version
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = aws_eks_cluster.main.endpoint
}

output "node_group_name" {
  description = "Managed node group name."
  value       = aws_eks_node_group.main.node_group_name
}

output "configure_kubectl" {
  description = "Command that writes the kubeconfig entry for this cluster."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.main.name}"
}
