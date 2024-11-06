#!/usr/bin/env bash
set -aeuo pipefail

echo "Docker Build"
docker build --quiet --platform=linux/amd64 --tag <FUNCTION NAME>:$1 .

echo "Log in to AWS"
aws ecr get-login-password --region <AWS REGION> | docker login --username AWS --password-stdin <AWS ECR REGISTRY URL >

echo "Crossplane xpg build"
crossplane xpkg build \
    --package-root=package \
    --embed-runtime-image=<FUNCTION NAME>:$1 \
    --package-file=<FUNCTION NAME>.xpkg
    
crossplane xpkg push \
  --package-files=<FUNCTION NAME>.xpkg \
   <AWS ECR REGISTRY URL >:$1
echo "Crossplane xpg push completed"
