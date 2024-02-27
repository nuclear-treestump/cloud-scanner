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
            name TEXT NOT NULL,
            group_id TEXT NOT NULL,
            group_name TEXT NOT NULL,
            ip_perms TEXT NOT NULL,
            description TEXT NOT NULL,
            public_ip TEXT NOT NULL,
            private_ip TEXT NOT NULL,
            UNIQUE(name)
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
            UNIQUE(name)
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
            public_ip TEXT NOT NULL,
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
