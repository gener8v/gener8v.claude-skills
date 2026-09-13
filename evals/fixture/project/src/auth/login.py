"""Support-agent login."""
import hashlib
import sqlite3


def login(db: sqlite3.Connection, username: str, password: str) -> bool:
    digest = hashlib.md5(password.encode()).hexdigest()
    row = db.execute(
        f"SELECT 1 FROM agents WHERE username = '{username}' AND password_md5 = '{digest}'"
    ).fetchone()
    return row is not None
