"""Security primitives: CSRF, session user loading, throttling, headers, password policy."""
from __future__ import annotations

import hashlib
import hmac
import ipaddress
import re
import secrets
from functools import wraps

from flask import Flask, abort, current_app, flash, g, redirect, request, session, url_for
from markupsafe import Markup, escape

from .db import get_db
from .util import ago, utc_str

COMMON_PASSWORDS = {
    "password", "password1", "password123", "123456789", "1234567890", "qwertyuiop",
    "azertyuiop", "motdepasse", "welcome123", "admin12345", "letmein123", "iloveyou123",
}
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")


# ── CSRF ──────────────────────────────────────────────────────────────────────
def csrf_token() -> str:
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def csrf_field() -> Markup:
    return Markup('<input type="hidden" name="_csrf" value="%s">') % csrf_token()


def _check_csrf() -> None:
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = request.form.get("_csrf") or request.headers.get("X-CSRF-Token", "")
        expected = session.get("_csrf", "")
        if not expected or not hmac.compare_digest(sent.encode(), expected.encode()):
            abort(400, "Invalid or missing CSRF token. Reload the page and try again.")


# ── Pseudonymisation helpers ──────────────────────────────────────────────────
def mask_ip(ip: str | None) -> str:
    """Truncate an IP address (IPv4 -> /24, IPv6 -> /48) before it reaches the audit trail."""
    if not ip:
        return "-"
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return "-"
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{ip}/{prefix}", strict=False).network_address) + f"/{prefix}"


def pseudonym(value: str) -> str:
    """Keyed digest used instead of raw identifiers (usernames, IPs) in logs and throttling."""
    key = current_app.config["SECRET_KEY"].encode()
    return hmac.new(key, value.strip().lower().encode(), hashlib.sha256).hexdigest()[:24]


# ── Login throttling ──────────────────────────────────────────────────────────
def throttle_keys(username: str) -> tuple[str, str]:
    return pseudonym("user:" + username), pseudonym("ip:" + (request.remote_addr or "?"))


def is_throttled(db, user_key: str, ip_key: str) -> bool:
    cutoff = ago(minutes=current_app.config["LOGIN_WINDOW_MINUTES"])

    def count(key: str) -> int:
        return db.execute("SELECT COUNT(*) FROM login_attempts WHERE key_hash=? AND created_at>?",
                          (key, cutoff)).fetchone()[0]

    return (count(user_key) >= current_app.config["LOGIN_MAX_FAILURES"]
            or count(ip_key) >= current_app.config["LOGIN_IP_MAX_FAILURES"])


def record_failure(db, user_key: str, ip_key: str) -> None:
    now = utc_str()
    db.executemany("INSERT INTO login_attempts (key_hash, created_at) VALUES (?, ?)",
                   [(user_key, now), (ip_key, now)])
    db.commit()


def clear_failures(db, user_key: str) -> None:
    db.execute("DELETE FROM login_attempts WHERE key_hash=?", (user_key,))
    db.commit()


# ── Validation ────────────────────────────────────────────────────────────────
def validate_password(password: str, username: str) -> str | None:
    if len(password) < 10:
        return "Password must be at least 10 characters long."
    if password.lower() in COMMON_PASSWORDS:
        return "This password is too common. Choose a less predictable one."
    if username and username.lower() in password.lower():
        return "Password must not contain your username."
    if password.isdigit() or password.isalpha():
        return "Mix letters with digits or symbols."
    return None


def validate_username(username: str) -> str | None:
    if not USERNAME_RE.match(username):
        return "Username must be 3-32 characters: letters, digits, dot, dash or underscore (no '@')."
    return None


# ── Decorators ────────────────────────────────────────────────────────────────
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user["role"] != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped


# ── App wiring ────────────────────────────────────────────────────────────────
def _allowed_when_blocked(endpoint: str | None) -> bool:
    endpoint = endpoint or ""
    return endpoint == "auth.logout" or endpoint.startswith(("privacy.", "pages.", "static"))


def _before_request():
    if request.endpoint == "static":
        return None
    _check_csrf()
    g.user = None
    uid = session.get("user_id")
    if uid is not None:
        row = get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
        if row is None:
            session.clear()
        else:
            g.user = row  # role and block status always come from the database, never the cookie
    if g.user is not None and g.user["is_blocked"] and not _allowed_when_blocked(request.endpoint):
        flash("Your account is suspended. You can still contest the decision, export or delete your data.", "danger")
        return redirect(url_for("privacy.contest"))
    from .retention import maybe_purge
    maybe_purge()


def _after_request(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; "
        "form-action 'self'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    if current_app.config["LUMEN_ENV"] == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-store"
    return response


def init_app(app: Flask) -> None:
    app.before_request(_before_request)
    app.after_request(_after_request)
    app.jinja_env.globals["csrf_field"] = csrf_field
