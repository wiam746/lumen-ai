"""Configuration, read from environment variables (a local .env file is supported).

Secrets are never hard-coded. In development, missing keys are generated once and
stored in ``instance/`` (git-ignored, mode 0600). In production they are mandatory.
"""
from __future__ import annotations

import os
import secrets
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_VERSION = "1.0"


def _int(env: dict, name: str, default: int) -> int:
    try:
        return int(env.get(name, default))
    except (TypeError, ValueError):
        return default


def _persisted_key(value: str | None, instance_dir: Path, filename: str, generator, production: bool, label: str) -> str:
    if value:
        return value
    if production:
        raise RuntimeError(f"{label} must be set when LUMEN_ENV=production")
    instance_dir.mkdir(parents=True, exist_ok=True)
    path = instance_dir / filename
    if path.exists():
        return path.read_text().strip()
    key = generator()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(key)
    return key


def load_config(overrides: dict | None = None) -> dict:
    load_dotenv(BASE_DIR / ".env")
    env = {**os.environ, **{k: str(v) for k, v in (overrides or {}).items() if v is not None}}

    lumen_env = env.get("LUMEN_ENV", "development").lower()
    production = lumen_env == "production"
    instance_dir = Path(env.get("LUMEN_INSTANCE_DIR", BASE_DIR / "instance"))

    cfg = {
        "LUMEN_ENV": lumen_env,
        "SECRET_KEY": _persisted_key(env.get("SECRET_KEY"), instance_dir, "secret.key",
                                     lambda: secrets.token_hex(32), production, "SECRET_KEY"),
        "DATA_ENCRYPTION_KEY": _persisted_key(env.get("DATA_ENCRYPTION_KEY"), instance_dir, "data.key",
                                              lambda: Fernet.generate_key().decode(), production,
                                              "DATA_ENCRYPTION_KEY"),
        "DATABASE_PATH": env.get("DATABASE_PATH", str(instance_dir / "lumen.db")),
        # Organization identity (shown in the privacy notice)
        "ORG_NAME": env.get("ORG_NAME", "Your Organization"),
        "DPO_CONTACT": env.get("DPO_CONTACT", "dpo@example.org"),
        # Access control
        "REGISTRATION_ENABLED": env.get("REGISTRATION_ENABLED", "1") not in ("0", "false", "False"),
        "REGISTRATION_CODE": env.get("REGISTRATION_CODE", ""),
        # AI provider: offline (default) | groq | ollama
        "LLM_PROVIDER": env.get("LLM_PROVIDER", "offline").lower(),
        "GROQ_API_KEY": env.get("GROQ_API_KEY", ""),
        "GROQ_MODEL": env.get("GROQ_MODEL", "llama-3.1-8b-instant"),
        "OLLAMA_BASE_URL": env.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "OLLAMA_MODEL": env.get("OLLAMA_MODEL", "llama3.1:8b"),
        "KNOWLEDGE_BASE_PATH": env.get("KNOWLEDGE_BASE_PATH", str(BASE_DIR / "config" / "knowledge_base.md")),
        # Limits
        "MAX_PROMPT_CHARS": _int(env, "MAX_PROMPT_CHARS", 2000),
        "ASK_RATE_LIMIT_PER_HOUR": _int(env, "ASK_RATE_LIMIT_PER_HOUR", 30),
        "LOGIN_MAX_FAILURES": _int(env, "LOGIN_MAX_FAILURES", 5),
        "LOGIN_IP_MAX_FAILURES": _int(env, "LOGIN_IP_MAX_FAILURES", 20),
        "LOGIN_WINDOW_MINUTES": _int(env, "LOGIN_WINDOW_MINUTES", 15),
        # Retention (storage limitation, GDPR Art. 5(1)(e))
        "REQUEST_RETENTION_DAYS": _int(env, "REQUEST_RETENTION_DAYS", 180),
        "AUDIT_RETENTION_DAYS": _int(env, "AUDIT_RETENTION_DAYS", 365),
        "CONTEST_RETENTION_DAYS": _int(env, "CONTEST_RETENTION_DAYS", 365),
        # Sessions & transport
        "PERMANENT_SESSION_LIFETIME": _int(env, "SESSION_LIFETIME_MINUTES", 120) * 60,
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": production,
        "PROXY_FIX_HOPS": _int(env, "PROXY_FIX_HOPS", 0),
        "MAX_CONTENT_LENGTH": 64 * 1024,
        "POLICY_VERSION": POLICY_VERSION,
        "TESTING": lumen_env == "testing",
    }
    Path(cfg["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
    return cfg
