from conftest import PASSWORD, login, make_user, post, register, token


def test_no_default_admin_account(app):
    from conftest import db_query
    assert db_query(app, "SELECT COUNT(*) FROM users")[0][0] == 0


def test_post_without_csrf_token_is_rejected(client):
    assert client.post("/login", data={"username": "a", "password": "b"}).status_code == 400


def test_security_headers(client):
    r = client.get("/login")
    assert "default-src 'self'" in r.headers["Content-Security-Policy"]
    assert "script-src 'self'" in r.headers["Content-Security-Policy"]
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["Cache-Control"] == "no-store"


def test_weak_passwords_rejected(client):
    for pw in ("short1", "password123", "onlylettersonly", "1234567890123"):
        assert register(client, "bob", pw).status_code == 400


def test_username_with_at_sign_rejected(client):
    assert register(client, "bob@example.com").status_code == 400


def test_policy_acceptance_required(client):
    data = {"username": "bob", "password": PASSWORD, "password_confirm": PASSWORD}
    assert post(client, "/register", data).status_code == 400


def test_registration_code_enforced(tmp_path):
    from cryptography.fernet import Fernet
    from lumen import create_app
    app = create_app({"LUMEN_ENV": "testing", "SECRET_KEY": "x", "DATA_ENCRYPTION_KEY": Fernet.generate_key().decode(),
                      "DATABASE_PATH": str(tmp_path / "c.db"), "LUMEN_INSTANCE_DIR": str(tmp_path),
                      "REGISTRATION_CODE": "open-sesame-42"})
    c = app.test_client()
    assert register(c, "bob").status_code == 400
    assert register(c, "bob", registration_code="open-sesame-42").status_code == 302


def test_login_throttling_locks_after_repeated_failures(client):
    register(client)
    for _ in range(5):
        assert login(client, "alice", "wrong-password-1").status_code == 401
    assert login(client, "alice", PASSWORD).status_code == 429


def test_login_error_does_not_reveal_which_part_is_wrong(client):
    register(client)
    a = login(client, "alice", "wrong-password-1").get_data(as_text=True)
    b = login(client, "nobody", "wrong-password-1").get_data(as_text=True)
    assert "Incorrect username or password." in a and "Incorrect username or password." in b


def test_login_attempts_store_no_raw_username_or_ip(app, client):
    from conftest import db_query
    login(client, "secret-user-name", "x")
    rows = db_query(app, "SELECT key_hash FROM login_attempts")
    assert rows and all("secret-user-name" not in r[0] and "127.0.0.1" not in r[0] for r in rows)
    events = db_query(app, "SELECT detail FROM audit_events WHERE action='LOGIN_FAILED'")
    assert events and all("secret-user-name" not in e[0] for e in events)


def test_admin_pages_forbidden_for_regular_users(app):
    c = make_user(app, "alice")
    assert c.get("/admin/").status_code == 403
    assert c.get("/admin/users").status_code == 403


def test_anonymous_redirected_to_login(client):
    r = client.get("/ask")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_session_cookie_flags(client):
    register(client)
    cookie = login(client).headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie


def test_session_fixation_protection(client):
    register(client)
    before = token(client)
    login(client)
    assert token(client) != before


def test_health_endpoint(client):
    assert client.get("/health").get_json()["status"] == "ok"


def test_production_requires_secrets(tmp_path):
    import pytest
    from lumen import create_app
    with pytest.raises(RuntimeError):
        create_app({"LUMEN_ENV": "production", "LUMEN_INSTANCE_DIR": str(tmp_path), "SECRET_KEY": "", "DATABASE_PATH": str(tmp_path / "p.db")})
