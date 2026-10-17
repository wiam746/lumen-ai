# Architecture

## Components

| Module | Responsibility |
|---|---|
| `lumen/__init__.py` | Application factory, error pages, CLI commands |
| `config.py` | Environment-based settings; generates dev secrets into `instance/`, requires them in production |
| `security.py` | CSRF, per-request user loading, throttling, pseudonymisation, security headers, password policy |
| `compliance.py` | Input filter (block / flag) and output redaction |
| `ai_service.py` | Provider abstraction: offline, Ollama (local), Groq (external) |
| `crypto.py` | Fernet encryption at rest, key rotation |
| `audit.py` | Hash-chained audit events and verification |
| `retention.py` | Automatic purge of expired data |
| `auth.py`, `chat.py`, `privacy.py`, `admin.py`, `pages.py` | Blueprints |

## Data model

`users` (pseudonymous account, role, suspension, objection flag, consent version) → `requests` (encrypted prompt and response, provider, `external_transfer`, flag, review status) · `warnings` · `contests` · `login_attempts` (HMAC keys only) · `audit_events` (hash chain) · `meta`.

Deleting a user cascades to their requests, warnings and contests. Audit events keep only a numeric, pseudonymous actor ID.

## Security controls

| Threat | Control | Where |
|---|---|---|
| Stored XSS via model output | Jinja autoescape, escape-before-format renderer, strict CSP | `templates/`, `static/js/app.js`, `security.py` |
| CSRF | Per-session token on all state-changing requests | `security.py` |
| Brute force | Throttling per username and per IP (HMAC keys), scrypt | `security.py`, `auth.py` |
| Stale privileges | Role and suspension read from DB each request | `security.py` |
| Data theft at rest | Fernet encryption, DB mode 0600, keys outside the DB | `crypto.py`, `db.py` |
| Log leakage | No prompts, usernames or raw IPs in logs | `audit.py`, `auth.py` |
| Log tampering | SHA-256 hash chain, `verify-audit` | `audit.py` |
| Reviewer over-reach | Reviewers open flagged content only; each access audited | `admin.py` |

## Extending

- **New provider:** add a branch in `ai_service.generate_response` and an entry in `PROVIDER_META`; mark `external=True` if data leaves your infrastructure.
- **New filter rule:** add a detector to `compliance.BLOCKED_DETECTORS` or a term group to `SENSITIVE_TERMS`, with a test.
- **New data field:** update `schema.sql`, the export in `privacy._collect`, the privacy notice and the DPIA.
