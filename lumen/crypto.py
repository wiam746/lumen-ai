"""Encryption at rest for prompts and responses (Fernet: AES-128-CBC + HMAC-SHA256).

DATA_ENCRYPTION_KEY may hold several comma-separated keys (newest first) to allow
key rotation: new data is written with the first key, old data stays readable.
"""
from __future__ import annotations

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from flask import Flask, current_app

UNREADABLE = "[unreadable: encryption key mismatch]"


def init_app(app: Flask) -> None:
    keys = [k.strip() for k in app.config["DATA_ENCRYPTION_KEY"].split(",") if k.strip()]
    app.extensions["lumen_fernet"] = MultiFernet([Fernet(k) for k in keys])


def encrypt(text: str) -> str:
    return current_app.extensions["lumen_fernet"].encrypt(text.encode("utf-8")).decode("ascii")


def decrypt(token: str) -> str:
    try:
        return current_app.extensions["lumen_fernet"].decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken:
        return UNREADABLE
