import json
import boto3
import os
import database_ops as db


def main():
    db.setup_database()
    main_json = json.load(open("cloud_scanner/fake_aws_resources_with_ips.json"))
    ec2_instances = main_json["EC2Instances"]
    s3_buckets = main_json["S3Buckets"]
    rds_instances = main_json["RDSInstances"]
    db.batch_insert_ec2(data=ec2_instances)
    db.batch_insert_s3(data=s3_buckets)
    db.batch_insert_rds(data=rds_instances)


main()
