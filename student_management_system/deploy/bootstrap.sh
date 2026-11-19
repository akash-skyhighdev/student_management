#!/bin/bash
# Runs once on each new EC2 instance (called from the launch template's user data).
# Expects these variables: AWS_REGION S3_BUCKET DB_HOST DB_NAME DB_SECRET_ARN SNS_TOPIC_ARN
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"

python3 -m venv venv
venv/bin/pip install --quiet -r requirements.txt gunicorn

# The database password never appears in the template: it is read from Secrets Manager.
SECRET_JSON="$(aws secretsmanager get-secret-value --region "$AWS_REGION" \
  --secret-id "$DB_SECRET_ARN" --query SecretString --output text)"
export SECRET_JSON
venv/bin/python deploy/write_env.py
unset SECRET_JSON

chown -R ec2-user:ec2-user "$APP_DIR"
chmod 600 .env

# Create the tables. Retry once in case a second instance is doing the same at the same moment.
sudo -u ec2-user venv/bin/flask --app app init-db || { sleep 20; sudo -u ec2-user venv/bin/flask --app app init-db; }

sed "s#__APP_DIR__#$APP_DIR#g" deploy/student.service > /etc/systemd/system/student.service
systemctl daemon-reload
systemctl enable --now student
