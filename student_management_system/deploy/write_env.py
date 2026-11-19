"""Writes .env on a new server from the values the CloudFormation stack passes in.
Called by deploy/bootstrap.sh. Nothing secret is stored in the template or the user data."""
import json
import os
import secrets


def quote(value):
    # single-quoted for python-dotenv, escaping backslash and quote
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


db = json.loads(os.environ["SECRET_JSON"])  # {"username": ..., "password": ...} from Secrets Manager
values = {
    "SECRET_KEY": secrets.token_hex(32),
    "DB_HOST": os.environ["DB_HOST"],
    "DB_PORT": "3306",
    "DB_USER": db["username"],
    "DB_PASSWORD": db["password"],
    "DB_NAME": os.environ["DB_NAME"],
    "S3_BUCKET": os.environ["S3_BUCKET"],
    "AWS_REGION": os.environ["AWS_REGION"],
    "AWS_ACCESS_KEY_ID": "",       # blank: the instance's IAM role is used
    "AWS_SECRET_ACCESS_KEY": "",
    "SNS_TOPIC_ARN": os.environ["SNS_TOPIC_ARN"],
    "REQUIRE_EMAIL_CONFIRMATION": "true",
    "PROXY_DOCUMENTS": "true",     # the bucket is reachable only through the VPC endpoint
    "ALLOW_SELF_REGISTRATION": "true",
}
with open(os.path.join(os.path.dirname(__file__), "..", ".env"), "w") as f:
    for key, value in values.items():
        f.write(f"{key}={quote(value)}\n")
