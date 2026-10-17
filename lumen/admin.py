"""Human oversight: review queue, user management and contest decisions."""
from __future__ import annotations

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from . import audit
from .db import get_db
from .records import request_view
from .security import admin_required
from .util import utc_str

bp = Blueprint("admin", __name__, url_prefix="/admin")
REVIEW_ACTIONS = {"validate": "validated", "warn": "warned", "block": "blocked", "delete": None}


@bp.route("/")
@admin_required
def home():
    db = get_db()
    stats = {
        "users": db.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "requests": db.execute("SELECT COUNT(*) FROM requests").fetchone()[0],
        "pending": db.execute("SELECT COUNT(*) FROM requests WHERE review_status='pending'").fetchone()[0],
        "contests": db.execute("SELECT COUNT(*) FROM contests WHERE status='open'").fetchone()[0],
    }
    pending = db.execute(
        "SELECT r.*, u.username FROM requests r JOIN users u ON u.id=r.user_id "
        "WHERE r.review_status='pending' ORDER BY r.id LIMIT 50").fetchall()
    contests = db.execute(
        "SELECT c.*, u.username, u.is_blocked FROM contests c JOIN users u ON u.id=c.user_id "
        "WHERE c.status='open' ORDER BY c.id LIMIT 50").fetchall()
    audit.record("ADMIN_VIEW_QUEUE")
    return render_template("admin.html", stats=stats, contests=contests,
                           pending=[dict(request_view(r, full=False), username=r["username"], user_id=r["user_id"]) for r in pending])


@bp.route("/requests/<int:req_id>")
@admin_required
def request_detail(req_id: int):
    row = get_db().execute("SELECT r.*, u.username FROM requests r JOIN users u ON u.id=r.user_id WHERE r.id=?",
                           (req_id,)).fetchone()
    if row is None or not row["is_flagged"]:
        abort(404)  # reviewers only ever see content that was flagged (data minimisation)
    audit.record("ADMIN_VIEW_CONTENT", target=req_id)
    return render_template("admin_request.html", row=dict(request_view(row), username=row["username"], user_id=row["user_id"]))


@bp.route("/requests/<int:req_id>/review", methods=["POST"])
@admin_required
def review(req_id: int):
    action = request.form.get("action", "")
    note = request.form.get("note", "").strip()
    if action not in REVIEW_ACTIONS or (action != "validate" and len(note) < 5):
        flash("Choose a valid action and write a justification (at least 5 characters).", "danger")
        return redirect(url_for("admin.request_detail", req_id=req_id))
    db = get_db()
    row = db.execute("SELECT r.*, u.role AS user_role FROM requests r JOIN users u ON u.id=r.user_id WHERE r.id=?",
                     (req_id,)).fetchone()
    if row is None or not row["is_flagged"]:
        abort(404)
    now = utc_str()
    if action == "block":
        if row["user_role"] == "admin" or row["user_id"] == g.user["id"]:
            flash("Administrator accounts cannot be suspended from the review queue.", "danger")
            return redirect(url_for("admin.request_detail", req_id=req_id))
        db.execute("UPDATE users SET is_blocked=1, blocked_reason=? WHERE id=?", (note, row["user_id"]))
    if action == "warn":
        db.execute("INSERT INTO warnings (user_id, request_id, reason, created_by) VALUES (?,?,?,?)",
                   (row["user_id"], req_id, note, g.user["id"]))
    if action == "delete":
        db.execute("DELETE FROM requests WHERE id=?", (req_id,))
    else:
        db.execute("UPDATE requests SET review_status=?, review_note=?, reviewed_by=?, reviewed_at=? WHERE id=?",
                   (REVIEW_ACTIONS[action], note or "Acceptable use confirmed.", g.user["id"], now, req_id))
    audit.record("ADMIN_REVIEW_" + action.upper(), target=req_id, detail={"user_id": row["user_id"]})
    flash(f"Request #{req_id}: {action} recorded.", "success")
    return redirect(url_for("admin.home"))


@bp.route("/users")
@admin_required
def users():
    rows = get_db().execute(
        "SELECT u.id, u.username, u.role, u.created_at, u.last_login_at, u.is_blocked, u.blocked_reason, "
        "(SELECT COUNT(*) FROM requests r WHERE r.user_id=u.id) AS requests, "
        "(SELECT COUNT(*) FROM warnings w WHERE w.user_id=u.id) AS warnings "
        "FROM users u ORDER BY u.id").fetchall()
    audit.record("ADMIN_VIEW_USERS")
    return render_template("admin_users.html", users=rows)


@bp.route("/users/<int:user_id>/unblock", methods=["POST"])
@admin_required
def unblock(user_id: int):
    get_db().execute("UPDATE users SET is_blocked=0, blocked_reason=NULL WHERE id=?", (user_id,))
    audit.record("ADMIN_UNBLOCK", target=user_id)
    flash("Account reactivated.", "success")
    return redirect(url_for("admin.users"))


@bp.route("/contests/<int:contest_id>/decide", methods=["POST"])
@admin_required
def decide_contest(contest_id: int):
    decision = request.form.get("decision", "")
    note = request.form.get("note", "").strip()
    if decision not in ("accepted", "rejected") or len(note) < 5:
        flash("Choose a decision and explain it (at least 5 characters).", "danger")
        return redirect(url_for("admin.home"))
    db = get_db()
    row = db.execute("SELECT * FROM contests WHERE id=? AND status='open'", (contest_id,)).fetchone()
    if row is None:
        abort(404)
    db.execute("UPDATE contests SET status=?, decision_note=?, decided_by=?, decided_at=? WHERE id=?",
               (decision, note, g.user["id"], utc_str(), contest_id))
    if decision == "accepted" and request.form.get("unblock"):
        db.execute("UPDATE users SET is_blocked=0, blocked_reason=NULL WHERE id=?", (row["user_id"],))
    audit.record("ADMIN_CONTEST_" + decision.upper(), target=contest_id, detail={"user_id": row["user_id"]})
    flash(f"Contest #{contest_id} {decision}.", "success")
    return redirect(url_for("admin.home"))
