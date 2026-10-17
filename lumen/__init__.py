"""Lumen AI: a privacy-first, accountable AI assistant for organizations."""
from __future__ import annotations

import getpass
import logging

import click
from flask import Flask, g, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash

__version__ = "1.0.0"

ERRORS = {
    400: ("Request rejected", "The request could not be processed. Reload the page and try again."),
    403: ("Not allowed", "You do not have permission to open this page."),
    404: ("Page not found", "The page you asked for does not exist."),
    405: ("Method not allowed", "This action is not available here."),
    413: ("Request too large", "The request is larger than the allowed size."),
    500: ("Something went wrong", "An unexpected error occurred. It has been logged."),
}


def create_app(overrides: dict | None = None) -> Flask:
    from .config import load_config

    app = Flask(__name__)
    app.config.update(load_config(overrides))
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    hops = app.config["PROXY_FIX_HOPS"]
    if hops:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=hops, x_proto=hops, x_host=hops)

    from . import ai_service, crypto, db, security
    crypto.init_app(app)
    db.init_app(app)
    security.init_app(app)

    from . import admin, auth, chat, pages, privacy
    for module in (auth, chat, privacy, admin, pages):
        app.register_blueprint(module.bp)

    @app.context_processor
    def inject_globals():
        return {
            "org_name": app.config["ORG_NAME"], "dpo_contact": app.config["DPO_CONTACT"],
            "version": __version__, "current_user": g.get("user"),
            "retention_days": app.config["REQUEST_RETENTION_DAYS"],
            "policy_version": app.config["POLICY_VERSION"],
            "max_prompt_chars": app.config["MAX_PROMPT_CHARS"],
            "registration_code_required": bool(app.config["REGISTRATION_CODE"]),
        }

    def render_error(error):
        code = getattr(error, "code", 500)
        title, message = ERRORS.get(code, ERRORS[500])
        return render_template("error.html", code=code, title=title, message=message), code

    for code in ERRORS:
        app.register_error_handler(code, render_error)

    _register_cli(app)
    return app


def _register_cli(app: Flask) -> None:
    from . import audit
    from .db import get_db
    from .retention import purge_expired
    from .security import validate_password

    @app.cli.command("create-admin")
    @click.argument("username")
    def create_admin(username):
        """Create an administrator (password is prompted, never stored in a file)."""
        password = getpass.getpass("Password: ")
        if password != getpass.getpass("Repeat password: "):
            raise click.ClickException("Passwords do not match.")
        error = validate_password(password, username)
        if error:
            raise click.ClickException(error)
        db = get_db()
        db.execute(
            "INSERT INTO users (username, password_hash, role, policy_version, policy_accepted_at) "
            "VALUES (?, ?, 'admin', ?, datetime('now'))",
            (username, generate_password_hash(password), app.config["POLICY_VERSION"]))
        audit.record("ADMIN_CREATED_CLI", actor="system", detail={"username_ref": username[:1] + "***"})
        click.echo(f"Administrator '{username}' created.")

    @app.cli.command("reset-password")
    @click.argument("username")
    def reset_password(username):
        """Reset a user's password (for lost passwords; no e-mail is collected)."""
        db = get_db()
        user = db.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not user:
            raise click.ClickException("Unknown user.")
        password = getpass.getpass("New password: ")
        error = validate_password(password, username)
        if error:
            raise click.ClickException(error)
        db.execute("UPDATE users SET password_hash=? WHERE id=?", (generate_password_hash(password), user["id"]))
        audit.record("PASSWORD_RESET_CLI", actor="system", target=user["id"])
        click.echo("Password updated.")

    @app.cli.command("purge")
    def purge():
        """Delete expired records now (also runs automatically every 24h)."""
        click.echo(f"Purged: {purge_expired(get_db())}")

    @app.cli.command("verify-audit")
    def verify_audit():
        """Verify the integrity of the audit hash chain."""
        ok, checked, broken = audit.verify(get_db())
        if ok:
            click.echo(f"Audit trail intact ({checked} events verified).")
        else:
            raise click.ClickException(f"Audit trail BROKEN at event #{broken} (after {checked} valid events).")
