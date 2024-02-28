import json
import boto3
import sys
import os
import argparse
import database_ops as db
from app import app


def breakdown_json(json_file):
    ec2_instances = json_file.get("EC2Instances", [])
    s3_buckets = json_file.get("S3Buckets", [])
    rds_instances = json_file.get("RDSInstances", [])
    return ec2_instances, s3_buckets, rds_instances


def load_json_input(source=None):
    if source:
        with open(source, "r") as file:
            return json.load(file)
    elif not sys.stdin.isatty():
        return json.load(sys.stdin)
    else:
        raise ValueError(
            "No input provided. Please provide JSON via stdin or specify a file path."
        )


def main():
    """
    Main function that starts the party.

    Starts the db up

    Checks if arguments are attached to command invocation, redirecting
    to load_json_input to control initial data load.

    Then breaks down the json into the 3 types (S3Buckets, EC2Instances, RDSInstances)
    and sends them to the DB.

    Then starts the flask server to access the contents
    """
    parser = argparse.ArgumentParser(
        description="Load cloud resource data from JSON into the database."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path to the JSON file containing the cloud resource data.",
    )
    parser.add_argument(
        "--serve", "-s", action="store_true", help="Start the Flask server on port 5000"
    )
    args = parser.parse_args()

    db.setup_database()

    try:
        json_input = load_json_input(args.file)
    except ValueError as e:
        print(e)
        sys.exit(1)

    ec2_instances, s3_buckets, rds_instances = breakdown_json(json_input)
    db.batch_insert_ec2(data=ec2_instances)
    db.batch_insert_s3(data=s3_buckets)
    db.batch_insert_rds(data=rds_instances)

    if args.serve:
        app.run()
