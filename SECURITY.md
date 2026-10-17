# Security policy

## Reporting a vulnerability
Please report vulnerabilities privately through GitHub: **Security > Report a vulnerability** on this repository. Do not open a public issue. Include steps to reproduce and the affected version. You will get an acknowledgement within 5 working days.

## Supported versions
Only the latest release receives security fixes.

## Security model (summary)
- Passwords: scrypt hashes (Werkzeug). Password policy and per-user and per-IP login throttling.
- Prompts and responses are encrypted at rest (Fernet). Keys live in the environment, never in the database.
- CSRF tokens on every state-changing request; strict Content-Security-Policy (no inline scripts or styles); HttpOnly, SameSite cookies.
- Roles and suspension status are read from the database on every request, never trusted from the cookie.
- Audit trail is hash-chained; run `flask verify-audit` regularly.

## Production hardening checklist
- [ ] `LUMEN_ENV=production`, with `SECRET_KEY` and `DATA_ENCRYPTION_KEY` from a secret manager
- [ ] Serve behind HTTPS (reverse proxy) with a real WSGI server (`gunicorn "lumen:create_app()"`), `PROXY_FIX_HOPS` set correctly
- [ ] `REGISTRATION_CODE` set (or registration disabled)
- [ ] Database and `instance/` readable only by the service account; encrypted, access-controlled backups
- [ ] First administrator created with `flask create-admin`
- [ ] Scheduled `flask verify-audit`; log shipping for application logs
- [ ] If using an external AI provider: data processing agreement and legal basis in place (see `docs/fr/transferts-groq.md`)

## Known limitations
No multi-factor authentication and no e-mail-based password reset yet (see roadmap in the README). The personal-data filter is pattern-based and cannot detect free-text names.
