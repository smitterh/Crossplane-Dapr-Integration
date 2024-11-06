#!/usr/bin/env bash
set -aeuo pipefail

docker build --platform=linux/amd64 -t dapr/policyvalidator:$1 .
docker tag dapr/policyvalidator:$1 <AWS ECR IMAGE URL>:$1

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <AWS ACCOUNT ECR URL>
docker push  <AWS ECR IMAGE URL>:$1