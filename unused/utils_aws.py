import boto3
from .auth import get_boto3_session
from typing import Optional, Callable, List, Tuple, Any


def get_ec2_instances(boto_session: boto3.Session) -> dict:
    """
    Get EC2 instances
    """
    ec2 = boto_session.client("ec2")
    ec2_instances = ec2.describe_instances()
