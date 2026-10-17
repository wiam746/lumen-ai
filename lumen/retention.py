"""Storage limitation (GDPR Art. 5(1)(e)): automatic deletion of expired records."""
from __future__ import annotations

import time
from datetime import timedelta

from flask import current_app

from . import audit
from .db import get_db
from .util import ago, parse_utc, utc_str, utcnow


def purge_expired(db) -> dict:
    cfg = current_app.config
    counts = {
        "requests": db.execute("DELETE FROM requests WHERE created_at < ?",
                               (ago(days=cfg["REQUEST_RETENTION_DAYS"]),)).rowcount,
        "contests": db.execute("DELETE FROM contests WHERE created_at < ? AND status != 'open'",
                               (ago(days=cfg["CONTEST_RETENTION_DAYS"]),)).rowcount,
        "warnings": db.execute("DELETE FROM warnings WHERE created_at < ?",
                               (ago(days=cfg["CONTEST_RETENTION_DAYS"]),)).rowcount,
        "login_attempts": db.execute("DELETE FROM login_attempts WHERE created_at < ?",
                                     (ago(days=1),)).rowcount,
        "audit_events": db.execute("DELETE FROM audit_events WHERE created_at < ?",
                                   (ago(days=cfg["AUDIT_RETENTION_DAYS"]),)).rowcount,
    }
    db.commit()
    return counts


def maybe_purge() -> None:
    """Run the purge at most once per 24h, checked lazily (at most hourly per process)."""
    app = current_app
    if time.time() - app.extensions.get("lumen_purge_check", 0) < 3600:
        return
    app.extensions["lumen_purge_check"] = time.time()
    db = get_db()
    row = db.execute("SELECT value FROM meta WHERE key='last_purge'").fetchone()
    if row and utcnow() - parse_utc(row["value"]) < timedelta(hours=24):
        return
    counts = purge_expired(db)
    db.execute("INSERT INTO meta (key, value) VALUES ('last_purge', ?) "
               "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (utc_str(),))
    audit.record("RETENTION_PURGE", actor="system", detail=counts)
