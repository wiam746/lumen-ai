"""Data-subject rights (GDPR Art. 12-22; Law 09-08 Art. 5-9) and the contestation procedure."""
from __future__ import annotations

import json
import sqlite3

from flask import Blueprint, Response, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import audit
from .db import get_db
from .records import request_view
from .security import login_required, validate_password, validate_username
from .util import utc_str

bp = Blueprint("privacy", __name__)


def _collect(db, user_id: int) -> dict:
    user = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    reqs = db.execute("SELECT * FROM requests WHERE user_id=? ORDER BY id", (user_id,)).fetchall()
    return {
        "exported_at": utc_str() + " UTC",
        "account": {k: user[k] for k in ("id", "username", "role", "created_at", "last_login_at", "policy_version",
                                          "policy_accepted_at", "external_ai_optout", "is_blocked", "blocked_reason")},
        "requests": [{k: v for k, v in request_view(r).items() if k not in ("prompt_preview", "response_preview")} for r in reqs],
        "warnings": [dict(r) for r in db.execute(
            "SELECT id, request_id, reason, created_at FROM warnings WHERE user_id=?", (user_id,))],
        "contests": [dict(r) for r in db.execute(
            "SELECT id, request_id, kind, message, status, decision_note, decided_at, created_at FROM contests WHERE user_id=?",
            (user_id,))],
    }


# ── Access, portability ───────────────────────────────────────────────────────
@bp.route("/my-data")
@login_required
def my_data():
    db = get_db()
    counts = {
        "requests": db.execute("SELECT COUNT(*) FROM requests WHERE user_id=?", (g.user["id"],)).fetchone()[0],
        "warnings": db.execute("SELECT COUNT(*) FROM warnings WHERE user_id=?", (g.user["id"],)).fetchone()[0],
        "contests": db.execute("SELECT COUNT(*) FROM contests WHERE user_id=?", (g.user["id"],)).fetchone()[0],
    }
    audit.record("RIGHT_ACCESS")
    return render_template("my_data.html", counts=counts)


@bp.route("/my-data/export")
@login_required
def export_data():
    payload = json.dumps(_collect(get_db(), g.user["id"]), ensure_ascii=False, indent=2)
    audit.record("RIGHT_EXPORT")
    return Response(payload, mimetype="application/json",
                    headers={"Content-Disposition": "attachment; filename=lumen-my-data.json"})


# ── Erasure ───────────────────────────────────────────────────────────────────
@bp.route("/my-data/delete-history", methods=["POST"])
@login_required
def delete_history():
    n = get_db().execute("DELETE FROM requests WHERE user_id=?", (g.user["id"],)).rowcount
    audit.record("RIGHT_ERASURE_HISTORY", detail={"deleted": n})
    flash("Your request history has been deleted.", "success")
    return redirect(url_for("privacy.my_data"))


@bp.route("/my-data/delete-account", methods=["POST"])
@login_required
def delete_account():
    db = get_db()
    if not check_password_hash(g.user["password_hash"], request.form.get("password", "")):
        flash("Password incorrect. Your account was not deleted.", "danger")
        return redirect(url_for("privacy.settings"))
    if g.user["role"] == "admin" and db.execute("SELECT COUNT(*) FROM users WHERE role='admin'").fetchone()[0] <= 1:
        flash("You are the last administrator. Promote another administrator before deleting this account.", "danger")
        return redirect(url_for("privacy.settings"))
    uid = g.user["id"]
    db.execute("DELETE FROM users WHERE id=?", (uid,))  # cascades to requests, warnings, contests
    audit.record("RIGHT_ERASURE_ACCOUNT", actor=uid)
    session.clear()
    flash("Your account and all associated data have been deleted.", "success")
    return redirect(url_for("auth.login"))


# ── Rectification, objection ──────────────────────────────────────────────────
@bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


@bp.route("/settings/username", methods=["POST"])
@login_required
def change_username():
    new = request.form.get("username", "").strip()
    error = validate_username(new)
    if error:
        flash(error, "danger")
        return redirect(url_for("privacy.settings"))
    try:
        get_db().execute("UPDATE users SET username=? WHERE id=?", (new, g.user["id"]))
    except sqlite3.IntegrityError:
        flash("This username is already taken.", "danger")
        return redirect(url_for("privacy.settings"))
    audit.record("RIGHT_RECTIFICATION", detail={"field": "username"})
    flash("Username updated.", "success")
    return redirect(url_for("privacy.settings"))


@bp.route("/settings/password", methods=["POST"])
@login_required
def change_password():
    if not check_password_hash(g.user["password_hash"], request.form.get("current_password", "")):
        flash("Current password incorrect.", "danger")
        return redirect(url_for("privacy.settings"))
    new = request.form.get("new_password", "")
    error = validate_password(new, g.user["username"])
    if error:
        flash(error, "danger")
        return redirect(url_for("privacy.settings"))
    get_db().execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(new), g.user["id"]))
    audit.record("PASSWORD_CHANGED")
    flash("Password updated.", "success")
    return redirect(url_for("privacy.settings"))


@bp.route("/settings/ai-processing", methods=["POST"])
@login_required
def ai_processing():
    optout = 1 if request.form.get("external_ai_optout") else 0
    get_db().execute("UPDATE users SET external_ai_optout=? WHERE id=?", (optout, g.user["id"]))
    audit.record("RIGHT_OBJECTION", detail={"external_ai_optout": bool(optout)})
    flash("Preference saved." if optout else "External AI processing re-enabled.", "success")
    return redirect(url_for("privacy.settings"))


# ── Contestation procedure ────────────────────────────────────────────────────
@bp.route("/contest")
@login_required
def contest():
    db = get_db()
    mine = db.execute("SELECT * FROM contests WHERE user_id=? ORDER BY id DESC", (g.user["id"],)).fetchall()
    prefill = request.args.get("request_id", type=int)
    return render_template("contest.html", contests=mine, prefill=prefill)


@bp.route("/contest", methods=["POST"])
@login_required
def contest_create():
    kind = request.form.get("kind", "other")
    message = request.form.get("message", "").strip()
    req_id = request.form.get("request_id", type=int)
    if kind not in ("ai_output", "moderation", "other") or not (10 <= len(message) <= 2000):
        flash("Describe your contest in 10 to 2000 characters.", "danger")
        return redirect(url_for("privacy.contest"))
    db = get_db()
    if req_id and not db.execute("SELECT 1 FROM requests WHERE id=? AND user_id=?", (req_id, g.user["id"])).fetchone():
        req_id = None
    cur = db.execute("INSERT INTO contests (user_id, request_id, kind, message) VALUES (?,?,?,?)",
                     (g.user["id"], req_id, kind, message))
    audit.record("CONTEST_CREATED", target=cur.lastrowid, detail={"kind": kind})
    flash("Your contest was registered. A human reviewer will answer it.", "success")
    return redirect(url_for("privacy.contest"))
