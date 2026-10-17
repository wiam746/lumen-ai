"""Tamper-evident audit trail (accountability, GDPR Art. 5(2) and Art. 24).

Every event stores the SHA-256 hash of the previous event, forming a chain:
altering or deleting a past event breaks verification (`flask verify-audit`).
Events hold pseudonymous user IDs and masked IPs, never usernames or message content.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3

from flask import g, has_request_context, request

from .db import get_db
from .security import mask_ip
from .util import utc_str

logger = logging.getLogger("lumen.audit")
GENESIS = "0" * 64


def _digest(prev: str, created_at: str, actor: str, action: str, target: str, detail: str, ip: str) -> str:
    payload = json.dumps([prev, created_at, actor, action, target, detail, ip],
                         ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def record(action: str, *, actor=None, target: str = "", detail: dict | None = None) -> None:
    """Append an event. NOTE: commits the current transaction."""
    db = get_db()
    if actor is None:
        user = g.get("user") if has_request_context() else None
        actor = user["id"] if user else "anonymous"
    actor = str(actor)
    ip = mask_ip(request.remote_addr) if has_request_context() else "-"
    detail_s = json.dumps(detail or {}, ensure_ascii=False, sort_keys=True)
    for _ in range(8):  # retry if a concurrent worker appended first (UNIQUE prev_hash)
        row = db.execute("SELECT hash FROM audit_events ORDER BY id DESC LIMIT 1").fetchone()
        prev = row["hash"] if row else GENESIS
        created = utc_str()
        digest = _digest(prev, created, actor, action, str(target), detail_s, ip)
        try:
            db.execute(
                "INSERT INTO audit_events (created_at, actor, action, target, detail, ip_masked, prev_hash, hash) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (created, actor, action, str(target), detail_s, ip, prev, digest),
            )
            db.commit()
            logger.info("action=%s actor=%s target=%s", action, actor, target)
            return
        except sqlite3.IntegrityError:
            continue
    raise RuntimeError("Could not append audit event")


def verify(db) -> tuple[bool, int, int | None]:
    """Return (ok, events_checked, first_broken_event_id)."""
    prev_hash = None
    checked = 0
    for row in db.execute("SELECT * FROM audit_events ORDER BY id"):
        expected = _digest(row["prev_hash"], row["created_at"], row["actor"], row["action"],
                           row["target"], row["detail"], row["ip_masked"])
        if expected != row["hash"] or (prev_hash is not None and row["prev_hash"] != prev_hash):
            return False, checked, row["id"]
        prev_hash = row["hash"]
        checked += 1
    return True, checked, None
