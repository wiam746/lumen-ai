"""Dashboard, AI requests and personal history."""
from __future__ import annotations

from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from . import audit
from .ai_service import describe_provider, generate_response
from .compliance import check_compliance, redact
from .crypto import encrypt
from .db import get_db
from .records import request_view
from .security import login_required
from .util import ago

bp = Blueprint("chat", __name__)
PER_PAGE = 10


@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    rows = db.execute("SELECT * FROM requests WHERE user_id=? ORDER BY id DESC LIMIT 5", (g.user["id"],)).fetchall()
    total = db.execute("SELECT COUNT(*) FROM requests WHERE user_id=?", (g.user["id"],)).fetchone()[0]
    open_contests = db.execute("SELECT COUNT(*) FROM contests WHERE user_id=? AND status='open'", (g.user["id"],)).fetchone()[0]
    return render_template("dashboard.html", recent=[request_view(r, full=False) for r in rows], total=total,
                           open_contests=open_contests, provider=describe_provider(bool(g.user["external_ai_optout"])))


@bp.route("/ask", methods=["GET", "POST"])
@login_required
def ask():
    cfg = current_app.config
    provider = describe_provider(bool(g.user["external_ai_optout"]))
    if request.method == "GET":
        return render_template("ask.html", provider=provider)

    prompt = request.form.get("prompt", "").strip()
    if not prompt:
        flash("Enter a question or a text to summarise.", "warning")
        return render_template("ask.html", provider=provider), 400
    if len(prompt) > cfg["MAX_PROMPT_CHARS"]:
        flash(f"Your message is limited to {cfg['MAX_PROMPT_CHARS']} characters.", "danger")
        return render_template("ask.html", provider=provider, prompt=prompt), 400

    db = get_db()
    used = db.execute("SELECT COUNT(*) FROM requests WHERE user_id=? AND created_at>?",
                      (g.user["id"], ago(hours=1))).fetchone()[0]
    if used >= cfg["ASK_RATE_LIMIT_PER_HOUR"]:
        audit.record("RATE_LIMIT", detail={"limit": cfg["ASK_RATE_LIMIT_PER_HOUR"]})
        flash(f"Limit of {cfg['ASK_RATE_LIMIT_PER_HOUR']} requests per hour reached. Try again later.", "danger")
        return render_template("ask.html", provider=provider, prompt=prompt), 429

    check = check_compliance(prompt)
    if check.blocked:
        # Rejected before storage and before any provider call; the content is not logged.
        audit.record("COMPLIANCE_BLOCK", detail={"categories": check.categories})
        flash(check.reason + " Remove it and try again. Nothing was stored or sent.", "danger")
        return render_template("ask.html", provider=provider, prompt=prompt), 422

    result = generate_response(prompt, allow_external=not g.user["external_ai_optout"])
    answer = redact(result.text)
    cur = db.execute(
        "INSERT INTO requests (user_id, prompt_enc, response_enc, provider, model, external_transfer, "
        "is_flagged, flag_reason, review_status) VALUES (?,?,?,?,?,?,?,?,?)",
        (g.user["id"], encrypt(prompt), encrypt(answer), result.provider, result.model, int(result.external),
         int(check.flagged), check.reason if check.flagged else "", "pending" if check.flagged else "none"),
    )
    audit.record("ASK", target=cur.lastrowid, detail={
        "provider": result.provider, "external_transfer": result.external, "flagged": check.flagged})
    return render_template("ask.html", provider=provider, prompt=prompt, answer=answer, result=result,
                           request_id=cur.lastrowid, flagged=check.flagged, flag_reason=check.reason)


@bp.route("/history")
@login_required
def history():
    page = max(1, request.args.get("page", 1, type=int))
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM requests WHERE user_id=?", (g.user["id"],)).fetchone()[0]
    rows = db.execute("SELECT * FROM requests WHERE user_id=? ORDER BY id DESC LIMIT ? OFFSET ?",
                      (g.user["id"], PER_PAGE, (page - 1) * PER_PAGE)).fetchall()
    pages = max(1, -(-total // PER_PAGE))
    return render_template("history.html", rows=[request_view(r, full=False) for r in rows], page=page, pages=pages, total=total)


@bp.route("/history/<int:req_id>")
@login_required
def history_detail(req_id: int):
    row = get_db().execute("SELECT * FROM requests WHERE id=? AND user_id=?", (req_id, g.user["id"])).fetchone()
    if row is None:
        flash("Request not found.", "danger")
        return redirect(url_for("chat.history"))
    audit.record("HISTORY_DETAIL", target=req_id)
    return render_template("history_detail.html", row=request_view(row))


@bp.route("/history/<int:req_id>/delete", methods=["POST"])
@login_required
def delete_request(req_id: int):
    db = get_db()
    deleted = db.execute("DELETE FROM requests WHERE id=? AND user_id=?", (req_id, g.user["id"])).rowcount
    if deleted:
        audit.record("DELETE_REQUEST", target=req_id)
        flash("Request deleted.", "success")
    return redirect(url_for("chat.history"))
