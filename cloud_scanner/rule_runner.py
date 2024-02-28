"""
rule_runner.py

The purpose of this module is to serve as the runner of the rules.

Each of the *_check() functions work in the same way:
1. Uses the @with_db_connection() decorator from database_ops to seamlessly
handle connection management to connect to the DB
2. The for loop runs each of the SQL queries, using the key of the query as the
name of the violation
3. Re-assembles the data into a dictionary of dictionaries, with the ID from the SQLite DB
as the primary key (given that duplicate entries were found in the original data load, so the 
name field could not be used for this)
4. Assign Violation nested key to each primary key with the name of the violation.
5. Read this dictionary into all_results dict
6. Repeat for all existing queries
7. Sort by len() of violation subkey, in descending order
8. return json_output
"""

from database_ops import with_db_connection
import sqlite3


@with_db_connection()
def s3_rule_check(conn):
    """
    Process the three S3 rules and identify most at risk resources by weighted risk score.



    Rules:
        Assign 1 point if Public Access is true
        Assign 1 point if Encrypted is false
        Assign 1 point if logging_enabled is false


    conn: SQLite Connection Object supplied by decorator

    returns:
        dict

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

    json_output = {row_id: data for row_id, data in sorted_results}
    return json_output


@with_db_connection()
def ec2_instance_check(conn):
    """
    Process the 2 EC2 rules and identify most at risk resources by weighted risk score.

    Rules:
        Assign 1 point if IpPermissions exists with an insecure CIDR range
        Assign 1 point if public IP is present.


    conn: SQLite Connection Object supplied by decorator

    returns:
        dict

    """
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    queries = {
        "PublicIPExposure": "SELECT DISTINCT * FROM ec2instances WHERE public_ip IS NOT NULL GROUP BY group_id, group_name",
        "InsecureCIDRRange": "SELECT DISTINCT * FROM ec2instances WHERE ip_perms IS NOT '[]' GROUP BY group_id, group_name",
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
    json_output = {row_id: data for row_id, data in sorted_results}

    return json_output


@with_db_connection()
def rds_rule_check(conn):
    """
    Process the two RDS rules and identify most at risk resources by weighted risk score.



    Rules:
        Assign 1 point if Encrypted is false
        Assign 1 point if Public IP exists

    conn: SQLite Connection Object supplied by decorator

    returns:
        dict

    """
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    queries = {
        "PublicAccessEnabled": "SELECT DISTINCT * FROM rdsinstances WHERE public_access = 1 GROUP BY db_name",
        "EncryptionDisabled": "SELECT DISTINCT * FROM rdsinstances WHERE encryption = 0 GROUP BY db_name",
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

    json_output = {row_id: data for row_id, data in sorted_results}
    return json_output


def process_results(violation_type: str, rows: dict) -> dict:
    """
    Assign violation nested key + append new violations to ID

    violation_type (str): Text of Violation string
    rows (dict):  rows from SQL query.
    """
    processed_rows = {}
    for row in rows:
        row_id = row["id"]
        if row_id not in processed_rows:
            processed_rows[row_id] = dict(row)
            processed_rows[row_id]["Violations"] = [violation_type]
        else:
            processed_rows[row_id]["Violations"].append(violation_type)
    return processed_rows
