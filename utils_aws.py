import boto3
from .auth import get_boto3_session
from typing import Optional, Callable, List, Tuple, Any


def get_ec2_instances(session: boto3.Session):
    ec2 = session.client("ec2")
