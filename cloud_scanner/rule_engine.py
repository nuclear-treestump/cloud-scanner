import json
from decorator import autolog
from database_ops import fetch_entry_by_id
from rule_runner import ec2_instance_check, s3_rule_check, rds_rule_check

"""

Plan
run the 3 check scripts, save json to variable

reprocess json obj, separating 3s and 2s, outputting len() as "Risk Score"

Create simple REST API to allow zeroing in on what data class one would want.

"""


def postprocessing():
    ec2_json = ec2_instance_check()
    s3_json = s3_rule_check()
    rds_json = rds_rule_check()
    try:
        filtered_data = {
            key: value
            for key, value in s3_json.items()
            if len(value.get("Violations", [])) > 2
        }
    except AttributeError as e:
        print(f"Error processing data: {e}")
