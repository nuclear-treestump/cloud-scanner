import json
import boto3
import os
from . import database_ops as db

main_json = json.load(open("fake_aws_resources_with_ips.json"))

ec2_instances = main_json["EC2Instances"]
s3_buckets = main_json["S3Buckets"]
rds_instances = main_json["RDSInstances"]

with open("ec2_instances.json", "w") as outfile0:
    outfile0.write(json.dumps(ec2_instances, indent=4))

with open("s3_buckets.json", "w") as outfile1:
    outfile1.write(json.dumps(s3_buckets, indent=4))

with open("rds_instances.json", "w") as outfile2:
    outfile2.write(json.dumps(rds_instances, indent=4))

db.setup_database()
