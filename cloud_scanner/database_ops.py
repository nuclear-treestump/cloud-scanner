import functools
import json
import sqlite3
from typing import Optional, Callable, List, Tuple, Any
from decorator import autolog


@autolog(__name__)
def with_db_connection(db_path: str = "data.db") -> Callable:
    """
    Open new connection if not already supplied.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper_decorator(*args: Any, **kwargs: Any) -> Any:
            # Check if 'conn' is already supplied
            conn = kwargs.get("conn")
            if conn is not None and isinstance(conn, sqlite3.Connection):
                return func(*args, **kwargs)

            # Manage a new connection
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
        INSERT INTO ec2instances (group_id, group_name, ip_perms, description, public_ip, private_ip)
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
        INSERT INTO s3buckets (name, creation_date, public_access, encryption, logging_enabled)
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
        INSERT INTO rdsinstances (db_name, db_instance_type, db_software, public_access, encryption, db_portnumber, public_ip, private_ip)
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
