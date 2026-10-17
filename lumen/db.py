"""SQLite access (one connection per request)."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from flask import Flask, current_app, g

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect(current_app.config["DATABASE_PATH"])
    return g.db


def close_db(_exc=None) -> None:
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    path = current_app.config["DATABASE_PATH"]
    conn = connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    try:
        os.chmod(path, 0o600)  # secure storage: owner read/write only
    except OSError:
        pass


def init_app(app: Flask) -> None:
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
