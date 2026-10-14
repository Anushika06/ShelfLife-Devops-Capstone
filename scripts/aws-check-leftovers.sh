#!/usr/bin/env bash
# Read-only check for billable leftovers after `terraform destroy`.
# Lists anything in the region that this project could have created, directly
# (Terraform) or indirectly (Kubernetes LoadBalancer Services, EBS volumes).
# Usage: scripts/aws-check-leftovers.sh [region]      default: ap-south-1
set -uo pipefail

REGION="${1:-ap-south-1}"
PROJECT_TAG="shelflife"
found=0

check() {
  local label="$1"; shift
  local out
  out="$("$@" 2>&1)"
  if [ -n "$out" ] && [ "$out" != "None" ]; then
    echo "LEFTOVER  $label:"
    echo "$out" | sed 's/^/    /'
    found=1
  else
    echo "ok        $label: none"
  fi
}

echo "Checking region $REGION ..."
check "EKS clusters" aws eks list-clusters --region "$REGION" --query 'clusters[]' --output text
check "VPCs tagged Project=$PROJECT_TAG" aws ec2 describe-vpcs --region "$REGION" \
  --filters "Name=tag:Project,Values=$PROJECT_TAG" --query 'Vpcs[].VpcId' --output text
check "running/stopped EC2 instances tagged by EKS" aws ec2 describe-instances --region "$REGION" \
  --filters "Name=tag-key,Values=eks:cluster-name" "Name=instance-state-name,Values=pending,running,stopping,stopped" \
  --query 'Reservations[].Instances[].InstanceId' --output text
check "Classic load balancers" aws elb describe-load-balancers --region "$REGION" \
  --query 'LoadBalancerDescriptions[].LoadBalancerName' --output text
check "ALB/NLB load balancers" aws elbv2 describe-load-balancers --region "$REGION" \
  --query 'LoadBalancers[].LoadBalancerName' --output text
check "unattached EBS volumes" aws ec2 describe-volumes --region "$REGION" \
  --filters "Name=status,Values=available" --query 'Volumes[].VolumeId' --output text
check "Elastic IPs" aws ec2 describe-addresses --region "$REGION" --query 'Addresses[].PublicIp' --output text
check "NAT gateways (not created by this project)" aws ec2 describe-nat-gateways --region "$REGION" \
  --filter "Name=state,Values=pending,available" --query 'NatGateways[].NatGatewayId' --output text

echo
if [ "$found" -eq 0 ]; then
  echo "No leftovers found in $REGION. Also check Billing > Bills the next day."
else
  echo "Leftovers found. Delete them (or re-run terraform destroy) before you stop paying attention."
  exit 1
fi
