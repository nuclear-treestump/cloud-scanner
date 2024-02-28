import json
import boto3
import os
import database_ops as db


def breakdown_json(json_file):
    ec2_instances = json_file.get("EC2Instances", [])
    s3_buckets = json_file.get("S3Buckets", [])
    rds_instances = json_file.get("RDSInstances", [])
    return ec2_instances, s3_buckets, rds_instances


def main():
    db.setup_database()
    ec2_instances, s3_buckets, rds_instances = breakdown_json(
        json.load(open("cloud_scanner/fake_aws_resources_with_ips.json"))
    )
    db.batch_insert_ec2(data=ec2_instances)
    db.batch_insert_s3(data=s3_buckets)
    db.batch_insert_rds(data=rds_instances)
