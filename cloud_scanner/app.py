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
        json_data = json.load(file)
        ec2_instances, s3_buckets, rds_instances = breakdown_json(json_data)
        db.batch_insert_ec2(data=ec2_instances)
        db.batch_insert_s3(data=s3_buckets)
        db.batch_insert_rds(data=rds_instances)
        return (
            jsonify(
                f"Data has been loaded. {len(ec2_instances) + len(s3_buckets) + len(rds_instances)} Items Accepted."
            ),
            200,
        )


@app.route("/api/resources", methods=["POST"])
def get_resources():
    print(request.headers)
    print(request.cookies)
    print(request.data)
    print(request.args)
    print(request.form)
    print(request.endpoint)
    print(request.method)
    print(request.remote_addr)
    data = request.get_json()
    print(request)
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
        print(f"Error processing data: {e}")

    return jsonify(filtered_data)


if __name__ == "__main__":
    app.run()
