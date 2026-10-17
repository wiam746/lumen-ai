"""Small shared helpers (UTC timestamps stored as sortable strings)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

FMT = "%Y-%m-%d %H:%M:%S"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def utc_str(dt: datetime | None = None) -> str:
    return (dt or utcnow()).strftime(FMT)


def parse_utc(value: str) -> datetime:
    return datetime.strptime(value, FMT).replace(tzinfo=timezone.utc)


def ago(**delta) -> str:
    """UTC timestamp string for `now - delta` (e.g. ago(hours=1))."""
    return utc_str(utcnow() - timedelta(**delta))
