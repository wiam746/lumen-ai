import json

from conftest import PASSWORD, db_query, login, make_user, post, register, token

PROMPT = "Explain photosynthesis in simple terms"


def test_ask_stores_encrypted_and_never_plaintext(app):
    c = make_user(app, "alice")
    r = post(c, "/ask", {"prompt": PROMPT})
    assert r.status_code == 200 and "AI-generated" in r.get_data(as_text=True)
    row = db_query(app, "SELECT prompt_enc, response_enc, external_transfer FROM requests")[0]
    assert "photosynthesis" not in row["prompt_enc"] and row["external_transfer"] == 0
    raw = open(app.config["DATABASE_PATH"], "rb").read()
    assert b"photosynthesis" not in raw


def test_blocked_prompt_is_not_stored_nor_processed(app):
    c = make_user(app, "alice")
    r = post(c, "/ask", {"prompt": "My email is jane@example.com"})
    assert r.status_code == 422
    assert db_query(app, "SELECT COUNT(*) FROM requests")[0][0] == 0
    assert db_query(app, "SELECT COUNT(*) FROM audit_events WHERE action='COMPLIANCE_BLOCK'")[0][0] == 1
    assert "jane@example.com" not in str(db_query(app, "SELECT detail FROM audit_events")[0][0])


def test_xss_payload_is_escaped_everywhere(app):
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": "<script>alert(1)</script> explain TCP"})
    page = c.get("/history/1").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in page and "&lt;script&gt;alert(1)&lt;/script&gt;" in page


def test_prompt_length_limit(app):
    c = make_user(app, "alice")
    assert post(c, "/ask", {"prompt": "a" * 2001}).status_code == 400


def test_rate_limit_per_hour(app):
    app.config["ASK_RATE_LIMIT_PER_HOUR"] = 2
    c = make_user(app, "alice")
    for _ in range(2):
        assert post(c, "/ask", {"prompt": "what is gdpr"}).status_code == 200
    assert post(c, "/ask", {"prompt": "what is gdpr"}).status_code == 429


def test_users_cannot_read_each_others_history(app):
    alice, bob = make_user(app, "alice"), make_user(app, "bob")
    post(alice, "/ask", {"prompt": PROMPT})
    r = bob.get("/history/1")
    assert r.status_code == 302 and PROMPT not in r.get_data(as_text=True)
    assert post(bob, "/history/1/delete").status_code == 302
    assert db_query(app, "SELECT COUNT(*) FROM requests")[0][0] == 1


def test_export_contains_full_content(app):
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": PROMPT})
    data = json.loads(c.get("/my-data/export").get_data(as_text=True))
    assert data["requests"][0]["prompt"] == PROMPT and data["account"]["username"] == "alice"
    assert "password_hash" not in json.dumps(data)


def test_delete_history(app):
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": PROMPT})
    post(c, "/my-data/delete-history")
    assert db_query(app, "SELECT COUNT(*) FROM requests")[0][0] == 0


def test_delete_account_erases_everything(app):
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": PROMPT})
    post(c, "/contest", {"kind": "other", "message": "This is a test contest."})
    assert post(c, "/my-data/delete-account", {"password": "wrong-password-1"}).status_code == 302
    assert db_query(app, "SELECT COUNT(*) FROM users")[0][0] == 1
    post(c, "/my-data/delete-account", {"password": PASSWORD})
    for table in ("users", "requests", "contests"):
        assert db_query(app, f"SELECT COUNT(*) FROM {table}")[0][0] == 0
    assert login(app.test_client(), "alice").status_code == 401


def test_last_admin_cannot_delete_account(app):
    c = make_user(app, "root", role="admin")
    post(c, "/my-data/delete-account", {"password": PASSWORD})
    assert db_query(app, "SELECT COUNT(*) FROM users")[0][0] == 1


def test_rectification_and_password_change(app):
    c = make_user(app, "alice")
    post(c, "/settings/username", {"username": "alice2"})
    assert db_query(app, "SELECT username FROM users")[0][0] == "alice2"
    new = "another-strong-pass-7"
    post(c, "/settings/password", {"current_password": PASSWORD, "new_password": new})
    assert login(app.test_client(), "alice2", new).status_code == 302


def test_objection_to_external_processing(app):
    c = make_user(app, "alice")
    post(c, "/settings/ai-processing", {"external_ai_optout": "1"})
    assert db_query(app, "SELECT external_ai_optout FROM users")[0][0] == 1


def test_external_provider_opt_out_prevents_transfer(app, monkeypatch):
    import lumen.ai_service as svc
    app.config.update(LLM_PROVIDER="groq", GROQ_API_KEY="gsk_test")
    called = []
    monkeypatch.setattr(svc, "_chat_completion", lambda *a, **k: called.append(1) or "external answer")
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": PROMPT})
    assert called and db_query(app, "SELECT external_transfer, provider FROM requests")[0][0] == 1
    post(c, "/settings/ai-processing", {"external_ai_optout": "1"})
    called.clear()
    post(c, "/ask", {"prompt": PROMPT})
    assert not called
    assert db_query(app, "SELECT provider FROM requests ORDER BY id DESC")[0][0] == "offline"


def test_provider_failure_falls_back_to_offline(app, monkeypatch):
    import requests, lumen.ai_service as svc
    app.config.update(LLM_PROVIDER="groq", GROQ_API_KEY="gsk_test")
    def boom(*a, **k): raise requests.ConnectionError("down")
    monkeypatch.setattr(svc, "_chat_completion", boom)
    c = make_user(app, "alice")
    r = post(c, "/ask", {"prompt": PROMPT})
    assert r.status_code == 200 and "unavailable" in r.get_data(as_text=True)
    assert db_query(app, "SELECT external_transfer FROM requests")[0][0] == 0


def test_model_output_pii_is_redacted(app, monkeypatch):
    import lumen.ai_service as svc
    app.config.update(LLM_PROVIDER="ollama")
    monkeypatch.setattr(svc, "_chat_completion", lambda *a, **k: "Write to boss@corp.com")
    c = make_user(app, "alice")
    post(c, "/ask", {"prompt": PROMPT})
    assert "boss@corp.com" not in c.get("/history/1").get_data(as_text=True)


def test_human_oversight_and_contestation_end_to_end(app):
    alice, admin = make_user(app, "alice"), make_user(app, "root", role="admin")
    r = post(alice, "/ask", {"prompt": "Explain the rules for processing health data"})
    assert "Queued for human review" in r.get_data(as_text=True)
    assert "alice" in admin.get("/admin/").get_data(as_text=True)
    # a justification is mandatory for a sanction
    assert "Choose a valid action" in post(admin, "/admin/requests/1/review", {"action": "block"}, follow_redirects=True).get_data(as_text=True)
    post(admin, "/admin/requests/1/review", {"action": "block", "note": "Repeated policy violation"})
    assert db_query(app, "SELECT is_blocked FROM users WHERE username='alice'")[0][0] == 1
    # blocked users are cut off immediately but keep their rights
    assert alice.get("/ask").status_code == 302
    assert alice.get("/my-data").status_code == 200
    assert alice.get("/my-data/export").status_code == 200
    post(alice, "/contest", {"kind": "moderation", "request_id": "1", "message": "The topic was legitimate, a GDPR question."})
    assert "legitimate" in admin.get("/admin/").get_data(as_text=True)
    post(admin, "/admin/contests/1/decide", {"decision": "accepted", "note": "Context was legitimate", "unblock": "1"})
    assert db_query(app, "SELECT is_blocked FROM users WHERE username='alice'")[0][0] == 0
    assert db_query(app, "SELECT status FROM contests")[0][0] == "accepted"
    assert alice.get("/ask").status_code == 200


def test_admin_cannot_block_another_admin_or_read_unflagged_content(app):
    a1, a2 = make_user(app, "root", role="admin"), make_user(app, "root2", role="admin")
    post(a2, "/ask", {"prompt": "Explain the rules for processing health data"})
    post(a1, "/admin/requests/1/review", {"action": "block", "note": "trying to block an admin"})
    assert db_query(app, "SELECT is_blocked FROM users WHERE username='root2'")[0][0] == 0
    post(a2, "/ask", {"prompt": PROMPT})
    assert a1.get("/admin/requests/2").status_code == 404  # unflagged content is not readable by reviewers


def test_contest_requires_meaningful_message(app):
    c = make_user(app, "alice")
    post(c, "/contest", {"kind": "other", "message": "no"})
    assert db_query(app, "SELECT COUNT(*) FROM contests")[0][0] == 0


def test_public_pages_render_without_login(client):
    for url in ("/privacy", "/policy", "/transparency", "/login", "/register"):
        assert client.get(url).status_code == 200
    assert "Test Org" in client.get("/privacy").get_data(as_text=True)
