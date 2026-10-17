# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/), versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-10-06

First public release of **Lumen AI**, a ground-up rewrite of an earlier prototype.

### Added
- Application factory architecture (`lumen/` package), English UI and codebase.
- Encryption at rest for prompts and responses (Fernet, key rotation supported).
- Tamper-evident audit trail (SHA-256 hash chain) with `flask verify-audit`.
- Human oversight: review queue, justified decisions, user suspension that stays contestable.
- Contestation procedure for AI answers and moderation decisions.
- Data-subject rights: full export, erasure of history and account, rectification, objection to external AI processing.
- Pluggable providers: offline (default), local Ollama, Groq (external, opt-in) with per-request transfer tracing.
- Automatic retention purge, CSRF protection, strict CSP, login throttling, password policy.
- Risk register, DPIA, governance framework, acceptable-use policy and transfer assessment (`docs/fr/`).
- Test suite (62 tests) and GitHub Actions workflow.

### Security
- No default administrator account: create one with `flask create-admin`.
- Fixed stored-XSS path in the answer renderer; account suspension now takes effect immediately.
- Raw IP addresses and typed usernames are no longer written to logs.
- No third-party requests from the browser (no external fonts or scripts).
