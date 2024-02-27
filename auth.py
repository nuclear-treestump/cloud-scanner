"""
Handles auth for boto3, and where needed, SSM requests.
"""

import botocore
import boto3
import os
from .decorator import auto_log as autolog


@autolog(__name__)
def get_boto3_session():
    """
    Get boto3 session through credentials stored in env variables.
    This would be better served by keychain or a credential store on the machine.

    Returns:
        Boto3 Session object
    """
    try:
        session = boto3.Session(
            aws_access_key_id=(os.getenv("AMZN_ACCESS_KEY")),
            aws_secret_access_key=(os.getenv("AMZN_SECRET_KEY")),
            region_name=(os.getenv("AMZN_REGION", "us-east-1")),
        )
    except botocore.exceptions.ClientError as client_error:
        print(client_error)
    return session
