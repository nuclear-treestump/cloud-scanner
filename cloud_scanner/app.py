"""
app.py 

The purpose of this Flask app is to add a simple API to access the results on
demand.

It offers two main features: uploading JSON files
to assess resources and fetching evaluation results based on security criteria.

Key Features:
Upload Endpoint (/upload): POST a JSON file to insert cloud resource data into
the database. The file should include EC2Instances, S3Buckets, and RDSInstances.

Assessment Endpoint (/api/resources): POST a request to get security risk scores
for specified resources (ec2, s3, rds), filtering by a minimum risk score if needed.

Quick Start:
Upload: Send your JSON file with cloud resource data to /upload. Make sure the file
matches the expected structure.

Fetch Results: Post to /api/resources with the resource type and an optional
minimum score to see which resources pass or need attention.
"""

from flask import Flask, request, jsonify
from rule_runner import s3_rule_check, ec2_instance_check, rds_rule_check
import json
from . import database_ops as db

app = Flask(__name__)


def breakdown_json(json_file):
    ec2_instances = json_file["EC2Instances"]
    s3_buckets = json_file["S3Buckets"]
    rds_instances = json_file["RDSInstances"]
    return ec2_instances, s3_buckets, rds_instances


@app.route("/upload", methods=["POST"])
def upload_json():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    if file:
        try:
            json_data = json.load(file)
        except ValueError:
            return (
                jsonify(
                    "Your file was not accepted due to a ValueError during load. Please validate your file is valid JSON"
                ),
                400,
            )

        ec2_instances, s3_buckets, rds_instances = breakdown_json(json_data)
        db.batch_insert_ec2(data=ec2_instances)
        db.batch_insert_s3(data=s3_buckets)
        db.batch_insert_rds(data=rds_instances)
        return (
            jsonify(
                f"Data has been loaded. {(len(ec2_instances) + len(s3_buckets) + len(rds_instances))} Items Accepted."
            ),
            200,
        )


@app.route("/api/resources", methods=["POST"])
def get_resources():
    data = request.get_json()
    resource_type = data.get("type")
    min_score = data.get("min_score", 0)

    if resource_type.lower() == "s3":
        resources = s3_rule_check()
    elif resource_type.lower() == "ec2":
        resources = ec2_instance_check()
    elif resource_type.lower() == "rds":
        resources = rds_rule_check()
    else:
        return jsonify({"error": "Invalid resource type"}), 400

    try:
        filtered_data = {
            key: value
            for key, value in resources.items()
            if len(value.get("Violations", [])) >= min_score
        }
    except AttributeError as e:
        return jsonify(f"Error processing data: {e}"), 400

    return jsonify(filtered_data)


if __name__ == "__main__":
    app.run()
