"""Helpers to turn encrypted request rows into displayable dictionaries."""
from __future__ import annotations

from .crypto import decrypt


def preview(text: str, limit: int = 140) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def request_view(row, *, full: bool = True) -> dict:
    prompt, response = decrypt(row["prompt_enc"]), decrypt(row["response_enc"])
    view = {
        "id": row["id"], "created_at": row["created_at"], "provider": row["provider"], "model": row["model"],
        "external_transfer": bool(row["external_transfer"]), "is_flagged": bool(row["is_flagged"]),
        "flag_reason": row["flag_reason"], "review_status": row["review_status"], "review_note": row["review_note"],
        "prompt_preview": preview(prompt), "response_preview": preview(response, 200),
    }
    if full:
        view.update(prompt=prompt, response=response)
    return view
