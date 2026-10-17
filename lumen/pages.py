"""Public information pages: privacy notice, acceptable use policy, AI transparency, health check."""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, render_template

from . import __version__
from .ai_service import describe_provider

bp = Blueprint("pages", __name__)


@bp.route("/privacy")
def privacy_notice():
    return render_template("privacy.html", provider=describe_provider())


@bp.route("/policy")
def policy():
    return render_template("policy.html")


@bp.route("/transparency")
def transparency():
    return render_template("transparency.html", provider=describe_provider())


@bp.route("/health")
def health():
    return jsonify(status="ok", version=__version__, provider=current_app.config["LLM_PROVIDER"])
