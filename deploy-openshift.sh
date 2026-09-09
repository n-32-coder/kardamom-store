#!/bin/bash
# Deploy KARDAMOM to OpenShift (Developer Sandbox or any cluster).
# 1. Log in first:  oc login --token=... --server=https://...
# 2. Run:           bash deploy-openshift.sh
set -euo pipefail

PROJECT="${PROJECT:-kardamom}"
IMAGE="${IMAGE:-ghcr.io/n-32-coder/kardamom:latest}"

echo "==> project"
oc new-project "$PROJECT" 2>/dev/null || oc project "$PROJECT"

echo "==> secrets (edit k8s/10-secret.yaml with real values first)"
oc apply -f k8s/10-secret.yaml

echo "==> storage + RBAC"
oc apply -f k8s/20-pvc.yaml
oc apply -f k8s/70-rbac.yaml

echo "==> workload (image: $IMAGE)"
sed "s|ghcr.io/STUDENT/kardamom:latest|$IMAGE|" k8s/30-deployment.yaml | oc apply -f -
oc apply -f k8s/40-service.yaml
oc apply -f k8s/55-route.yaml
oc apply -f k8s/60-hpa.yaml
oc apply -f k8s/80-networkpolicy.yaml

echo "==> waiting for rollout"
oc rollout status deployment/kardamom -n "$PROJECT" --timeout=300s

echo "==> live URL"
oc get route kardamom -n "$PROJECT" -o jsonpath='https://{.spec.host}{"\n"}'
