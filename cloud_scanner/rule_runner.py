from database_ops import with_db_connection
import sqlite3
import json


@with_db_connection()
def s3_rule_check(conn):
    """
    Process the three S3 rules and identify most at risk resources by weighted risk score.



    Rules:
        Assign 1 point if Public Access is true
        Assign 1 point if Encrypted is false
        Assign 1 point if logging_enabled is false

    """
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    queries = {
        "PublicAccessEnabled": "SELECT DISTINCT * FROM s3buckets WHERE public_access = 1 GROUP BY name, creation_date",
        "EncryptionDisabled": "SELECT DISTINCT * FROM s3buckets WHERE encryption = 0 GROUP BY name, creation_date",
        "LoggingDisabled": "SELECT DISTINCT * FROM s3buckets WHERE logging_enabled = 0 GROUP BY name, creation_date",
    }
    all_results = {}

    for violation_type, query in queries.items():
        cursor.execute(query)
        rows = cursor.fetchall()
        processed_rows = process_results(violation_type, rows)

        for row_id, data in processed_rows.items():
            if row_id in all_results:
                all_results[row_id]["Violations"].extend(data["Violations"])
            else:
                all_results[row_id] = data

    for data in all_results.values():
        data["Violations"] = list(set(data["Violations"]))

    sorted_results = sorted(
        all_results.items(), key=lambda item: len(item[1]["Violations"]), reverse=True
    )

    json_output = {row_id: json.dumps(data) for row_id, data in sorted_results}
    return json_output


def process_results(violation_type, rows):
    processed_rows = {}
    for row in rows:
        row_id = row["id"]
        if row_id not in processed_rows:
            processed_rows[row_id] = dict(row)
            processed_rows[row_id]["Violations"] = [violation_type]
        else:
            processed_rows[row_id]["Violations"].append(violation_type)
    return processed_rows


s3_rule_check()
