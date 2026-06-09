#!/usr/bin/env bash
# setup.sh — create namespace, DB, secret, and deploy history-explorer
# Run once from the project root: bash k8s/setup.sh
set -euo pipefail

NAMESPACE="history-explorer"
DB_NAME="history-explorer"
SECRET_NAME="history-explorer"
PG_HOST="postgresql-rw.postgresql.svc.cluster.local"

echo "==> Pulling DB credentials from unscripted-living secret..."
DB_USER=$(kubectl get secret unscripted-living -n unscripted-living \
  -o jsonpath='{.data.username}' | base64 -d)
DB_PASS=$(kubectl get secret unscripted-living -n unscripted-living \
  -o jsonpath='{.data.password}' | base64 -d)

echo "==> Generating Django secret key..."
DJANGO_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

echo "==> Creating namespace ${NAMESPACE}..."
kubectl apply -f k8s/deployment.yaml --dry-run=client -o yaml \
  | kubectl apply -f - 2>/dev/null || true
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

echo "==> Creating PostgreSQL database '${DB_NAME}'..."
kubectl run -i --rm --restart=Never pg-setup-"$(date +%s)" \
  --image=postgres:15 \
  --namespace=default \
  --env="PGPASSWORD=${DB_PASS}" \
  --command -- psql \
    -h "$PG_HOST" \
    -U "$DB_USER" \
    -c "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" \
  | grep -q 1 \
  && echo "   database already exists, skipping create" \
  || kubectl run -i --rm --restart=Never pg-createdb-"$(date +%s)" \
       --image=postgres:15 \
       --namespace=default \
       --env="PGPASSWORD=${DB_PASS}" \
       --command -- psql \
         -h "$PG_HOST" \
         -U "$DB_USER" \
         -c "CREATE DATABASE \"${DB_NAME}\" OWNER \"${DB_USER}\";"

echo "==> Creating k8s secret '${SECRET_NAME}' in namespace ${NAMESPACE}..."
kubectl create secret generic "$SECRET_NAME" \
  --namespace="$NAMESPACE" \
  --from-literal=secret_key="$DJANGO_SECRET" \
  --from-literal=username="$DB_USER" \
  --from-literal=password="$DB_PASS" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "==> Applying deployment..."
kubectl apply -f k8s/deployment.yaml

echo ""
echo "==> Done. Waiting for rollout..."
kubectl rollout status deployment/history-explorer -n "$NAMESPACE" --timeout=120s

echo ""
echo "==> Pod status:"
kubectl get pods -n "$NAMESPACE"
echo ""
echo "App will be available at: https://history-explorer.jaycurtis.org"
