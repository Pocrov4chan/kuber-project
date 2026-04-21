#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT=/tmp/sealed-secrets-pub.pem
IN="$REPO_ROOT/unsealed"
OUT="$REPO_ROOT/sealed-secrets"

echo "==> Waiting for sealed-secrets-controller..."
kubectl wait -n kube-system --for=condition=available \
  deployment/sealed-secrets-controller --timeout=300s

echo "==> Fetching controller public key..."
kubeseal --fetch-cert \
  --controller-name=sealed-secrets-controller \
  --controller-namespace=kube-system \
  > "$CERT"

echo "==> Re-sealing secrets..."
kubeseal --cert "$CERT" -o yaml < "$IN/keycloak.yaml"           > "$OUT/sealed-keycloak.yaml"
kubeseal --cert "$CERT" -o yaml < "$IN/post.yaml"               > "$OUT/sealed-postgres.yaml"
kubeseal --cert "$CERT" -o yaml < "$IN/minio-creds.yaml"        > "$OUT/sealed-minio-creds.yaml"
kubeseal --cert "$CERT" -o yaml < "$IN/minio-backup-secret.yaml" > "$OUT/sealed-minio-backup.yaml"
kubeseal --cert "$CERT" -o yaml < "$IN/grafana-admin.yaml"      > "$OUT/sealed-grafana-admin.yaml"

echo "==> Verifying all outputs contain encryptedData..."
missing=$(grep -L "encryptedData" "$OUT"/*.yaml || true)
if [ -n "$missing" ]; then
  echo "ERROR: plaintext detected in:"
  echo "$missing"
  exit 1
fi

echo "==> Done. Files ready in $OUT"
echo "Next: git add sealed-secrets/ && git commit -m 're-seal for new cluster' && git push"