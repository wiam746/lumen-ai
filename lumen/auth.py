"""Registration, sign-in and sign-out."""
from __future__ import annotations

import hmac
import sqlite3

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import audit
from .db import get_db
from .security import (clear_failures, is_throttled, login_required, pseudonym, record_failure,
                       throttle_keys, validate_password, validate_username)
from .util import utc_str

bp = Blueprint("auth", __name__)
_DUMMY_HASH = generate_password_hash("not-a-real-password")  # equalises timing for unknown users


@bp.route("/")
def index():
    return redirect(url_for("chat.dashboard" if g.user else "auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("chat.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user_key, ip_key = throttle_keys(username)
        if is_throttled(db, user_key, ip_key):
            audit.record("LOGIN_THROTTLED", detail={"user_ref": pseudonym(username)})
            flash("Too many failed attempts. Try again in a few minutes.", "danger")
            return render_template("login.html"), 429
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        valid = check_password_hash(user["password_hash"] if user else _DUMMY_HASH, password) and user is not None
        if not valid:
            record_failure(db, user_key, ip_key)
            # The typed username is never logged (people sometimes type passwords there).
            audit.record("LOGIN_FAILED", detail={"user_ref": pseudonym(username)})
            flash("Incorrect username or password.", "danger")
            return render_template("login.html"), 401
        clear_failures(db, user_key)
        session.clear()  # prevents session fixation
        session["user_id"] = user["id"]
        session.permanent = True
        db.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (utc_str(), user["id"]))
        audit.record("LOGIN_SUCCESS", actor=user["id"])
        return redirect(url_for("chat.dashboard"))
    return render_template("login.html")


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    audit.record("LOGOUT")
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    cfg = current_app.config
    if not cfg["REGISTRATION_ENABLED"]:
        flash("Registration is closed. Contact an administrator.", "warning")
        return redirect(url_for("auth.login"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        code = request.form.get("registration_code", "")
        error = validate_username(username) or validate_password(password, username)
        if not error and password != request.form.get("password_confirm", ""):
            error = "Passwords do not match."
        if not error and not request.form.get("accept_policy"):
            error = "You must accept the acceptable use policy and privacy notice."
        if not error and cfg["REGISTRATION_CODE"] and not hmac.compare_digest(
                code.encode(), cfg["REGISTRATION_CODE"].encode()):
            error = "Invalid registration code."
        if error:
            flash(error, "danger")
            return render_template("register.html", username=username), 400
        db = get_db()
        try:
            cur = db.execute(
                "INSERT INTO users (username, password_hash, role, policy_version, policy_accepted_at) "
                "VALUES (?, ?, 'user', ?, ?)",
                (username, generate_password_hash(password), cfg["POLICY_VERSION"], utc_str()),
            )
        except sqlite3.IntegrityError:
            flash("This username is already taken.", "danger")
            return render_template("register.html", username=username), 409
        audit.record("REGISTER", actor=cur.lastrowid, detail={"policy_version": cfg["POLICY_VERSION"]})
        flash("Account created. You can now sign in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")
