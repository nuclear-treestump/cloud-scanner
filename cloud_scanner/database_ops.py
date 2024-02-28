"""
database_ops.py

Handles the creation, reading, and writing of data into the SQLite DB

Usage of the with_db_connection() decorator defines a default path to
data.db (which can be overwritten) and simplifies db connection management.

All queries are parameterized, and where possible, executemany is used to
limit the number of transactions.

"""

import functools
import json
import sqlite3
from typing import Optional, Callable, List, Tuple, Any
from decorator import autolog


@autolog(__name__)
def with_db_connection(db_path: str = "../data.db") -> Callable:
    """
    Open new connection if not already supplied.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_decorator(*args: Any, **kwargs: Any) -> Any:

            conn = kwargs.get("conn")
            if conn is not None and isinstance(conn, sqlite3.Connection):
                return func(*args, **kwargs)

            with sqlite3.connect(db_path) as conn:
                kwargs["conn"] = conn
                return func(*args, **kwargs)

        return wrapper_decorator

    return decorator


@autolog(__name__)
@with_db_connection()
def setup_database(conn: Optional[sqlite3.Connection] = None) -> None:
    """
    Sets up the database and associated tables.

    Args:
        conn (sqlite3.Connection, optional): An existing database
        connection. If not provided, a new connection will be created.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ec2instances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT NOT NULL,
            group_name TEXT NOT NULL,
            ip_perms TEXT,
            description TEXT NOT NULL,
            public_ip TEXT,
            private_ip TEXT NOT NULL,
            UNIQUE(group_id)
        )
    """
    )
    conn.commit()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS s3buckets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            creation_date TEXT NOT NULL,
            public_access BOOLEAN NOT NULL,
            encryption BOOLEAN NOT NULL,
            logging_enabled BOOLEAN NOT NULL,
            UNIQUE(name, creation_date)
        )
    """
    )
    conn.commit()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rdsinstances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            db_name TEXT NOT NULL,
            db_instance_type TEXT NOT NULL,
            db_software TEXT NOT NULL,
            public_access BOOLEAN NOT NULL,
            encryption BOOLEAN NOT NULL,
            db_portnumber INT NOT NULL,
            public_ip TEXT,
            private_ip TEXT NOT NULL,
            UNIQUE(db_name)
        )
    """
    )
    conn.commit()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS flags (
            key TEXT PRIMARY KEY,
            value TEXT,
            UNIQUE(key)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            resource_table TEXT,
            condition_field TEXT,
            condition_value TEXT,
            risk_score INT,
            remediation_steps TEXT
        )
        """
    )
    conn.commit()


@autolog(__name__)
@with_db_connection()
def batch_insert_ec2(
    data: List[dict], conn: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Batch insert ec2 entries into SQLite DB table 'ec2instances'

    data: List of dictionaries containing EC2 instances
    conn (Optional): SQLite3 connection. Supplied by @with_db_connection() decorator
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO ec2instances (group_id, group_name, ip_perms, description, public_ip, private_ip)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                d["GroupId"],
                d["GroupName"],
                json.dumps(d["IpPermissions"]),
                d["Description"],
                d["PublicIp"],
                d["PrivateIp"],
            )
            for d in data
        ],
    )
    conn.commit()


@autolog(__name__)
@with_db_connection()
def batch_insert_s3(
    data: List[dict], conn: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Batch insert s3 bucket entries into SQLite DB table 's3buckets'

    data: List of dictionaries containing S3 Bucket entries
    conn (Optional): SQLite3 connection. Supplied by @with_db_connection() decorator
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO s3buckets (name, creation_date, public_access, encryption, logging_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                d["Name"],
                d["CreationDate"],
                d["PublicAccess"],
                d["Encrypted"],
                d["LoggingEnabled"],
            )
            for d in data
        ],
    )
    conn.commit()


@autolog(__name__)
@with_db_connection()
def batch_insert_rds(
    data: List[dict], conn: Optional[sqlite3.Connection] = None
) -> bool:
    """
    Batch insert RDS entries into SQLite DB table 'rdsinstances'

    data: List of dictionaries containing RDS instances
    conn (Optional): SQLite3 connection. Supplied by @with_db_connection() decorator
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT OR REPLACE INTO rdsinstances (db_name, db_instance_type, db_software, public_access, encryption, db_portnumber, public_ip, private_ip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                d["DBInstanceIdentifier"],
                d["DBInstanceClass"],
                d["Engine"],
                d["PubliclyAccessible"],
                d["StorageEncrypted"],
                d["DBPortNumber"],
                d["PublicIp"],
                d["PrivateIp"],
            )
            for d in data
        ],
    )
    conn.commit()


def fetch_entry_by_id(
    item_id: int, table_name: str, conn: Optional[sqlite3.Connection] = None
) -> Optional[sqlite3.Row]:
    """
    Get row from the database by ID.

    Args:
        item_id (int): The ID of the row to query for.
        table_name (str): The table to pull from.
        conn (sqlite3.Connection, optional): An existing
        database connection. If not provided, a new connection
        will be created.

    Returns:
        sqlite3.Row object
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM ? WHERE id = ?",
        (table_name, item_id),
    )
    row = cursor.fetchone()

    if row:
        return row
    return None
