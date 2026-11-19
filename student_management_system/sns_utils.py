import boto3
from botocore.config import Config as BotoConfig
from flask import current_app


def _client():
    cfg = current_app.config
    kwargs = {"region_name": cfg["AWS_REGION"], "config": BotoConfig(signature_version="v4")}
    # With an IAM role (EC2) leave the keys blank and boto3 finds the role itself.
    if cfg["AWS_ACCESS_KEY_ID"] and cfg["AWS_SECRET_ACCESS_KEY"]:
        kwargs["aws_access_key_id"] = cfg["AWS_ACCESS_KEY_ID"]
        kwargs["aws_secret_access_key"] = cfg["AWS_SECRET_ACCESS_KEY"]
    return boto3.client("sns", **kwargs)


def subscribe_email(email):
    """Ask SNS to send the "Confirm subscription" mail. Returns the subscription ARN
    (it reads "pending confirmation" until the student clicks the link)."""
    resp = _client().subscribe(
        TopicArn=current_app.config["SNS_TOPIC_ARN"],
        Protocol="email",
        Endpoint=email,
        ReturnSubscriptionArn=True,
    )
    return resp["SubscriptionArn"]


def is_confirmed(subscription_arn):
    """True once the student has clicked the confirmation link in the email."""
    attrs = _client().get_subscription_attributes(SubscriptionArn=subscription_arn)["Attributes"]
    return attrs.get("PendingConfirmation") == "false"


def unsubscribe(subscription_arn):
    _client().unsubscribe(SubscriptionArn=subscription_arn)
