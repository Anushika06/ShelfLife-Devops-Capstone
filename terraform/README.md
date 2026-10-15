# terraform/ — AWS VPC + EKS

Provisions the AWS side of the capstone in `ap-south-1` (Mumbai) by default:

- VPC `10.42.0.0/16` with DNS support, an internet gateway and a public route table
- Two public subnets in two availability zones (tagged for EKS load balancers)
- IAM roles for the EKS control plane and the worker nodes
- EKS cluster `shelflife-eks` (Kubernetes 1.36, standard support, access entries, creator is admin)
- Managed node group `shelflife-nodes` (default 2 × `t3.medium`, min 1, max 3, AL2023, 20 GiB)
- Optional AWS Budgets email alert when `budget_alert_email` is set

| File | Contents |
| --- | --- |
| `versions.tf` | Terraform ≥ 1.6, AWS provider `~> 6.0`, provider config and default tags |
| `variables.tf` | All inputs with defaults and descriptions |
| `main.tf` | Network, IAM, EKS cluster, node group, optional budget |
| `outputs.tf` | VPC/subnet IDs, cluster name/endpoint, `configure_kubectl` command |
| `terraform.tfvars.example` | Copy to `terraform.tfvars` (git-ignored). Contains no credentials |
| `.terraform.lock.hcl` | Provider lock file (committed on purpose) |

Cost choices: no NAT gateway (nodes in public subnets), no control-plane logging, local state.
The EKS control plane is billed per hour while the cluster exists, so destroy it after use.

## Prerequisites

Terraform ≥ 1.6, AWS CLI v2 with credentials from `aws configure` / `aws sso login` or `AWS_*`
environment variables. Credentials are never written into these files.

## Commands

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars    # set cluster_endpoint_public_access_cidrs to your IP/32
aws sts get-caller-identity                     # confirm the account before spending money

terraform init
terraform fmt -check && terraform validate
terraform plan -out tfplan
terraform apply tfplan
aws eks update-kubeconfig --region ap-south-1 --name shelflife-eks
kubectl get nodes

# teardown (remove LoadBalancer services first if you created any)
terraform destroy
../scripts/aws-check-leftovers.sh ap-south-1     # read-only check for anything left behind
```

CI runs `terraform fmt -check`, `terraform init -backend=false` and `terraform validate` on every
push; it never needs AWS credentials.

## Evidence run (14–15 Oct 2026)

`plan` → 16 to add, `apply` → 16 added, `destroy` → 16 destroyed, leftover check clean. That run
set `node_instance_types = ["t3.small"]` in the local `terraform.tfvars`. Screenshots:
`demo/evidence/E09-*` to `E12-*`.
