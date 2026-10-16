#!/bin/bash
set -euxo pipefail
exec > /var/log/oiab-dvapp-bootstrap.log 2>&1
dnf install -y docker awscli
systemctl enable --now docker
# Resolve the shared Mongo (dvinyl-db) private IP by TAG at boot - no hardcoded IP.
REGION=us-east-1
DB_IP=""
for try in $(seq 1 30); do
  DB_IP=$(aws ec2 describe-instances --region $REGION \
    --filters "Name=tag:Role,Values=dvinyl-db" "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].PrivateIpAddress' --output text 2>/dev/null)
  [ -n "$DB_IP" ] && [ "$DB_IP" != "None" ] && break
  sleep 5
done
echo "resolved dvinyl-db IP by tag: $DB_IP"
docker run -d --name dvinyl_app --restart unless-stopped -p 3099:3099 \
  -e MONGODB_URL="mongodb://${DB_IP}:27017/dvinyl" \
  -e PROD=true -e VINYL_PORT=3099 \
  -e PASSJWT=demo-jwt-not-secret -e SESSION_SECRET=demo-session-not-secret \
  ghcr.io/kyonew/dvinyl:latest
touch /var/log/oiab-dvapp-DONE
