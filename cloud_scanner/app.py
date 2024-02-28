from flask import Flask, request, jsonify
from rule_runner import s3_rule_check, ec2_instance_check, rds_rule_check
import json

app = Flask(__name__)


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
